"""
Shell智能体主类 - 整合所有功能模块
"""
from typing import Dict, Any, List, Optional
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
        
        # 命令历史记录
        self.command_history = []
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """处理用户输入
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            Dict[str, Any]: 处理结果
        """
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