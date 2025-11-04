#!/bin/bash

# Create the dotnet project (as a unit test project)
echo "Creating the dotnet project"
dotnet new xunit

# Install the Microsoft Agent Framework library
echo "Installing the Microsoft Agent Framework library"
dotnet add package Microsoft.Agents.AI --prerelease

# Install OpenAI model support
echo "Installing OpenAI libraries"
dotnet add package Microsoft.Extensions.AI.OpenAI --prerelease

# Install Microsoft agent evaluators
echo "Installing agent evaluators"
dotnet add package Microsoft.Extensions.AI.Evaluation
dotnet add package Microsoft.Extensions.AI.Evaluation.Quality