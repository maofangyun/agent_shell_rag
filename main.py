"""
Shell智能体应用程序入口
"""
import os
import sys
from dotenv import load_dotenv
from shell_agent.agent import ShellAgent
import argparse

# 加载环境变量
load_dotenv()

def print_colored(text, color_code):
    """打印彩色文本"""
    print(f"\033[{color_code}m{text}\033[0m")

def print_success(text):
    """打印成功信息（绿色）"""
    print_colored(text, "32")

def print_error(text):
    """打印错误信息（红色）"""
    print_colored(text, "31")

def print_info(text):
    """打印信息（蓝色）"""
    print_colored(text, "34")

def print_command(text):
    """打印命令（黄色）"""
    print_colored(text, "33")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Shell智能体 - 基于LangChain的智能Shell助手")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="使用的OpenAI模型名称")
    parser.add_argument("--db-dir", default="./chroma_db", help="RAG向量数据库持久化目录")
    args = parser.parse_args()
    
    # 检查OpenAI API密钥
    if not os.environ.get("OPENAI_API_KEY"):
        print_error("错误: 未设置OPENAI_API_KEY环境变量")
        print_info("请创建.env文件并添加您的OpenAI API密钥:")
        print_info("OPENAI_API_KEY=your_api_key_here")
        return
    
    # 初始化Shell智能体
    print_info(f"初始化Shell智能体 (模型: {args.model})...")
    agent = ShellAgent(model_name=args.model, rag_persist_directory=args.db_dir)
    print_success("Shell智能体初始化完成!")
    
    print_info("欢迎使用Shell智能体! 输入您的需求，智能体将生成并执行相应的Shell命令。")
    print_info("输入 'exit' 或 'quit' 退出程序。")
    
    # 主循环
    while True:
        try:
            # 获取用户输入
            print()
            user_input = input("🧠 请输入您的需求: ")
            
            # 检查退出命令
            if user_input.lower() in ["exit", "quit"]:
                print_info("感谢使用Shell智能体，再见!")
                break
            
            # 处理用户输入
            print_info("正在处理您的请求...")
            result = agent.process_input(user_input)
            
            # 显示生成的命令
            print("\n📋 生成的命令:")
            print_command(result["command"])
            
            # 显示执行结果
            print("\n🖥️ 执行结果:")
            if result["success"]:
                print_success("✅ 命令执行成功!")
                print(result["output"])
            else:
                print_error("❌ 命令执行失败!")
                print(result["output"])
                
                # 显示错误分析和解决方案
                if result["error_analysis"]:
                    print("\n🔍 错误分析和解决方案:")
                    print(result["error_analysis"])
            
            # 显示相似的历史命令
            if result["similar_commands"]:
                print("\n📚 相似的历史命令:")
                for i, cmd in enumerate(result["similar_commands"], 1):
                    print(f"{i}. 用户请求: {cmd['user_input']}")
                    print(f"   执行命令: {cmd['command']}")
                    print(f"   执行结果: {'成功' if cmd['success'] else '失败'}")
                    print()
            
        except KeyboardInterrupt:
            print_info("\n操作已取消。输入 'exit' 或 'quit' 退出程序。")
        except Exception as e:
            print_error(f"\n发生错误: {str(e)}")

if __name__ == "__main__":
    main()