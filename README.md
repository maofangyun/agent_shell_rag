# Shell Agent

Shell Agent 是一个基于 LangChain 和大语言模型（LLM）构建的智能 Shell 命令助手。它能理解自然语言描述的用户需求，自动生成、执行相应的 Shell 命令，并能从执行历史中学习，分析错误。

## 核心功能

- **自然语言到 Shell 命令**：将“列出当前目录下最大的三个文件”这样的自然语言直接转化为可执行的 Shell 命令。
- **命令自动执行**：无缝执行生成的命令，并返回执行结果或错误信息。
- **错误分析**：当命令执行失败时，Agent 会尝试分析错误原因并提供解决方案。
- **RAG 增强**：通过检索相似的历史成功/失败案例，提高生成命令的准确性。
- **历史记录**：将所有成功的命令执行历史保存到向量数据库中，用于未来的检索增强。

## 项目结构

经过优化后，项目采用了更清晰、更模块化的结构：

```
shell_agent/
├── __init__.py         # 包初始化文件
├── agent.py            # 核心 Agent 类，负责协调和规划
├── error_analyzer.py   # 错误分析模块
├── param_model.py      # 工具参数的 Pydantic 模型
├── rag_search.py       # RAG 检索和历史记录模块
└── shell_executor.py   # Shell 命令执行模块
```

## 安装与配置

1.  **克隆项目**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

3.  **配置环境变量**
    项目需要 OpenAI 的 API 密钥才能工作。请在您的执行环境中设置以下环境变量：
    ```bash
    export OPENAI_API_KEY="your-openai-api-key"
    ```

## 使用示例

以下是如何在 Python 代码中使用 `ShellAgent` 的一个简单示例：

```python
from shell_agent.agent import ShellAgent

# 1. 初始化 Agent
# 你可以指定使用的模型和 RAG 数据库的持久化路径
shell_agent = ShellAgent(model_name="gpt-4", rag_persist_directory="./shell_commands_db")

# 2. 处理用户输入
user_request = "在当前目录创建一个名为 'test_dir' 的新目录"
result = shell_agent.process_input(user_request)

# 3. 查看结果
print(f"用户请求: {user_request}")
print("-" * 20)

# 从返回结果中安全地获取命令
command = result.get("command", "未能提取命令")
print(f"生成的命令: {command}")

# 查看执行输出
output = result.get("output", "没有输出")
print(f"执行输出:\n{output}")

# 查看执行状态
success = result.get("success", False)
print(f"执行是否成功: {success}")