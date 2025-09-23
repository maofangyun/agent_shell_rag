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

class CommandConverter:
    """命令转换工具类 - 提供Linux和Windows命令的互相转换"""

    # 常用命令对照表
    COMMAND_MAP = {
        # 文件和目录操作
        'ls': {'windows': 'Get-ChildItem', 'linux': 'ls'},
        'll': {'windows': 'Get-ChildItem', 'linux': 'ls -la'},
        'pwd': {'windows': 'Get-Location', 'linux': 'pwd'},
        'cd': {'windows': 'Set-Location', 'linux': 'cd'},
        'mkdir': {'windows': 'New-Item -ItemType Directory', 'linux': 'mkdir'},
        'rm': {'windows': 'Remove-Item', 'linux': 'rm'},
        'cp': {'windows': 'Copy-Item', 'linux': 'cp'},
        'mv': {'windows': 'Move-Item', 'linux': 'mv'},
        'cat': {'windows': 'Get-Content', 'linux': 'cat'},
        'touch': {'windows': 'New-Item -ItemType File', 'linux': 'touch'},
        'find': {'windows': 'Get-ChildItem -Recurse', 'linux': 'find'},
        'grep': {'windows': 'Select-String', 'linux': 'grep'},
        'which': {'windows': 'Get-Command', 'linux': 'which'},
        'whoami': {'windows': 'whoami', 'linux': 'whoami'},
        'date': {'windows': 'Get-Date', 'linux': 'date'},
        'env': {'windows': 'Get-ChildItem Env:', 'linux': 'env'},
        'ps': {'windows': 'Get-Process', 'linux': 'ps'},
        'kill': {'windows': 'Stop-Process', 'linux': 'kill'},
        'head': {'windows': 'Select-Object -First', 'linux': 'head'},
        'tail': {'windows': 'Select-Object -Last', 'linux': 'tail'},
        'wc': {'windows': 'Measure-Object -Line -Word -Character', 'linux': 'wc'},
        'sort': {'windows': 'Sort-Object', 'linux': 'sort'},
        'uniq': {'windows': 'Sort-Object -Unique', 'linux': 'uniq'},
        'curl': {'windows': 'Invoke-WebRequest', 'linux': 'curl'},
        'wget': {'windows': 'Invoke-WebRequest', 'linux': 'wget'},
        'tar': {'windows': 'Compress-Archive/Expand-Archive', 'linux': 'tar'},
        'zip': {'windows': 'Compress-Archive', 'linux': 'zip'},
        'unzip': {'windows': 'Expand-Archive', 'linux': 'unzip'},
        'chmod': {'windows': '# Windows无直接等效命令', 'linux': 'chmod'},
        'chown': {'windows': '# Windows无直接等效命令', 'linux': 'chown'},
        'sudo': {'windows': '# 以管理员身份运行PowerShell', 'linux': 'sudo'},
        'apt': {'windows': '# Windows使用winget或choco', 'linux': 'apt'},
        'yum': {'windows': '# Windows使用winget或choco', 'linux': 'yum'},
        'systemctl': {'windows': 'Get-Service/Set-Service', 'linux': 'systemctl'},
        'service': {'windows': 'Get-Service/Set-Service', 'linux': 'service'},
    }

    @staticmethod
    def convert_command_to_windows(command: str) -> str:
        """将Linux命令转换为Windows PowerShell命令

        Args:
            command: Linux命令字符串

        Returns:
            str: 转换后的Windows命令
        """
        if not command:
            return command

        # 分割命令和参数
        parts = command.split()
        if not parts:
            return command

        cmd_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # 查找命令映射
        if cmd_name in CommandConverter.COMMAND_MAP:
            windows_cmd = CommandConverter.COMMAND_MAP[cmd_name]['windows']

            # 特殊处理一些命令
            if cmd_name == 'ls' and '-la' in args:
                return 'Get-ChildItem -Force'
            elif cmd_name == 'mkdir' and args:
                return f'New-Item -ItemType Directory -Path {" ".join(args)} -Force'
            elif cmd_name == 'touch' and args:
                return f'New-Item -ItemType File -Path {" ".join(args)} -Force'
            elif cmd_name == 'rm' and '-rf' in args:
                return f'Remove-Item -Recurse -Force {" ".join([arg for arg in args if arg != "-rf"])}'
            elif cmd_name == 'cp' and len(args) >= 2:
                return f'Copy-Item -Path {args[0]} -Destination {args[1]} -Recurse'
            elif cmd_name == 'mv' and len(args) >= 2:
                return f'Move-Item -Path {args[0]} -Destination {args[1]}'
            elif cmd_name == 'find' and args:
                return f'Get-ChildItem -Recurse -Filter {" ".join(args)}'
            elif cmd_name == 'grep' and args:
                pattern = args[0] if args else ''
                files = ' '.join(args[1:]) if len(args) > 1 else '*'
                return f'Select-String -Pattern "{pattern}" -Path {files}'
            elif cmd_name == 'ps' and 'aux' in args:
                return 'Get-Process | Format-Table -AutoSize'
            elif cmd_name == 'kill' and args:
                if args[0].isdigit():
                    return f'Stop-Process -Id {args[0]} -Force'
                else:
                    return f'Stop-Process -Name {args[0]} -Force'
            elif cmd_name == 'head' and args:
                n = args[0].replace('-n', '') if args[0].startswith('-n') else '10'
                file = args[1] if len(args) > 1 else ''
                return f'Get-Content {file} -Head {n}'
            elif cmd_name == 'tail' and args:
                n = args[0].replace('-n', '') if args[0].startswith('-n') else '10'
                file = args[1] if len(args) > 1 else ''
                return f'Get-Content {file} -Tail {n}'
            elif cmd_name == 'curl' and args:
                url = args[0] if args else ''
                return f'Invoke-WebRequest -Uri {url} -UseBasicParsing'
            elif cmd_name == 'wget' and args:
                url = args[0] if args else ''
                return f'Invoke-WebRequest -Uri {url} -OutFile (Split-Path -Leaf {url})'
            else:
                # 基本命令转换
                if args:
                    return f'{windows_cmd} {" ".join(args)}'
                else:
                    return windows_cmd

        # 如果没有找到映射，返回原始命令
        return command

    @staticmethod
    def get_system_command(command: str, is_windows: bool = None) -> str:
        """根据系统类型获取合适的命令

        Args:
            command: 命令字符串
            is_windows: 是否为Windows系统，如果为None则自动检测

        Returns:
            str: 适合当前系统的命令
        """
        if is_windows is None:
            is_windows = PlatformUtils.is_windows()

        if is_windows:
            return CommandConverter.convert_command_to_windows(command)
        else:
            return command