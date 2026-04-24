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
    ring: Ring = Field(
        description="The Technology Radar ring classification. "
        "'Adopt' = strong recommendation, proven and mature. "
        "'Trial' = worth pursuing, teams should try on low-risk projects. "
        "'Assess' = worth exploring to understand impact. "
        "'Hold' = proceed with caution, not recommended for new projects."
    )
    claims: list[Claim] = Field(
        description="Objective factual claims extracted from the text, with verification."
    )


agent: Agent = Agent(
    model="anthropic:claude-sonnet-4-5",
    output_type=Assessment,
    instructions="""You are a Thoughtworks Technology Radar analyst. Given a blip description, you must:

1. CLASSIFY the blip into a Ring: Adopt, Trial, Assess, or Hold.
   - Adopt: Strong recommendation, proven at scale, sensible default
   - Trial: Worth pursuing, teams should try it on low-risk projects
   - Assess: Worth exploring to understand how it will affect your organization
   - Hold: Proceed with caution, not recommended for new adoption
   Look for signal words: "we recommend", "sensible default" → Adopt; "worth pursuing", "we've seen success" → Trial; "worth exploring", "keep an eye on" → Assess; "proceed with caution", "concerns" → Hold.

2. EXTRACT at least 3 objective factual claims from the text.
   - Focus on verifiable statements, not opinions
   - For each claim, rate it as TRUE, FALSE, MISLEADING, or UNVERIFIABLE
   - Provide a brief explanation of your verification
   - Include at least one credible source URL for each claim (use real, well-known URLs like official docs, Wikipedia, or reputable tech publications)
""",
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
