"""
Shell命令生成模块 - 负责将用户输入转换为shell命令
"""
from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ShellCommandGenerator:
    """根据用户输入生成shell命令的类"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """初始化Shell命令生成器
        
        Args:
            model_name: 使用的OpenAI模型名称
        """
        self.llm = ChatOpenAI(model_name=model_name)
        self.prompt = ChatPromptTemplate.from_template(
            """你是一个专业的Shell命令生成助手。
            根据用户的需求，生成适当的Shell命令。
            只返回命令本身，不要包含任何解释或其他文本。
            确保命令在Windows PowerShell环境中可以正常运行。
            
            用户需求: {user_input}
            """
        )
        self.output_parser = StrOutputParser()
        self.chain = self.prompt | self.llm | self.output_parser
    
    def generate_command(self, user_input: str) -> str:
        """根据用户输入生成shell命令
        
        Args:
            user_input: 用户的输入文本
            
        Returns:
            生成的shell命令
        """
        try:
            command = self.chain.invoke({"user_input": user_input})
            return command.strip()
        except Exception as e:
            print(f"生成命令时出错: {str(e)}")
            return ""