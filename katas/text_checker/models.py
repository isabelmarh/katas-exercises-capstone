from __future__ import annotations

from typing import Literal

from pydantic import AnyUrl, BaseModel, Field

type Rating = Literal["Hold", "Assess", "Trial", "Adopt"]


class Claim(BaseModel):
    claim: str = Field(description="The specific claim extracted from the text")
    rating: Literal["TRUE", "FALSE", "MISLEADING", "UNVERIFIABLE"] = Field(
        description="Rating of the claim"
    )
    explanation: str = Field(
        description="Detailed explanation with supporting evidence"
    )
    sources: list[AnyUrl]


class Assessment(BaseModel):
    rating: Rating
    claims: list[Claim]
