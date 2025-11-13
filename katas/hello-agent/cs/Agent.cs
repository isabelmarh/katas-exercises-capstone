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

await new Agent().HelloAgent();

public class Agent
{
    private static string AgentName = "HelloAgent";
    private static readonly ActivitySource AgentActivitySource = new ActivitySource(AgentName);
    private static readonly Meter AgentMeter = new(AgentName, "1.0");

    [Fact]
    public async Task HelloAgent()
    {
        // Configure Opik Open Telemetry endpoint
        string otlpEndpoint = Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT") ?? "http://localhost:5173/api/v1/private/otel/v1/traces";
        var openAiApiEndpoint = Environment.GetEnvironmentVariable("OPENAI_API_ENDPOINT") ?? "http://localhost:1234/v1";
        var openApiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY") ?? "no-key-required";
        var model = Environment.GetEnvironmentVariable("OPENAI_API_MODEL") ?? "unsloth/gpt-oss-20b";
        
        // Method to configure exporter options
        Action<OtlpExporterOptions> otlpExporterOptions = (options) => 
        {
            options.Endpoint = new Uri(otlpEndpoint);
            options.Protocol = OtlpExportProtocol.HttpProtobuf;
            options.Headers = $"projectName=katas";
        };
        // Method to configure otel logging
        Action<OpenTelemetryLoggerOptions> otelLoggingOptions = options =>
        {
            options.SetResourceBuilder(ResourceBuilder.CreateDefault().AddService(AgentName, serviceVersion: "1.0.0"));
            options.AddOtlpExporter(otlpOptions => otlpOptions.Endpoint = new Uri(otlpEndpoint));
            options.IncludeScopes = true;
            options.IncludeFormattedMessage = true;
        };

        // Configure OTel tracing
        using var tracerProvider = Sdk.CreateTracerProviderBuilder()
            .SetResourceBuilder(ResourceBuilder.CreateDefault().AddService(AgentName))
            .AddSource(AgentName)
            .AddSource("*Microsoft.Agents.AI") // Agent Framework telemetry
            .AddHttpClientInstrumentation() // Capture HTTP calls to OpenAI
            .AddOtlpExporter(otlpExporterOptions)
            .Build();    

        // Start an activity (span) with some tags (attributes)
        using (var activity = AgentActivitySource.StartActivity(AgentName))
        {
            IChatClient chatClient = new OpenAIClient(
                new ApiKeyCredential("no-key-required"),
                new OpenAIClientOptions()
                {
                    Endpoint = new Uri(openAiApiEndpoint)
                }
            )
            .GetChatClient(model)
            .AsIChatClient()
            // Override MaxOutputTokens to allow eval to work with reasoning models
            .AsBuilder()
            .UseOpenTelemetry(                  // Enable telemetry on chat client
                sourceName: AgentName,
                configure: (cfg) => cfg.EnableSensitiveData = true)
            .ConfigureOptions(o => o.MaxOutputTokens = null)
            .Build();

            var agent = chatClient.CreateAIAgent(
                instructions: "Simply respond with 'Hello from Agent' without any additional markup or syntax.",
                name: AgentName
            ).AsBuilder()
            .UseOpenTelemetry(
                sourceName: AgentName,
                configure: (cfg) => cfg.EnableSensitiveData = true)
            .Build();

            // Send the chat prompt and get the response
            string request = "Hello, Agent";
            var response = await agent.RunAsync(request);

            Console.WriteLine($"Agent response: {response}");

            IEvaluator eval = new EquivalenceEvaluator();
            // EquivalenceEvaluator needs ground truth provided via EquivalenceEvaluatorContext
            var evaluatorContext = new EquivalenceEvaluatorContext("Hello from Agent");

            // EvaluateAsync with ground truth context (passed as a collection)
            EvaluationResult result = await eval.EvaluateAsync(
                request,
                response.Text,
                new ChatConfiguration(chatClient),
                [evaluatorContext]
            );

            var metrics = result.Get<NumericMetric>(EquivalenceEvaluator.EquivalenceMetricName);

            // Create a counter instrument
            Histogram<int> equivalenceMeter = AgentMeter.CreateHistogram<int>("Equivalence");

            // Configure the OpenTelemetry MeterProvider
            using var meterProvider = Sdk.CreateMeterProviderBuilder()
                .AddMeter(Assembly.GetExecutingAssembly().FullName!)
                .AddOtlpExporter((options) =>
                {
                    options.Endpoint = new Uri(otlpEndpoint);
                    options.Protocol = OtlpExportProtocol.HttpProtobuf;
                    options.Headers = $"projectName=katas";
                })
                .Build();

            // Standard assertions for Microsoft.Extensions.AI.Evaluation evaluators:

            // 1. Check that the evaluation didn't fail
            Assert.False(metrics.Interpretation!.Failed,
                $"Equivalence evaluation failed: {metrics.Reason}");

            // 2. Check the rating (if your LLM returns proper format, you'll get Good/Exceptional)
            Assert.True(metrics.Interpretation.Rating is
                // Loosen the eval: EvaluationRating.Good or
                EvaluationRating.Exceptional,
                $"Unexpected rating: {metrics.Interpretation.Rating}. Reason: {metrics.Reason}");

            // Optional: Check for diagnostics (may contain parsing issues with local LLM)
            Assert.False(metrics.ContainsDiagnostics(), "Evaluation produced diagnostic issues");

        }
    }
}