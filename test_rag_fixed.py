"""
测试修复后的RAG搜索功能，使用新的数据库路径
"""
import os
import shutil
from shell_agent.rag_search import RAGSearch

# 使用临时数据库路径以避免影响现有数据
temp_db_path = os.path.join(os.getcwd(), "temp_chroma_db")
print(f"使用临时数据库路径: {temp_db_path}")

# 确保临时目录不存在
try:
    if os.path.exists(temp_db_path):
        shutil.rmtree(temp_db_path)
    print(f"已清除临时数据库目录")
except Exception as e:
    print(f"清除临时目录时出错: {str(e)}")

# 初始化RAGSearch实例
rag = RAGSearch(persist_directory=temp_db_path)

# 打印数据库中的初始文档数量
try:
    doc_count = rag.vectordb._collection.count()
    print(f"初始数据库中的文档总数: {doc_count}")

except Exception as e:
    print(f"获取文档数量时出错: {str(e)}")

# 添加测试命令历史
print("添加测试命令历史...")

# 添加测试命令历史
test_commands = [
    {
        "user_input": "查看当前目录下的文件",
        "command": "dir",
        "result": "file1.txt, file2.py, README.md",
        "success": True
    },
    {
        "user_input": "创建一个新文件",
        "command": "echo \"Hello World\" > test.txt",
        "result": "文件创建成功",
        "success": True
    },
    {
        "user_input": "查看系统信息",
        "command": "systeminfo",
        "result": "操作系统名称: Microsoft Windows 11...",
        "success": True
    }
]

for cmd in test_commands:
    rag.add_shell_command_history(
        user_input=cmd["user_input"],
        command=cmd["command"],
        result=cmd["result"],
        success=cmd["success"]
    )

# 验证添加成功
try:
    new_count = rag.vectordb._collection.count()
    print(f"添加后文档总数: {new_count}")

except Exception as e:
    print(f"获取文档数量时出错: {str(e)}")

# 直接检查向量数据库中的内容
print("\n直接检查向量数据库中的所有文档:")
try:
    # 获取所有文档（在实际应用中不建议对大型数据库这样做）
    all_docs = rag.vectordb.get()
    print(f"数据库中共有 {len(all_docs['ids'])} 个文档")
    
    # 打印每个文档的内容和metadata
    for i in range(len(all_docs['ids'])):
        print(f"\n文档 {i+1}:")
        print(f"ID: {all_docs['ids'][i]}")
        print(f"内容: {all_docs['documents'][i][:100]}...")
        print(f"Metadata: {all_docs['metadatas'][i]}")
except Exception as e:
    print(f"获取所有文档时出错: {str(e)}")

# 测试get_similar_commands方法
test_queries = [
    "查看当前目录",
    "创建文件",
    "系统信息"
]

for query in test_queries:
    print(f"\n搜索查询: '{query}'")
    try:
        # 直接使用向量数据库的查询方法查看原始结果
        raw_results = rag.vectordb.similarity_search_with_score(query, k=5)
        print(f"原始搜索结果数量: {len(raw_results)}")
        
        # 打印原始结果的metadata
        for i, (doc, score) in enumerate(raw_results):
            print(f"原始结果 {i+1} (分数: {score}):")
            print(f"  内容预览: {doc.page_content[:50]}...")
            print(f"  Metadata: {doc.metadata}")
        
        # 调用get_similar_commands方法
        similar_commands = rag.get_similar_commands(query, k=3)
        print(f"过滤后的相似命令数量: {len(similar_commands)}")
        
        # 打印过滤后的结果
        for i, cmd in enumerate(similar_commands):
            print(f"相似命令 {i+1}:")
            print(f"  用户输入: {cmd['user_input']}")
            print(f"  命令: {cmd['command']}")
            print(f"  成功: {cmd['success']}")
            print(f"  相似度分数: {cmd['similarity_score']}")
    except Exception as e:
        print(f"搜索时出错: {str(e)}")

print("\n测试完成")