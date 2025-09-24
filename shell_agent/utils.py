"""
工具类模块 - 提供通用功能支持
"""
import os
import platform
from typing import Dict, Any, Optional
from langchain_core.documents import Document

class PlatformUtils:
    """平台相关工具类"""

    @staticmethod
    def get_shell_command() -> list:
        """获取当前平台的shell命令"""
        if platform.system() == "Windows":
            return ["powershell", "-Command"]
        else:
            return ["cmd", "/c"]

    @staticmethod
    def is_windows() -> bool:
        """判断是否为Windows平台"""
        return platform.system() == "Windows"

class DocumentUtils:
    """文档处理工具类"""

    @staticmethod
    def create_documents(documents: list, metadatas: Optional[list] = None) -> list[Document]:
        """创建带metadata的Document对象列表

        Args:
            documents: 文档内容列表
            metadatas: 文档元数据列表

        Returns:
            List[Document]: Document对象列表
        """
        doc_objects = []
        for i, doc in enumerate(documents):
            # 安全地获取metadata
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            doc_objects.append(Document(page_content=doc, metadata=metadata))
        return doc_objects

    @staticmethod
    def create_shell_history_document(user_input: str, command: str, result: str, success: bool) -> tuple[str, Dict[str, Any]]:
        """创建shell历史文档内容和元数据

        Args:
            user_input: 用户输入
            command: 执行的命令
            result: 命令执行结果
            success: 命令是否成功执行

        Returns:
            tuple[str, Dict[str, Any]]: (文档内容, 元数据)
        """
        document = f"""
用户请求: {user_input}
执行命令: {command}
执行结果: {'成功' if success else '失败'}
输出内容: {result}
"""
        metadata = {
            "type": "shell_history",
            "user_input": user_input,
            "command": command,
            "success": success
        }
        return document, metadata

class EnvUtils:
    """环境变量工具类"""

    @staticmethod
    def check_openai_api_key() -> tuple[bool, Optional[str]]:
        """检查OpenAI API密钥

        Returns:
            tuple[bool, Optional[str]]: (是否设置, 错误信息)
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return False, "错误: 未设置OPENAI_API_KEY环境变量\n请创建.env文件并添加您的OpenAI API密钥:\nOPENAI_API_KEY=your_api_key_here"
        return True, None