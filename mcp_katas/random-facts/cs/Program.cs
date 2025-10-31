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
public static class GetRandomFactsTool
{
    [McpServerTool, Description("Get a random fact about cats")]
    public static async Task<string> GetCatFact()
    {
        // TODO: Implement tool
        // Hint: Call https://catfact.ninja/fact and extract the 'fact' field
        // Return with a fun emoji prefix

        throw new NotImplementedException();
    }

    [McpServerTool, Description("Get a useless fact")]
    public static async Task<string> GetUselessFact()
    {
        // TODO: Implement tool  
        // Hint: Call https://uselessfacts.jsph.pl/api/v2/facts/random
        // Extract the 'text' field

        throw new NotImplementedException();
    }

    [McpServerTool, Description("Get a joke")]
    public static async Task<string> GetJoke()
    {
        // TODO: Implement tool
        // Hint: Call https://official-joke-api.appspot.com/random_joke
        // Format with setup and punchline

        throw new NotImplementedException();
    }

    [McpServerTool, Description("Get a quote")]
    public static async Task<string> GetQuote()
    {
        // TODO: Implement tool
        // Hint: Call https://zenquotes.io/api/random
        // Extract quote "q" and author "q" fields

        throw new NotImplementedException();
    }
}