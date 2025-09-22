# Shell智能体

基于LangChain的智能Shell助手，能够根据自然语言输入生成并执行Shell命令，并提供错误分析和解决方案。

## 功能特点

- 🤖 **自然语言转Shell命令**：根据用户的自然语言描述生成对应的Shell命令
- ⚙️ **自动执行命令**：自动运行生成的Shell命令并返回结果
- 🔍 **错误分析与解决**：当命令执行失败时，自动分析错误并提供解决方案
- 📚 **RAG搜索增强**：利用检索增强生成(RAG)技术，基于历史命令提供更准确的结果
- 🧠 **命令历史记忆**：记住之前执行过的命令，并在相似情况下提供参考

## 安装说明

### 前提条件

- Python 3.8+
- OpenAI API密钥

### 安装步骤

1. 克隆或下载本项目到本地

2. 安装依赖包
   ```
   pip install -r requirements.txt
   ```

3. 创建`.env`文件并添加您的OpenAI API密钥
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## 使用方法

### 基本用法

运行主程序：

```
python main.py
```

然后按照提示输入您的需求，智能体将生成并执行相应的Shell命令。

### 高级选项

您可以通过命令行参数自定义智能体的行为：

```
python main.py --model gpt-4 --db-dir ./my_chroma_db
```

参数说明：
- `--model`：指定使用的OpenAI模型（默认：gpt-3.5-turbo）
- `--db-dir`：指定RAG向量数据库的存储目录（默认：./chroma_db）

## 项目结构

```
shell_agent/
├── __init__.py
├── agent.py           # 智能体主类
├── shell_generator.py # Shell命令生成模块
├── shell_executor.py  # Shell命令执行模块
├── error_analyzer.py  # 错误分析模块
└── rag_search.py      # RAG搜索增强模块
main.py                # 主程序入口
requirements.txt       # 依赖包列表
README.md             # 项目说明文档
```

## 示例

以下是一些使用示例：

1. **查找大文件**
   ```
   🧠 请输入您的需求: 找出当前目录下最大的5个文件
   ```

2. **系统信息查询**
   ```
   🧠 请输入您的需求: 显示系统内存和CPU使用情况
   ```

3. **文件操作**
   ```
   🧠 请输入您的需求: 将所有的txt文件移动到一个新的文件夹中
   ```

## 注意事项

- 本项目会执行生成的Shell命令，请确保您了解这些命令的作用，以避免意外操作。
- 在Windows环境中，命令将通过PowerShell执行。
- 需要有效的OpenAI API密钥才能使用此应用程序。

## 许可证

MIT