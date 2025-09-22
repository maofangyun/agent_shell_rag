"""
测试搜索相似历史命令功能的脚本
"""
import os
from dotenv import load_dotenv
from shell_agent.agent import ShellAgent

# 加载环境变量
load_dotenv()

def test_search_similar_commands():
    """测试搜索相似历史命令功能"""
    print("===== 测试搜索相似历史命令功能 =====")
    
    # 检查OpenAI API密钥
    if not os.environ.get("OPENAI_API_KEY"):
        print("错误: 未设置OPENAI_API_KEY环境变量")
        print("请创建.env文件并添加您的OpenAI API密钥:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    # 初始化Shell智能体
    print("初始化Shell智能体...")
    agent = ShellAgent()
    print("Shell智能体初始化完成!")
    
    # 准备测试用例
    test_queries = [
        "查看当前目录下的文件",
        "创建一个新文件",
        "查看系统信息"
    ]
    
    # 执行测试
    for query in test_queries:
        print(f"\n\n测试查询: {query}")
        result = agent.process_input(query)
        
        # 显示结果
        print(f"生成的命令: {result['command']}")
        print(f"执行成功: {result['success']}")
        print(f"相似命令数量: {len(result['similar_commands'])}")
        
        if result['similar_commands']:
            print("找到的相似命令:")
            for i, cmd in enumerate(result['similar_commands'], 1):
                print(f"  {i}. 用户请求: {cmd['user_input']}")
                print(f"     执行命令: {cmd['command']}")
                print(f"     执行结果: {'成功' if cmd['success'] else '失败'}")
                print(f"     相似度: {cmd['similarity_score']:.3f}")
    
    print("\n\n===== 测试完成 =====")

if __name__ == "__main__":
    test_search_similar_commands()