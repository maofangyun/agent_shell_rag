"""
错误分析模块 - 负责分析命令执行错误并提供解决方案
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class ErrorAnalyzer:
    """分析命令执行错误并提供解决方案的类"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """初始化错误分析器
        
        Args:
            model_name: 使用的OpenAI模型名称
        """
        self.llm = ChatOpenAI(model_name=model_name)
        self.prompt = ChatPromptTemplate.from_template(
            """你是一个专业的Shell错误分析专家。
            分析以下命令执行错误，并提供详细的解决方案。
            
            用户请求: {user_input}
            执行的命令: {command}
            错误信息: {error_message}
            
            请提供:
            1. 错误原因分析
            2. 解决方案
            3. 修正后的命令（如果适用）
            """
        )
        self.output_parser = StrOutputParser()
        self.chain = self.prompt | self.llm | self.output_parser
    
    def analyze_error(self, user_input: str, command: str, error_message: str) -> str:
        """分析错误并提供解决方案
        
        Args:
            user_input: 用户的原始输入
            command: 执行的命令
            error_message: 错误信息
            
        Returns:
            str: 错误分析和解决方案
        """
        try:
            analysis = self.chain.invoke({
                "user_input": user_input,
                "command": command,
                "error_message": error_message
            })
            return analysis
        except Exception as e:
            return f"分析错误时出现问题: {str(e)}"