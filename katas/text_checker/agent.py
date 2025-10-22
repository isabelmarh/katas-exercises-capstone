from __future__ import annotations

from typing import Literal

from pydantic import AnyUrl, BaseModel, Field
from pydantic_ai import Agent

type Ring = Literal["Hold", "Assess", "Trial", "Adopt"]
type ClaimRating = Literal["TRUE", "FALSE", "MISLEADING", "UNVERIFIABLE"]
import questionary



class Claim(BaseModel):
    claim: str = Field(description="...")
    rating: ClaimRating = Field(description="...")
    explanation: str = Field(description="...")
    sources: list[AnyUrl]


class Assessment(BaseModel):
    ring: Ring
    # claims: list[Claim] # TODO: Enable this on the second step


agent: Agent[None, Assessment] = Agent(
    model="google-gla:gemini-2.5-pro", output_type=Assessment, instructions="..."
)

if __name__ == "__main__":
    input = questionary.text(
        message="What is the TechRadar Blip description?\n", multiline=True
    ).ask()

    print("\nWaiting for agent...\n")
    res = agent.run_sync(input)

    print("\nResult:\n")
    print(res.output.model_dump_json(indent=2))
