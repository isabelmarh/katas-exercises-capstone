from __future__ import annotations

from typing import Literal

import questionary
from pydantic import AnyUrl, BaseModel, Field
from pydantic_ai import Agent

type Ring = Literal["Hold", "Assess", "Trial", "Adopt"]
type ClaimRating = Literal["TRUE", "FALSE", "MISLEADING", "UNVERIFIABLE"]


class Claim(BaseModel):
    claim: str = Field(description="...")
    rating: ClaimRating = Field(description="...")
    explanation: str = Field(description="...")
    sources: list[AnyUrl]


class Assessment(BaseModel):
    ring: str
    # ring: Ring = Field(description="...") # TODO: Give the agent more info on what to expect
    # claims: list[Claim] # TODO: Enable this on the second step


agent: Agent = Agent(
    model="google-gla:gemini-2.5-pro",
    # output_type=Assessment, # TODO: Enable this to change the output type
    instructions="...",  # TODO: Tell the agent what todo
)


def main():
    input = questionary.text(
        message="What is the TechRadar Blip description?\n", multiline=True
    ).ask()

    print("\nWaiting for agent...\n")
    res = agent.run_sync(input)

    print("\nResult:\n")

    if isinstance(res.output, BaseModel):
        print(res.output.model_dump_json(indent=2))
    else:
        print(str(res.output))


if __name__ == "__main__":
    main()
