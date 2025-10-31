using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using ModelContextProtocol.Server;
using System.ComponentModel;

var builder = Host.CreateApplicationBuilder(args);
builder.Logging.AddConsole(consoleLogOptions =>
{
    // Configure all logs to go to stderr
    consoleLogOptions.LogToStandardErrorThreshold = LogLevel.Trace;
});
builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithToolsFromAssembly();

await builder.Build().RunAsync();

[McpServerToolType]
public static class CarbonIntensityTool
{
    [McpServerTool, Description("Get current carbon intensity for the nation or a specific postcode (e.g. SW1A)")]
    public static async Task<decimal> GetCurrentCarbonIntensity(string? postcode)
    {
        // TODO: Implement tool
        // Hint: Call https://api.carbonintensity.org.uk/intensity for national data
        // Or https://api.carbonintensity.org.uk/regional/postcode/{postcode} for regional

        throw new NotImplementedException();
    }

    [McpServerTool, Description("Get forecast carbon intensity for the nation or a specific postcode (e.g. SW1A)")]
    public static async Task<decimal> GetForecastCarbonIntensity(string? postcode)
    {
        // TODO: Implement tool
        // Hint: Use the /intensity endpoint and parse the data array for future periods

        throw new NotImplementedException();
    }


    [McpServerTool, Description("Get current carbon intensity for the nation or a specific postcode (e.g. SW1A)")]
    public static async Task<Dictionary<string, decimal>> GetGenerationMix()
    {
        // TODO: Implement tool
        // Hint: Call https://api.carbonintensity.org.uk/generation
        // Parse the generationmix array

        throw new NotImplementedException();
    }
}

