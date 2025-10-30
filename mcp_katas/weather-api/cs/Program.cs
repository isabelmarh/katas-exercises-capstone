
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
public static class GetWeatherInformationTool
{
    [McpServerTool(Name="Get Current Weather"), Description("Returns current temperature, conditions, humidity, wind speed for a given location")]
    public static string GetCurrentWeather(string location = "")
    {
        // TODO: Implement 
        // Hint: Use HttpClient to call https://wttr.in/{location}?format=j1
        // Return current temperature, conditions, humidity, wind speed
        //throw new NotImplementedException();

        // Use this to test connections
         return "26 degrees C, some clouds, 80% humidity, wind speed is 12 m/s";
    }

    [McpServerTool, Description("Returns the weather forecast for the requested number of days, for a given location")]
    public static string GetWeatherForecast(string location = "", int days = 1)
    {
        // TODO: Implement 
        // Hint: Parse the weather array from the API response
        // Return forecast for the requested number of days
        throw new NotImplementedException();

        // Use this to test connections
        // return $"The weather for the next {days} days is wet ";
    }
}