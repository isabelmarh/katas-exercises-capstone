using ModelContextProtocol.Server;
using System.ComponentModel;

var builder = WebApplication.CreateBuilder(args);
builder.Logging.AddConsole(consoleLogOptions =>
{
    // Configure all logs to go to stderr
    consoleLogOptions.LogToStandardErrorThreshold = LogLevel.Trace;
});
builder.Services
    .AddMcpServer()
    .WithHttpTransport()
    // For StdIO, comment out the above line and uncomment the line below
    // .WithStdioServerTransport()
    .WithToolsFromAssembly();

// For Stdio
// await builder.Build().RunAsync();

// For HTTP transport
var app = builder.Build();
app.MapMcp();
app.Run("http://localhost:3001");

[McpServerToolType]
public static class GetCurrentWeatherTool
{
    [McpServerTool, Description("Returns current temperature, conditions, humidity, wind speed for a given location")]
    public static string GetCurrentWeather(string location = "")
    {
        // TODO: Implement 
        // Hint: Use httpx to call https://wttr.in/{location}?format=j1
        // Return current temperature, conditions, humidity, wind speed
        throw new NotImplementedException();
    }
}

[McpServerToolType]
public static class GetWeatherForecastTool
{
    [McpServerTool, Description("Returns the weather forecast for the requested number of days, for a given location")]
    public static string GetWeatherForecast(string location = "", int days = 1)
    {
        // TODO: Implement 
        // Hint: Parse the weather array from the API response
        // Return forecast for the requested number of days
        throw new NotImplementedException();
    }
}