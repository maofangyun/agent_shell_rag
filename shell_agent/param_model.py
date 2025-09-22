from pydantic import BaseModel, Field

# 在ShellAgent类外部定义参数模型
class SaveCommandHistoryParams(BaseModel):
    user_requirement: str = Field(..., description="用户的原始请求")
    command: str = Field(..., description="实际执行的shell命令")
    result: str = Field(..., description="命令执行的完整输出内容")
    success: bool = Field(..., description="表示命令是否执行成功")