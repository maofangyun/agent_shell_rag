"""
Shell智能体主类 - 整合所有功能模块
"""
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
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
            Tool(
                name="save_command_history",
                func=self._save_command_history_wrapper,
                description="将命令执行历史保存到数据库中，输入应该是包含用户需求、命令、结果和成功状态的字典"
            )
        ]
    
    def _create_agent_executor(self) -> AgentExecutor:
        """创建agent执行器"""
        # 系统提示词
        system_prompt = """你是一个专业的Shell命令助手。请根据用户需求选择合适的工具来：
        1. 搜索相似的历史命令（可选）
        2. 生成合适的shell命令
        3. 执行生成的shell命令（必须执行）
        4. 分析错误（如果执行失败）
        5. 保存执行历史
        
        重要：对于用户要求执行shell命令的需求，你必须执行生成的命令，而不仅仅是生成命令。
        执行命令是完成用户请求的关键步骤，不能省略。
        
        请按合理的顺序使用工具，确保最终为用户提供完整的解决方案，包括命令执行结果。"""
        
        # 创建提示词模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # 创建agent
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        
        # 创建执行器
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
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
        if success:
            return f"命令执行成功! 输出:\n{output}"
        else:
            return f"命令执行失败! 错误信息:\n{output}"

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
                    lines = user_input.split('\n')
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

    def _save_command_history_wrapper(self, params: Dict[str, Any]) -> str:
        """保存命令历史的包装函数"""
        try:
            # 从字典参数中提取信息
            if isinstance(params, dict):
                user_input = params.get("user_requirement", "")
                command = params.get("command", "")
                result = params.get("result", "")
                success = params.get("success", False)
            else:
                # 处理字符串输入（降级处理）
                user_input = str(params)
                command = ""
                result = ""
                success = False
                
                # 尝试从字符串中提取结构化信息
                if "用户请求:" in user_input and "命令:" in user_input:
                    lines = user_input.split('\n')
                    for line in lines:
                        if line.startswith("用户请求:"):
                            user_input = line.replace("用户请求:", "").strip()
                        elif line.startswith("命令:"):
                            command = line.replace("命令:", "").strip()
                        elif line.startswith("结果:"):
                            result = line.replace("结果:", "").strip()
                        elif line.startswith("成功:"):
                            success_str = line.replace("成功:", "").strip().lower()
                            success = success_str in ["true", "yes", "1", "成功"]
            
            self.rag_search.add_shell_command_history(user_input, command, result, success)
            return "命令历史已成功保存到数据库"
        except Exception as e:
            return f"保存命令历史时出现问题: {str(e)}"
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """处理用户输入
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            # 使用agent执行器处理输入
            result = self.agent_executor.invoke({"input": user_input})
            
            # 提取工具执行结果
            output = result.get("output", "")
            
            # 解析结果并构建响应
            return self._parse_agent_output(output, user_input)
            
        except Exception as e:
            print(f"Agent执行出错: {str(e)}")
            # 降级处理：使用原来的硬编码逻辑
            return self._fallback_process(user_input)
    
    def _parse_agent_output(self, output: str, user_input: str) -> Dict[str, Any]:
        """解析agent输出并构建结构化响应"""
        # 这里需要根据实际的agent输出格式进行解析
        # 暂时返回一个基本结构
        return {
            "user_input": user_input,
            "command": "",
            "success": True,
            "output": output,
            "error_analysis": None,
            "similar_commands": []
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