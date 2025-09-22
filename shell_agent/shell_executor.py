"""
Shell命令执行模块 - 负责执行生成的shell命令并处理结果
"""
import subprocess
from typing import Dict, Any, Tuple
import platform
import os

class ShellExecutor:
    """执行shell命令并处理结果的类"""
    
    def __init__(self):
        """初始化Shell执行器"""
        self.is_windows = platform.system() == "Windows"
    
    def execute_command(self, command: str) -> Tuple[bool, str]:
        """执行shell命令并返回结果
        
        Args:
            command: 要执行的shell命令
            
        Returns:
            Tuple[bool, str]: (是否成功, 输出结果或错误信息)
        """
        try:
            # 在Windows上使用PowerShell执行命令
            if self.is_windows:
                process = subprocess.Popen(
                    ["powershell", "-Command", command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )
            else:
                # 在Linux/Mac上使用bash执行命令
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )
            
            # 获取命令输出
            stdout, stderr = process.communicate()
            
            # 检查命令是否成功执行
            if process.returncode == 0:
                return True, stdout
            else:
                return False, stderr
        except Exception as e:
            return False, f"执行命令时出错: {str(e)}"
    
    def format_result(self, success: bool, output: str) -> Dict[str, Any]:
        """格式化命令执行结果
        
        Args:
            success: 命令是否成功执行
            output: 命令的输出或错误信息
            
        Returns:
            Dict[str, Any]: 格式化的结果
        """
        return {
            "success": success,
            "output": output
        }