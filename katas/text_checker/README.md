# TEXT Checker

## Goal

The goal of this Kata is to build an AI agent that analyzes the "blips" from Thoughtworks's Tech radar, volume 32, and performs two main tasks:

1. **Derive Rating from text**: Take the text written by Thoughtworkers and let the agent come up with the rating. Reasoning behind is that we have so a cool evaluation case with ground truth. Let's not overthink how valuable this is.

2. **Fact Extraction & Fact Checking**: Extract objective facts from the (obviously opinionated) radar text, and then fact-check these statements. For each fact, the agent should attempt to provide supporting sources, leveraging Gemini's internal search capabilities for fact verification.

The broader goal is to explore and demonstrate Gemini's internal search and fact-checking abilities in a practical, challenging context.

## Challenge

Breakdown of the main challenges:

1. **Rating/Text Consistency**: For each blip, determine the rating assessment.
2. **Fact Extraction**: Identify and extract objective, factual statements from the radar text, separating them from opinions or subjective commentary.
3. **Fact Checking with Sources**: For each extracted fact, verify its accuracy using trusted sources. The agent should return both the verdict (true/false/uncertain) and the sources used for verification.

## Input

* `blips_vol32.yaml`, Note no guarantee for correctness has been converted to yaml via Gemini
