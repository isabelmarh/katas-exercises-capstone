
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
public static class CurrencyExchangeTool
{

    [McpServerTool(Name = "GetExchangeRate"), Description("Returns the exchange rate for the given currency pair")]
    public static Task<decimal> GetExchangeRate(string fromCurrency = "USD", string toCurrency = "EUR")
    {
        // TODO: Implement tool
        // Hint: Call https://open.er-api.com/v6/latest/{from_currency}
        // Extract the rate for toCurrencySymbol from the rates dict

        throw new NotImplementedException();
    }

    [McpServerTool(Name = "ConvertCurrency"), Description("Converts an amount from one currency to another")]
    public static async Task<decimal> ConvertCurrency(decimal amount = 1.00M, string fromCurrency = "USD", string toCurrency = "EUR")
    {
        // TODO: Implement tool
        // Hint: Get the exchange rate and multiply by the amount
        // Format the result nicely with 2 decimal places

        throw new NotImplementedException();
    }

    [McpServerTool(Name = "ListCurrencies"), Description("Returns the rates for all currencies paired with the provided base currency")]
    public static async Task<Dictionary<string, decimal>> ListCurrenciesForBaseCurrency(string baseCurrencySymbol = "USD")
    {
        // TODO: Implement tool
        // Note: You can return more complex types
        // Hint: Call the API with any base currency and extract all keys from rates dict
        // Hint: You may need to serialise the data

        throw new NotImplementedException();
    }

}