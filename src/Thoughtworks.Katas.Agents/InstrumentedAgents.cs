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
    public static (Microsoft.Agents.AI.AIAgent, Microsoft.Extensions.AI.IChatClient, ILogger, Meter) Build<T>(
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
        Meter meter = new(agentName);
        var meterProvider = BuildMeterProvider(SourceName, agentName, otlpExporterOptions);

        // Setup structured logging with OpenTelemetry
        var serviceCollection = new ServiceCollection();
        ConfigureLoggingWithOTel(ServiceName, serviceCollection, otlpExporterOptions);
        var serviceProvider = serviceCollection.BuildServiceProvider();
        var loggerFactory = serviceProvider.GetRequiredService<ILoggerFactory>();
        var appLogger = loggerFactory.CreateLogger<T>();



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

        return (agent, instrumentedChatClient, appLogger, meter);
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
            .AddMeter(agentName)
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