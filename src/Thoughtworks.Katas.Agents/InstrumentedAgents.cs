using System.ClientModel;
using System.Diagnostics;
using System.Diagnostics.Metrics;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using OpenAI;
using OpenTelemetry;
using OpenTelemetry.Exporter;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

namespace Thoughtworks.Katas.Agents;

public static class InstrumentedAgents
{
    public static (Microsoft.Agents.AI.AIAgent, Microsoft.Extensions.AI.IChatClient, ILogger) Build<T>(
        string agentName = "AIAgent",
        string openAiApiEndpoint = "http://localhost:1234/v1", // For OpenAI API: "https://api.openai.com/v1",
        string openAiApiKey = "",
        string model = "gpt-4o",
        string instructions = "You are a helpful assistant that provides concise and informative responses.",
        IList<AITool>? tools = default(List<AITool>),
        ActivitySource activitySource = null,
        string telemetryEndpoint = "http://localhost:5173/api/v1/private/otel/v1/traces", // Opik endpoint
        string telemetryProjectName = "katas"
    )
    {
        // Set up OTel
        string SourceName = agentName;
        string ServiceName = agentName;
        var otlpEndpoint = telemetryEndpoint;

        Action<OtlpExporterOptions> otlpExporterOptions = (options) => 
        {
            options.Endpoint = new Uri(otlpEndpoint);
            options.Protocol = OtlpExportProtocol.HttpProtobuf;
            options.Headers = $"projectName={telemetryProjectName}";
        };
        // Build the providers for exporting traces and metrics to the OTel endpoint
        var resource = BuildResourceProfile(ServiceName);
        var traceProvider = BuildTraceProvider(SourceName, agentName, otlpExporterOptions);
        var meterProvider = BuildMeterProvider(SourceName, agentName, otlpExporterOptions);

        // Setup structured logging with OpenTelemetry
        var serviceCollection = new ServiceCollection();
        ConfigureLoggingWithOTel(ServiceName, serviceCollection, otlpExporterOptions);
        var serviceProvider = serviceCollection.BuildServiceProvider();
        var loggerFactory = serviceProvider.GetRequiredService<ILoggerFactory>();
        var appLogger = loggerFactory.CreateLogger<T>();

        // Configure Metrics
        using var meter = new Meter(SourceName);

        var interactionCounter = meter.CreateCounter<int>("agent_interactions_total", description: "Total number of agent interactions");
        var responseTimeHistogram = meter.CreateHistogram<double>("agent_response_time_seconds", description: "Agent response time in seconds");

        // Create instrumented chat client
        using var instrumentedChatClient = new OpenAIClient(
            new ApiKeyCredential(openAiApiKey),
            new OpenAIClientOptions()
            {
                Endpoint = new Uri(openAiApiEndpoint)
            }
        )
        .GetChatClient(model)
        .AsIChatClient()
        .AsBuilder()
        .UseFunctionInvocation()
        .UseOpenTelemetry(
            sourceName: SourceName,
            configure: (cfg) => cfg.EnableSensitiveData = true)
        // Override MaxOutputTokens to allow evals to work with reasoning models
        .ConfigureOptions(o => o.MaxOutputTokens = null)
        .Build();

        appLogger.LogInformation("Creating Agent with OpenTelemetry instrumentation");
        // Create the agent with the instrumented chat client
        var agent = new ChatClientAgent(instrumentedChatClient,
            name: agentName,
            instructions: instructions,
            tools: tools)
            .AsBuilder()
            .UseOpenTelemetry(SourceName, configure: (cfg) => cfg.EnableSensitiveData = true) // enable telemetry at the agent level
            .Build();

        return (agent, instrumentedChatClient, appLogger);

        // var thread = agent.GetNewThread();

        // appLogger.LogInformation("Agent created successfully with ID: {AgentId}", agent.Id);

        // // Create a parent span for the entire agent session
        // using var sessionActivity = activitySource.StartActivity("Agent Session");
        // Console.WriteLine($"Trace ID: {sessionActivity?.TraceId} ");

        // var sessionId = Guid.NewGuid().ToString("N");
        // sessionActivity?
        //     .SetTag("agent.name", "Hello.Agent")
        //     .SetTag("session.id", sessionId)
        //     .SetTag("session.start_time", DateTimeOffset.UtcNow.ToString("O"));

        // appLogger.LogInformation("Starting agent session with ID: {SessionId}", sessionId);
        // using (appLogger.BeginScope(new Dictionary<string, object> { ["SessionId"] = sessionId, ["AgentName"] = agent.Name ?? "InstrumentedAIAgent" }))
        // {
        //     var interactionCount = 0;

        //     // while (true)
        //     // {
        //     //Console.Write("You (or 'exit' to quit): ");
        //     const string UserInput = "Name the last 20 kings and queens of England"; //Console.ReadLine();

        //     // if (string.IsNullOrWhiteSpace(userInput) || userInput.Equals("exit", StringComparison.OrdinalIgnoreCase))
        //     // {
        //     //     appLogger.LogInformation("User requested to exit the session");
        //     //     break;
        //     // }

        //     interactionCount++;
        //     appLogger.LogInformation("Processing user interaction #{InteractionNumber}: {UserInput}", interactionCount, UserInput);

        //     // Create a child span for each individual interaction
        //     using var activity = activitySource.StartActivity("Agent Interaction");
        //     activity?
        //         .SetTag("user.input", UserInput)
        //         .SetTag("agent.name", "OpenTelemetryDemoAgent")
        //         .SetTag("interaction.number", interactionCount);

        //     var stopwatch = Stopwatch.StartNew();

        //     try
        //     {
        //         appLogger.LogDebug("Starting agent execution for interaction #{InteractionNumber}", interactionCount);
        //         Console.Write("Agent: ");

        //         // Run the agent (this will create its own internal telemetry spans)
        //         await foreach (var update in agent.RunStreamingAsync(UserInput, thread))
        //         {
        //             Console.Write(update.Text);
        //         }

        //         Console.WriteLine();

        //         stopwatch.Stop();
        //         var responseTime = stopwatch.Elapsed.TotalSeconds;

        //         // Record metrics (similar to Python example)
        //         interactionCounter.Add(1, new KeyValuePair<string, object?>("status", "success"));
        //         responseTimeHistogram.Record(responseTime,
        //             new KeyValuePair<string, object?>("status", "success"));

        //         activity?.SetTag("response.success", true);

        //         appLogger.LogInformation("Agent interaction #{InteractionNumber} completed successfully in {ResponseTime:F2} seconds",
        //             interactionCount, responseTime);
        //     }
        //     catch (Exception ex)
        //     {
        //         Console.WriteLine($"Error: {ex.Message}");
        //         Console.WriteLine();

        //         stopwatch.Stop();
        //         var responseTime = stopwatch.Elapsed.TotalSeconds;

        //         // Record error metrics
        //         interactionCounter.Add(1, new KeyValuePair<string, object?>("status", "error"));
        //         responseTimeHistogram.Record(responseTime,
        //             new KeyValuePair<string, object?>("status", "error"));

        //         activity?
        //             .SetTag("response.success", false)
        //             .SetTag("error.message", ex.Message)
        //             .SetStatus(ActivityStatusCode.Error, ex.Message);

        //         appLogger.LogError(ex, "Agent interaction #{InteractionNumber} failed after {ResponseTime:F2} seconds: {ErrorMessage}",
        //             interactionCount, responseTime, ex.Message);
        //     }
        //     // }

        //     // Add session summary to the parent span
        //     sessionActivity?
        //         .SetTag("session.total_interactions", interactionCount)
        //         .SetTag("session.end_time", DateTimeOffset.UtcNow.ToString("O"));

        //     appLogger.LogInformation("Agent session completed. Total interactions: {TotalInteractions}", interactionCount);
        // } // End of logging scope

        // appLogger.LogInformation("OpenTelemetry Aspire Demo application shutting down");
    }

    private static void ConfigureLoggingWithOTel(
        string ServiceName,
        ServiceCollection serviceCollection,
        Action<OtlpExporterOptions> configureOtlpExporterOptions)
    {
        serviceCollection.AddLogging(loggingBuilder => loggingBuilder
            .SetMinimumLevel(LogLevel.Debug)
            .AddOpenTelemetry(options =>
            {
                options.SetResourceBuilder(ResourceBuilder.CreateDefault().AddService(ServiceName, serviceVersion: "1.0.0"));
                options.AddOtlpExporter(configureOtlpExporterOptions);
                options.IncludeScopes = true;
                options.IncludeFormattedMessage = true;
            }));
    }

    private static MeterProvider BuildMeterProvider(
        string sourceName,
        string agentName,
        Action<OtlpExporterOptions> configureOtlpExporterOptions)
    {

        // Setup metrics with resource and instrument name filtering
        return Sdk.CreateMeterProviderBuilder()
            .SetResourceBuilder(ResourceBuilder.CreateDefault().AddService(agentName, serviceVersion: "1.0.0"))
            .AddMeter(sourceName) // Our custom meter
            .AddMeter("*Microsoft.Agents.AI") // Agent Framework metrics
            .AddHttpClientInstrumentation() // HTTP client metrics
            .AddRuntimeInstrumentation() // .NET runtime metrics
            .AddOtlpExporter(configureOtlpExporterOptions)
            .Build();
    }

    private static TracerProvider BuildTraceProvider(
        string sourceName,
        string agentName,
        Action<OtlpExporterOptions> configureExporterOptions)
    {
        // Setup tracing with resource
        return Sdk.CreateTracerProviderBuilder()
            .SetResourceBuilder(ResourceBuilder.CreateDefault().AddService(agentName, serviceVersion: "1.0.0"))
            .AddSource(sourceName) // Our custom activity source
            .AddSource("*Microsoft.Agents.AI") // Agent Framework telemetry
            .AddHttpClientInstrumentation() // Capture HTTP calls to OpenAI
            .AddOtlpExporter(configureExporterOptions)
            .Build();
    }

    private static Resource BuildResourceProfile(string ServiceName)
    {

        // Create a resource to identify this service
        return ResourceBuilder.CreateDefault()
            .AddService(ServiceName, serviceVersion: "1.0.0")
            .AddAttributes(new Dictionary<string, object>
            {
                ["service.instance.id"] = Environment.MachineName,
                ["deployment.environment"] = "development"
            })
            .Build();
    }
}