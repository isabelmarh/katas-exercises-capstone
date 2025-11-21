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
public static class BelgianGridInformationTools
{
    [McpServerTool, Description("Get current (near-real-time) wind production for Federal region")]
    public static async Task<decimal> GetCurrentWindProduction()
    {
        // Get instrumented agent

        throw new NotImplementedException();
    }

    [McpServerTool, Description("Get current (near-real-time) solar production for Federal region")]
    public static async Task<string> GetCurrentSolarProduction()
    {
        var uri = "https://opendata.elia.be/api/explore/v2.1/catalog/datasets/ods087/records?select=datetime%2Cregion%2Crealtime&where=region%3D%22Brussels%22%20and%20realtime%3E0";
        
        var result = await new HttpClient().GetAsync(uri);
        
        var json = await result.Content.ReadAsStringAsync();

        Console.WriteLine(json);

        return json;
    }
}

