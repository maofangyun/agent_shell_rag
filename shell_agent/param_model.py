from pydantic import BaseModel, Field

# 在ShellAgent类外部定义参数模型
class SaveCommandHistoryParams(BaseModel):
    user_input: str = Field(..., description="用户的原始请求")
    command: str = Field(..., description="实际执行的shell命令")
    result: str = Field(..., description="命令执行的完整输出内容")
    success: bool = Field(..., description="表示命令是否执行成功")

class AnalyzeCommandErrorParams(BaseModel):
    """用于 analyze_command_error 工具的参数模型"""
    user_input: str = Field(..., description="用户的原始请求")
    command: str = Field(..., description="执行失败的shell命令")
    error_message: str = Field(..., description="命令返回的错误信息")