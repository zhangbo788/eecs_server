from pydantic import BaseModel, Field
from typing import List, Dict


class IdNameItem(BaseModel):
    id: int = Field(title="专业编号")
    name: str = Field(title="专业名称")


class ListData(BaseModel):
    class ListDataModel(BaseModel):
        total: int = Field("items的长度")
        items: List[IdNameItem] = Field(title="专业")

    code: int = Field(title="代码")
    data: ListDataModel = Field(title="数据")
