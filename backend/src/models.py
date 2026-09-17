"""Required response schema for contract comparisons."""

from typing import List

from pydantic import BaseModel


class ContractChangeOutput(BaseModel):
    sections_changed: List[str]
    topics_touched: List[str]
    summary_of_the_change: str
