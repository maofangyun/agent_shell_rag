"""
集成测试脚本，验证完整的Shell Agent功能，特别是搜索相似命令的功能
"""
import os
import sys
from shell_agent.agent import ShellAgent

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 初始化ShellAgent
try:
    print("初始化ShellAgent...")
    agent = ShellAgent()
    print("ShellAgent初始化成功")
except Exception as e:
    print(f"初始化ShellAgent时出错: {str(e)}")
    sys.exit(1)

# 添加一些测试命令历史到数据库
print("\n添加一些测试命令历史到数据库...")
test_commands = [
    {
        "user_input": "查看当前目录下的文件",
        "command": "dir",
        "result": "test_integration.py, test_rag.py, test_rag_fixed.py",
        "success": True
    },
    {
        "user_input": "创建一个新文件",
        "command": "echo \"Hello Trae AI\" > trae_test.txt",
        "result": "文件创建成功",
        "success": True
    },
    {
        "user_input": "查看系统信息",
        "command": "systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\"",
        "result": "OS Name: Microsoft Windows 11\nOS Version: 10.0.22621 N/A Build 22621",
        "success": True
    }
]

# 手动添加测试命令历史到RAG数据库
for cmd in test_commands:
    try:
        agent.rag_search.add_shell_command_history(
            user_input=cmd["user_input"],
            command=cmd["command"],
            result=cmd["result"],
            success=cmd["success"]
        )
        print(f"已添加命令历史: {cmd['user_input']}")
    except Exception as e:
        print(f"添加命令历史时出错: {str(e)}")

# 测试搜索相似命令的功能
test_queries = [
    "查看当前目录",
    "创建文件",
    "系统信息"
]

print("\n开始测试搜索相似命令功能:")
for query in test_queries:
    print(f"\n测试查询: '{query}'")
    try:
        # 直接测试get_similar_commands方法
        similar_commands = agent.rag_search.get_similar_commands(query)
        print(f"直接调用get_similar_commands返回的结果数量: {len(similar_commands)}")
        
        # 打印相似命令详情
        for i, cmd in enumerate(similar_commands):
            print(f"相似命令 {i+1}:")
            print(f"  用户输入: {cmd['user_input']}")
            print(f"  命令: {cmd['command']}")
            print(f"  成功: {cmd['success']}")
            print(f"  相似度分数: {cmd['similarity_score']}")
        
        # 测试完整的process_input流程
        print(f"\n测试完整的process_input流程...")
        result = agent.process_input(query)
        print(f"process_input返回的相似命令数量: {len(result.get('similar_commands', []))}")
        
        # 打印完整结果中的相似命令
        if 'similar_commands' in result:
            for i, cmd in enumerate(result['similar_commands']):
                print(f"结果中的相似命令 {i+1}:")
                print(f"  用户输入: {cmd.get('user_input', '')}")
                print(f"  命令: {cmd.get('command', '')}")
                print(f"  成功: {cmd.get('success', False)}")
                
    except Exception as e:
        print(f"测试查询 '{query}' 时出错: {str(e)}")

print("\n集成测试完成")