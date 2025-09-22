"""
Shell智能体主类 - 整合所有功能模块
"""
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

from .param_model import SaveCommandHistoryParams
from .shell_generator import ShellCommandGenerator
from .shell_executor import ShellExecutor
from .error_analyzer import ErrorAnalyzer
from .rag_search import RAGSearch

class ShellAgent:
    """Shell智能体主类，整合所有功能模块"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", rag_persist_directory: str = "./chroma_db"):
        """初始化Shell智能体
        
        Args:
            model_name: 使用的OpenAI模型名称
            rag_persist_directory: RAG向量数据库持久化目录
        """
        self.shell_generator = ShellCommandGenerator(model_name=model_name)
        self.shell_executor = ShellExecutor()
        self.error_analyzer = ErrorAnalyzer(model_name=model_name)
        self.rag_search = RAGSearch(persist_directory=rag_persist_directory)
        
        # 初始化LLM
        self.llm = ChatOpenAI(model_name=model_name, temperature=0)
        
        # 定义工具
        self.tools = self._create_tools()
        
        # 创建agent
        self.agent_executor = self._create_agent_executor()
        
        # 命令历史记录
        self.command_history = []
    
    def _create_tools(self) -> List[Tool]:
        """创建工具列表"""
        return [
            Tool(
                name="search_similar_commands",
                func=self._search_similar_commands_wrapper,
                description="搜索相似的历史shell命令和结果，输入应该是包含用户需求描述的字典"
            ),
            Tool(
                name="generate_shell_command",
                func=self._generate_shell_command_wrapper,
                description="根据用户需求生成合适的shell命令，输入应该是包含用户需求描述的字典"
            ),
            Tool(
                name="execute_shell_command",
                func=self._execute_shell_command_wrapper,
                description="执行shell命令并返回结果，输入应该是包含要执行的shell命令的字典"
            ),
            Tool(
                name="analyze_command_error",
                func=self._analyze_command_error_wrapper,
                description="分析shell命令执行错误并提供解决方案，输入应该是包含用户需求、命令和错误信息的字典"
            ),
            # 将普通Tool改为StructuredTool
            StructuredTool.from_function(
                func=self._save_command_history_wrapper,
                name="save_command_history",
                description="将命令执行历史保存到数据库中",
                args_schema= SaveCommandHistoryParams
            )
        ]
    
    def _create_agent_executor(self) -> AgentExecutor:
        """创建agent执行器"""
        # 系统提示词
        system_prompt = """你是一个专业的Shell命令助手。请根据用户需求选择合适的工具来：
        1. 已经为你搜索了相似的历史命令（见similar_commands_context）
        2. 生成合适的shell命令 （必须执行）
        3. 执行生成的shell命令（必须执行）
        4. 分析错误（如果执行失败）
        5. 保存执行历史（如果执行成功）

        重要：对于用户要求执行shell命令的需求，你必须执行生成的命令，而不仅仅是生成命令。
        执行命令是完成用户请求的关键步骤，不能省略。
        执行命令后，必须分析执行结果并根据需要执行分析错误工具。
        如果命令执行成功，必须保存执行历史，不能省略。
        如果命令执行失败，必须分析错误并提供解决方案，不能省略。

        特别重要：当使用save_command_history工具保存执行历史时，请直接传递以下四个参数：
        - user_requirement: 用户的原始请求
        - command: 实际执行的shell命令
        - result: 命令执行的完整输出内容
        - success: 布尔值，表示命令是否执行成功

        请参考提供的相似历史命令（如果有）来生成更合适的命令。
        请按合理的顺序使用工具，确保最终为用户提供完整的解决方案，包括命令执行结果。"""

        # 创建提示词模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("human", "相似历史命令（如果有）: {similar_commands_context}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # 创建agent
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        
        # 创建执行器
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,  # 处理解析错误
            return_intermediate_steps=True  # 返回中间步骤，便于调试
        )
    
    def _search_similar_commands_wrapper(self, params: Dict[str, Any]) -> str:
        """搜索相似命令的包装函数"""
        # 从字典参数中提取用户输入
        user_input = params.get("user_input", "") if isinstance(params, dict) else str(params)
        similar_commands = self.rag_search.get_similar_commands(user_input)
        if similar_commands:
            result = "找到相似的历史命令:\n"
            for i, cmd in enumerate(similar_commands, 1):
                result += f"{i}. 用户请求: {cmd['user_input']}\n"
                result += f"   执行命令: {cmd['command']}\n"
                result += f"   执行结果: {'成功' if cmd['success'] else '失败'}\n"
                result += f"   相似度: {cmd['similarity_score']:.3f}\n\n"
            return result
        else:
            return "未找到相似的历史命令"

    def _generate_shell_command_wrapper(self, params: Dict[str, Any]) -> str:
        """生成shell命令的包装函数"""
        # 从字典参数中提取用户输入
        user_input = params.get("user_input", "") if isinstance(params, dict) else str(params)
        command = self.shell_generator.generate_command(user_input)
        return f"生成的shell命令: {command}"

    def _execute_shell_command_wrapper(self, params: Dict[str, Any]) -> str:
        """执行shell命令的包装函数"""
        # 从字典参数中提取命令
        command = params.get("command", "") if isinstance(params, dict) else str(params)
        success, output = self.shell_executor.execute_command(command)

        # 保存命令执行结果到实例变量，供后续使用
        self.last_command_execution = {
            "command": command,
            "success": success,
            "output": output
        }

        # 保持原有的字符串返回格式，同时在实例变量中保存结构化数据
        if success:
            return f"命令执行成功! 输出:\n{output}\n\n(结构化数据已保存，可直接用于save_command_history工具)"
        else:
            return f"命令执行失败! 错误信息:\n{output}\n\n(结构化数据已保存，可直接用于analyze_command_error工具)"

    def _analyze_command_error_wrapper(self, params: Dict[str, Any]) -> str:
        """分析命令错误的包装函数"""
        try:
            # 从字典参数中提取信息
            if isinstance(params, dict):
                user_input = params.get("user_requirement", "")
                command = params.get("command", "")
                error_message = params.get("error", "")
            else:
                # 处理字符串输入（降级处理）
                user_input = str(params)
                command = ""
                error_message = str(params)
                
                # 尝试从字符串中提取结构化信息
                if "用户请求:" in user_input and "命令:" in user_input and "错误:" in user_input:
                    lines = user_input.split(',')
                    for line in lines:
                        if line.startswith("用户请求:"):
                            user_input = line.replace("用户请求:", "").strip()
                        elif line.startswith("命令:"):
                            command = line.replace("命令:", "").strip()
                        elif line.startswith("错误:"):
                            error_message = line.replace("错误:", "").strip()
            
            analysis = self.error_analyzer.analyze_error(user_input, command, error_message)
            return f"错误分析结果:\n{analysis}"
        except Exception as e:
            return f"分析错误时出现问题: {str(e)}"

    def _save_command_history_wrapper(self, user_requirement: str, command: str, result: str, success: bool) -> str:
        """保存命令历史的包装函数"""
        try:
            # 直接使用传入的参数，不需要再从字典中提取
            self.rag_search.add_shell_command_history(user_requirement, command, result, success)
            return "命令历史已成功保存到数据库"
        except Exception as e:
            return f"保存命令历史时出现问题: {str(e)}"
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """处理用户输入并生成响应
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            Dict[str, Any]: 包含命令、输出等信息的响应字典
        """
        try:
            # 前置搜索相似命令
            similar_commands = self.rag_search.get_similar_commands(user_input)
            print(f"搜索到 {len(similar_commands)} 条相似命令")
            
            # 构建包含相似命令信息的增强输入
            similar_commands_context = "\n".join([
                f"- 用户请求: {cmd['user_input']}\n  执行命令: {cmd['command']}\n  执行结果: {'成功' if cmd['success'] else '失败'}\n  相似度分数: {cmd['similarity_score']}"
                for cmd in similar_commands
            ]) if similar_commands else "无"
            
            enriched_input = {
                "input": user_input,
                "similar_commands_context": similar_commands_context
            }
            
            # 使用agent执行器处理增强后的输入
            result = self.agent_executor.invoke(enriched_input)
            
            # 确保结果中包含相似命令信息
            if "similar_commands" not in result:
                result["similar_commands"] = similar_commands
            
            # 解析agent的输出，提取命令信息
            if "output" in result:
                command_info = self._parse_agent_output(result["output"], user_input)
                result.update(command_info)
            
            return result
        except Exception as e:
            print(f"Agent执行出错: {str(e)}")
            # 降级处理
            return self._fallback_process(user_input)
    
    def _parse_agent_output(self, output: str, user_input: str) -> Dict[str, Any]:
        """解析agent输出并构建结构化响应"""
        # 无论agent是否执行了搜索，我们都主动搜索相似命令
        similar_commands = self.rag_search.get_similar_commands(user_input)
        
        # 尝试从输出中提取命令信息
        command = ""
        success = True
        result_output = output
        error_analysis = None
        
        # 简单解析常见的输出模式
        if "生成的shell命令: " in output:
            lines = output.split('\n')
            for line in lines:
                if line.startswith("生成的shell命令: "):
                    command = line.replace("生成的shell命令: ", "")
                elif line.startswith("命令执行成功!"):
                    success = True
                elif line.startswith("命令执行失败!"):
                    success = False
                elif line.startswith("错误分析结果:"):
                    error_analysis = line.replace("错误分析结果:", "")
        
        # 保存到命令历史
        history_entry = {
            "user_input": user_input,
            "command": command,
            "success": success,
            "output": result_output,
            "error_analysis": error_analysis
        }
        self.command_history.append(history_entry)
        
        # 如果有成功执行的命令，保存到RAG数据库
        if command and success:
            self.rag_search.add_shell_command_history(user_input, command, result_output, success)
        
        return {
            "user_input": user_input,
            "command": command,
            "success": success,
            "output": result_output,
            "error_analysis": error_analysis,
            "similar_commands": similar_commands
        }
    
    def _fallback_process(self, user_input: str) -> Dict[str, Any]:
        """降级处理：使用原来的硬编码逻辑"""
        # 1. 查找相似的历史命令
        similar_commands = self.rag_search.get_similar_commands(user_input)
        
        # 2. 生成shell命令
        command = self.shell_generator.generate_command(user_input)
        
        # 3. 执行shell命令
        success, output = self.shell_executor.execute_command(command)
        
        # 4. 如果执行失败，分析错误并提供解决方案
        error_analysis = None
        if not success:
            error_analysis = self.error_analyzer.analyze_error(user_input, command, output)
        
        # 5. 将命令和结果添加到RAG数据库
        self.rag_search.add_shell_command_history(user_input, command, output, success)
        
        # 6. 添加到命令历史
        history_entry = {
            "user_input": user_input,
            "command": command,
            "success": success,
            "output": output,
            "error_analysis": error_analysis
        }
        self.command_history.append(history_entry)
        
        # 7. 返回结果
        return {
            "user_input": user_input,
            "command": command,
            "success": success,
            "output": output,
            "error_analysis": error_analysis,
            "similar_commands": similar_commands
        }
    
    def get_command_history(self) -> List[Dict[str, Any]]:
        """获取命令历史记录
        
        Returns:
            List[Dict[str, Any]]: 命令历史记录列表
        """
        return self.command_history