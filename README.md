# Shell Agent

Shell Agent 是一个基于 LangChain 和大语言模型（LLM）构建的智能 Shell 命令助手。它能理解自然语言描述的用户需求，自动生成、执行相应的 Shell 命令，并能从执行历史中学习和分析错误。

## 核心功能

- **自然语言到 Shell 命令**：将“列出当前目录下最大的三个文件”这样的自然语言直接转化为可执行的 Shell 命令，并能根据操作系统（Windows/Linux/macOS）生成兼容的命令。
- **命令自动执行**：无缝执行生成的命令，并返回实时、完整的执行结果或错误信息。
- **智能错误分析**：当命令执行失败时，Agent 会调用 LLM 分析错误原因并提供详细的解决方案。
- **RAG 增强**：通过检索相似的历史成功/失败案例，为 Agent 提供决策参考，从而提高生成命令的准确性。
- **长期记忆**：将所有成功的命令执行历史保存到向量数据库中，用于未来的检索增强，形成长期记忆。

## 项目结构

项目采用了清晰、模块化的结构设计，各模块职责分明：

```
shell_agent/
├── __init__.py         # 包初始化文件
├── agent.py            # 核心 Agent 类，负责任务规划和工具协调
├── error_analyzer.py   # 错误分析模块，调用 LLM 分析失败原因
├── param_model.py      # 定义工具输入参数的 Pydantic 模型
├── rag_search.py       # RAG 检索和历史命令管理模块
├── shell_executor.py   # Shell 命令执行模块，处理底层命令交互
└── utils.py            # 通用工具类，提供平台检测等辅助功能
```

## 安装与配置

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. 安装依赖

项目依赖项记录在 `requirements.txt` 文件中。

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

项目需要 OpenAI 的 API 密钥才能工作。请在项目根目录下创建一个 `.env` 文件，并填入您的密钥：

```
OPENAI_API_KEY="your-openai-api-key"
```

*注意：应用会自动加载 `.env` 文件中的环境变量。*

## 使用示例

以下是如何在 Python 代码中使用 `ShellAgent` 的一个完整示例：

```python
from shell_agent.agent import ShellAgent
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 1. 初始化 Agent
# 你可以指定使用的模型和 RAG 数据库的持久化路径
shell_agent = ShellAgent(model_name="gpt-4", rag_persist_directory="./shell_commands_db")

# 2. 处理用户输入（一个成功示例）
print("--- 场景1: 执行成功 ---")
user_request_success = "在当前目录创建一个名为 'test_dir' 的新目录"
result_success = shell_agent.process_input(user_request_success)

# 3. 查看成功结果
print(f"用户请求: {user_request_success}")
print("-" * 20)
print(f"生成的命令: {result_success.get('command', 'N/A')}")
print(f"执行是否成功: {result_success.get('success', False)}")
print(f"执行输出:\n{result_success.get('output', 'N/A')}")

print("\n" + "="*40 + "\n")

# 4. 处理用户输入（一个失败示例）
print("--- 场景2: 执行失败并进行错误分析 ---")
user_request_fail = "删除一个不存在的文件 'non_existent_file.txt'"
result_fail = shell_agent.process_input(user_request_fail)

# 5. 查看失败结果和错误分析
print(f"用户请求: {user_request_fail}")
print("-" * 20)
print(f"生成的命令: {result_fail.get('command', 'N/A')}")
print(f"执行是否成功: {result_fail.get('success', False)}")
print(f"执行输出:\n{result_fail.get('output', 'N/A')}")
if not result_fail.get('success'):
    print(f"\n错误分析:\n{result_fail.get('error_analysis', '没有可用的分析。')}")

# 6. 查看 RAG 检索到的相似历史命令
print("\n--- 场景3: 检索相似历史命令 ---")
similar_commands = result_success.get('similar_commands', [])
if similar_commands:
    print("检索到以下相似历史命令:")
    for cmd in similar_commands:
        print(f"  - 命令: {cmd['command']} (相似度: {cmd['similarity_score']:.2f})")
else:
    print("没有找到相似的历史命令。")
