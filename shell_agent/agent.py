"""
Shell智能体主类 - 整合所有功能模块
"""
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool, Tool
from langchain_openai import ChatOpenAI

from .param_model import SaveCommandHistoryParams
from .shell_executor import ShellExecutor
from .error_analyzer import ErrorAnalyzer
from .rag_search import RAGSearch

class ShellAgent:
    """Shell智能体主类，整合所有功能模块"""

    def __init__(self, model_name: str = "gpt-3.5-turbo", rag_persist_directory: str = "./chroma_db"):
        """初始化Shell智能体"""
        self.shell_executor = ShellExecutor()
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.error_analyzer = ErrorAnalyzer(llm=self.llm)
        self.rag_search = RAGSearch(persist_directory=rag_persist_directory)
        
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent_executor()

    def _create_tools(self) -> List[Any]:
        """创建工具列表"""
        return [
            Tool(
                name="search_similar_commands",
                func=self.rag_search.get_similar_commands,
                description="搜索与用户输入相似的历史命令，输入为用户需求字符串。"
            ),
            Tool(
                name="execute_shell_command",
                func=self.shell_executor.execute_command,
                description="执行shell命令并返回一个元组(success: bool, output: str)。"
            ),
            Tool(
                name="analyze_command_error",
                func=self.error_analyzer.analyze_error,
                description="分析shell命令执行错误并提供解决方案。需要'user_input', 'command', 'error_message'作为参数。"
            ),
            StructuredTool.from_function(
                func=self.rag_search.add_shell_command_history,
                name="save_command_history",
                description="将命令执行历史保存到数据库中。",
                args_schema=SaveCommandHistoryParams
            )
        ]

    def _create_agent_executor(self) -> AgentExecutor:
        """创建agent执行器"""
        system_prompt = """你是一个专业的Shell命令助手。你的任务是根据用户的需求，生成一个合适的shell命令，然后使用 `execute_shell_command` 工具来执行它。

        **工作流程**:
        1.  **思考并生成**一个shell命令。
        2.  **必须调用** `execute_shell_command` 工具，并将你生成的命令作为参数传入。
        3.  **分析执行结果**：
            - 如果执行**成功** (success=True)，调用 `save_command_history` 工具保存历史。
            - 如果执行**失败** (success=False)，调用 `analyze_command_error` 工具分析错误。

        - **不要**只生成命令而不执行。
        - 你可以调用 `search_similar_commands` 来获取灵感。
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入，通过Agent协调工具执行，并返回结构化结果。
        """
        try:
            # Agent执行核心任务
            result = self.agent_executor.invoke({"input": user_input})
            
            # 补充相似命令的搜索结果（用于前端展示）
            similar_commands = self.rag_search.get_similar_commands(user_input)
            result["similar_commands"] = similar_commands

            # 从中间步骤中提取关键信息，以确保返回结果的结构一致性
            command = ""
            success = False
            output = result.get("output", "")

            for step in result.get("intermediate_steps", []):
                tool_name = step[0].tool
                tool_input = step[0].tool_input
                tool_output = step[1]

                if tool_name == "execute_shell_command":
                    # tool_input is the command
                    if isinstance(tool_input, str):
                        command = tool_input
                    elif isinstance(tool_input, dict) and 'command' in tool_input:
                        command = tool_input['command']
                    
                    # tool_output is a tuple (success, output_str)
                    if isinstance(tool_output, tuple) and len(tool_output) == 2:
                        success, output = tool_output

            # 将提取的信息统一添加到结果字典中
            result["command"] = command
            result["success"] = success
            # 'output' is already in the result, but we ensure it has the execution output
            result["output"] = output

            return result
        except Exception as e:
            print(f"Agent执行出错: {str(e)}")
            # 简化降级处理
            return {
                "input": user_input,
                "output": f"处理时发生错误: {e}",
                "intermediate_steps": [],
                "similar_commands": self.rag_search.get_similar_commands(user_input),
                "error": str(e)
            }
    