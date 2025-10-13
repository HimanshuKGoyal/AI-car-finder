from pydantic import BaseModel, Field

class Feedback(BaseModel):
    requestId: int = Field(..., description="Client-generated or server-issued request id")
    mmv: str = Field(..., description="Make-Model-Variant identifier")
    action: str = Field(..., pattern="^(save|dismiss)$")