"""
RAG搜索增强模块 - 提供相关知识支持
"""
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class RAGSearch:
    """RAG搜索增强类，用于提供相关知识支持"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """初始化RAG搜索
        
        Args:
            persist_directory: 向量数据库持久化目录
        """
        self.embeddings = OpenAIEmbeddings()
        self.persist_directory = persist_directory
        
        # 创建持久化目录（如果不存在）
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # 初始化向量数据库
        try:
            self.vectordb = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print(f"已加载现有向量数据库，包含 {self.vectordb._collection.count()} 条记录")
        except Exception as e:
            print(f"创建新的向量数据库: {str(e)}")
            self.vectordb = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        """添加文档到向量数据库
        
        Args:
            documents: 文档内容列表
            metadatas: 文档元数据列表
        """
        # 文本分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        # 创建带metadata的Document对象
        doc_objects = []
        for i, doc in enumerate(documents):
            # 确保即使metadatas为None或长度不足时也能安全访问
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            doc_objects.append(Document(page_content=doc, metadata=metadata))

        # 分割文档
        chunks = text_splitter.split_documents(doc_objects)
        
        # 添加到向量数据库
        self.vectordb.add_documents(chunks)
        print(f"已添加 {len(chunks)} 个文档块到向量数据库")
    
    def add_shell_command_history(self, user_input: str, command: str, result: str, success: bool):
        """添加Shell命令历史到向量数据库
        
        Args:
            user_input: 用户输入
            command: 执行的命令
            result: 命令执行结果
            success: 命令是否成功执行
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
        
        self.add_documents([document], [metadata])
    
    def get_similar_commands(self, user_input: str, k: int = 3) -> List[Dict[str, Any]]:
        """获取与用户输入相似的历史命令
        
        Args:
            user_input: 用户输入
            k: 返回的结果数量
            
        Returns:
            List[Dict[str, Any]]: 相似命令列表
        """
        results = self.vectordb.similarity_search_with_score(user_input, k=k)
        
        similar_commands = []
        for doc, score in results:
            if "type" in doc.metadata and doc.metadata["type"] == "shell_history":
                similar_commands.append({
                    "user_input": doc.metadata.get("user_input", ""),
                    "command": doc.metadata.get("command", ""),
                    "success": doc.metadata.get("success", False),
                    "content": doc.page_content,
                    "similarity_score": score
                })
        
        return similar_commands