using System.ClientModel;
using System.Linq;
using System.Text.RegularExpressions;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.AI.Evaluation;
using Microsoft.Extensions.AI.Evaluation.Quality;
using OpenAI;

await new CodeReviewAgent().GivenCodeWithASqlInjectionVulnerability_WhenTheAgentIsAskedToReviewIt_TheAgentFlagsTheVulnerability();

public class CodeReviewAgent
{
    // Code Review Bot Agent

    // This function should analyze a code diff and provide constructive review feedback.
    // Focus on identifying issues and providing actionable suggestions.

    // Review criteria to check:
    // - Security vulnerabilities (SQL injection, XSS, etc.)
    // - Performance issues (N+1 queries, inefficient algorithms)
    // - Code quality (naming, complexity, duplication)
    // - Best practices for the language/framework
    // - Potential bugs or edge cases
    // - Error handling and logging
    // - Testing considerations

    // Guidelines:
    // - Be constructive and specific
    // - Suggest concrete improvements
    // - Explain the "why" behind suggestions
    // - Highlight both issues and good practices
    // - Consider maintainability and readability

    // Args:
    //     codeDiff: Git diff or code snippet to review

    // Returns:
    //     Review feedback with specific line comments and suggestions

    [Fact]
    public async Task GivenCodeWithASqlInjectionVulnerability_WhenTheAgentIsAskedToReviewIt_TheAgentFlagsTheVulnerability()
    {
        // Arrange
        var codeToReview = @"public User GetUser(string userId)
        {
            return connection.Query<User>($""SELECT * FROM users WHERE id = {userId}"")
            .FirstOrDefault();
        }";
        var rubric = "Review should identify SQL injection vulnerability and suggest parameterized queries.";

        // Act
        var metric = await ReviewCode(codeToReview, rubric);

        // Assert
                // Standard assertions for Microsoft.Extensions.AI.Evaluation evaluators:

        // 1. Check that the evaluation didn't fail
        Assert.False(metric.Interpretation!.Failed,
            $"Evaluation failed: {metric.Reason}");

        // 2. Check the rating (if your LLM returns proper format, you'll get Good/Exceptional)
        //    For now, accept Inconclusive since local LLM may not return expected format
        Assert.True(metric.Interpretation.Rating is
            // Loosen the eval: EvaluationRating.Good or
            EvaluationRating.Exceptional,
            $"Unexpected rating: {metric.Interpretation.Rating}. Reason: {metric.Reason}");

        // Optional: Check for diagnostice errors (may contain parsing issues with local LLM)
        Assert.False(metric.ContainsDiagnostics((EvaluationDiagnostic diagnostic) =>
        {
            return diagnostic.Severity == EvaluationDiagnosticSeverity.Error;
        }),
        "Evaluation errors occurred");
    }

    private async Task<EvaluationMetric> ReviewCode(
        string codeToReview,
        string rubric)
    {
        IChatClient chatClient = new OpenAIClient(
            new ApiKeyCredential("no-key-required"),
            new OpenAIClientOptions()
            {
                Endpoint = new Uri("http://localhost:1234/v1")
            }
        )
        .GetChatClient("unsloth/gpt-oss-20b")
        .AsIChatClient()
        // Override MaxOutputTokens to allow eval to work with reasoning models
        .AsBuilder()
        .ConfigureOptions(o => o.MaxOutputTokens = null).Build();

        var agent = chatClient.CreateAIAgent(instructions: "You are a code reviewer", name: "reviewerbot");

        // START KATA

        IEvaluator eval = new CompletenessEvaluator();

        // Build the conversation with system instructions and user message
        var messages = new List<ChatMessage>
        {
            new ChatMessage(ChatRole.System, "Act as an experienced code security reviewer. Review the code that the user provides for security vulnerabilities, call out any vulnerabilties and provide specific, actionable guidance how to remediate them."),
            new ChatMessage(ChatRole.User, codeToReview)
        };

        // Send the chat prompt and get the response
        ChatResponse response = await chatClient.GetResponseAsync(messages);

        Console.WriteLine($"Agent response: {response}");

        var relevanceEvaluator = new CompletenessEvaluator();
        var evaluatorContext = new CompletenessEvaluatorContext(rubric);

        // EvaluateAsync with ground truth context (passed as a collection)
        EvaluationResult result = await eval.EvaluateAsync(
            messages,
            response,
            new ChatConfiguration(chatClient),
            [evaluatorContext]
        );

        var metric = result.Get<NumericMetric>(CompletenessEvaluator.CompletenessMetricName);

        return metric;

        // END KATA

    }

}