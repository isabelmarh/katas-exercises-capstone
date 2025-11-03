using System.ClientModel;
using System.Linq;
using System.Text.RegularExpressions;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.AI.Evaluation;
using Microsoft.Extensions.AI.Evaluation.Quality;
using OpenAI;

await new HelloAgent().GivenTheHelloAgentIsWorking_WhenGivenAnyPrompt_TheAgentRespondsWithHello();

public class HelloAgent
{
    [Fact]
    public async Task GivenTheHelloAgentIsWorking_WhenGivenAnyPrompt_TheAgentRespondsWithHello()
    {
        IChatClient chatClient = new OpenAIClient(
            new ApiKeyCredential("no-key-required"),
            new OpenAIClientOptions()
            {
                Endpoint = new Uri("http://localhost:1234/v1")
            }
        )
        .GetChatClient("gpt-oss-20b")
        .AsIChatClient()
        // Override MaxOutputTokens to allow eval to work with reasoning models
        .AsBuilder()
        .ConfigureOptions(o => o.MaxOutputTokens = null).Build();

        IEvaluator eval = new EquivalenceEvaluator();

        // Build the conversation with system instructions and user message
        var messages = new List<ChatMessage>
        {
            new ChatMessage(ChatRole.System, "Simply respond with 'Hello from Agent' without any additional markup or syntax."),
            new ChatMessage(ChatRole.User, "Hello, Agent")
        };

        // Send the chat prompt and get the response
        ChatResponse response = await chatClient.GetResponseAsync(messages);

        Console.WriteLine($"Agent response: {response}");

        // EquivalenceEvaluator needs ground truth provided via EquivalenceEvaluatorContext
        var evaluatorContext = new EquivalenceEvaluatorContext("Hello from Agent");

        // EvaluateAsync with ground truth context (passed as a collection)
        EvaluationResult result = await eval.EvaluateAsync(
            messages,
            response,
            new ChatConfiguration(chatClient),
            [evaluatorContext]
        );

        var metrics = result.Get<NumericMetric>(EquivalenceEvaluator.EquivalenceMetricName);

        // Standard assertions for Microsoft.Extensions.AI.Evaluation evaluators:

        // 1. Check that the evaluation didn't fail
        Assert.False(metrics.Interpretation!.Failed,
            $"Equivalence evaluation failed: {metrics.Reason}");

        // 2. Check the rating (if your LLM returns proper format, you'll get Good/Exceptional)
        //    For now, accept Inconclusive since local LLM may not return expected format
        Assert.True(metrics.Interpretation.Rating is
            // Loosen the eval: EvaluationRating.Good or
            EvaluationRating.Exceptional,
            $"Unexpected rating: {metrics.Interpretation.Rating}. Reason: {metrics.Reason}");

        // Optional: Check for diagnostics (may contain parsing issues with local LLM)
        Assert.False(metrics.ContainsDiagnostics(), "Evaluation produced diagnostic issues");

    }

}