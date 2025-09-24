"""
Shell命令执行模块 - 负责执行生成的shell命令并处理结果
"""
import subprocess
from typing import Tuple
from .utils import PlatformUtils

class ShellExecutor:
    """执行shell命令并处理结果的类"""

    def __init__(self, timeout: int = 30):
        """初始化Shell执行器
        
        Args:
            timeout: 命令执行超时时间（秒）
        """
        self.shell_cmd = PlatformUtils.get_shell_command()
        self.timeout = timeout

    def _create_subprocess(self, command: str) -> subprocess.Popen:
        """创建子进程执行命令"""
        return subprocess.Popen(
            self.shell_cmd + [command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )

    def execute_command(self, command: str) -> Tuple[bool, str]:
        """执行shell命令并返回结果

        Args:
            command: 要执行的shell命令

        Returns:
            Tuple[bool, str]: (是否成功, 输出结果或错误信息)
        """
        try:
            # 创建并执行子进程
            process = self._create_subprocess(command)
            stdout, stderr = process.communicate(timeout=self.timeout)

            # 返回执行结果
            return process.returncode == 0, stdout if process.returncode == 0 else stderr

        except subprocess.TimeoutExpired:
            process.kill()
            return False, f"命令执行超时 ({self.timeout}秒)"
        except Exception as e:
            return False, f"执行命令时出错: {str(e)}"