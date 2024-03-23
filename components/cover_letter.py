from langchain_core.pydantic_v1 import BaseModel, Field, validator
from typing import List


class CoverLetterContents(BaseModel):
    company_name: str = Field(description="The name of the company of the job listing.")
    company_address: str = Field(
        description="The address of the company you are applying to, including the city and state."
    )
    contents: List[str] = Field(
        description="The contents of the cover letter. Each paragraph should be in its own element."
    )

    @validator("contents", each_item=True, allow_reuse=True)
    def check_non_empty(cls, v):
        if not v.strip():
            raise ValueError("Content items must not be empty")
        return v

    def save(self, fp: str) -> None:
        with open(fp, "w") as f:
            f.write(str(self))
