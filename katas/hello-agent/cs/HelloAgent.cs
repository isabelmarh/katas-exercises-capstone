using System.ClientModel;
using System.ComponentModel;
using System.Diagnostics;
using System.Diagnostics.Metrics;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using OpenAI;
using OpenTelemetry;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using OpenTelemetry.Exporter;
using Microsoft.Extensions.AI.Evaluation;
using Microsoft.Extensions.AI.Evaluation.Quality;
using System.Reflection;
using OpenTelemetry.Metrics;
using OpenTelemetry.Logs;
using Thoughtworks.Katas.Agents;

await new HelloAgent().Run();

public class HelloAgent
{
    private static string AgentName = nameof(HelloAgent);
    private static readonly ActivitySource AgentActivitySource = new ActivitySource(AgentName);

    [Fact]
    public async Task Run()
    {
        // Configure Opik Open Telemetry endpoint
        string otlpEndpoint = Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT") ?? "http://localhost:5173/api/v1/private/otel/v1/traces";
        var openAiApiEndpoint = Environment.GetEnvironmentVariable("OPENAI_API_ENDPOINT") ?? "http://localhost:1234/v1";
        var openApiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY") ?? "no-key-required";
        var model = Environment.GetEnvironmentVariable("OPENAI_API_MODEL") ?? "unsloth/gpt-oss-20b";

        // Start an activity
        using (var activity = AgentActivitySource.StartActivity(AgentName))
        {
            var (agent, chatClient, logger, meter) = InstrumentedAgents.Build<HelloAgent>(
                agentName: AgentName,
                instructions: "Simply respond with 'Hello from Agent' without any additional markup, prefixes or suffixes, or syntax.",
                model: "unsloth/gpt-oss-20b",
                openAiApiKey: "no-key-needed",
                activitySource: AgentActivitySource);

            var agentStopwatch = Stopwatch.StartNew();

            // Send the chat prompt and get the response
            string request = "Hello, Agent";
            var response = await agent.RunAsync(request);

            agentStopwatch.Stop();
            var agentResponseTime = agentStopwatch.Elapsed.TotalSeconds;

            Console.WriteLine($"Agent response: {response}");

            IEvaluator eval = new EquivalenceEvaluator();
            // EquivalenceEvaluator needs ground truth provided via EquivalenceEvaluatorContext
            var evaluatorContext = new EquivalenceEvaluatorContext("[Assistant] Hello from Agent");

            var evalStopwatch = Stopwatch.StartNew();

            // EvaluateAsync with ground truth context (passed as a collection)
            EvaluationResult result = await eval.EvaluateAsync(
                request,
                response.Text,
                new ChatConfiguration(chatClient),
                [evaluatorContext]
            );

            evalStopwatch.Stop();
            var evalResponseTime = evalStopwatch.Elapsed.TotalSeconds;

            var metrics = result.Get<NumericMetric>(EquivalenceEvaluator.EquivalenceMetricName);

            // OTel metrics
            var equivalenceRatingHistogram = meter.CreateHistogram<int>("Equivalence");
            var agentResponseTimeHistogram = meter.CreateHistogram<double>("agent_response_time_seconds", description: "Agent response time in seconds");
            var evalDurationHistogram = meter.CreateHistogram<double>("eval_duration_time", description: "Time taken to perform evaluation");

            // Log OTel metrics
            equivalenceRatingHistogram.Record((int)metrics.Interpretation.Rating);
            agentResponseTimeHistogram.Record(agentResponseTime);
            evalDurationHistogram.Record(evalResponseTime);

            // Standard assertions for Microsoft.Extensions.AI.Evaluation evaluators:

            // 1. Check that the evaluation didn't fail
            Assert.False(metrics.Interpretation!.Failed,
                $"Equivalence evaluation failed: {metrics.Reason}"); 

            // 2. Check the rating (if your LLM returns proper format, you'll get Good/Exceptional)
            Assert.True(metrics.Interpretation.Rating is
                EvaluationRating.Good or
                EvaluationRating.Exceptional,
                $"Unexpected rating: {metrics.Interpretation.Rating}");

            // Optional: Check for diagnostics (may contain parsing issues with local LLM)
            Assert.False(metrics.ContainsDiagnostics(), "Evaluation produced diagnostic issues");

            activity?.SetTag("success", "true");
        }
    }
}