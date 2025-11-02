using System.ClientModel;
using Microsoft.Agents.AI;
using OpenAI;

AIAgent agent = new OpenAIClient(
    new ApiKeyCredential("no-key-required"),
    new OpenAIClientOptions()
    {
        Endpoint = new Uri("http://localhost:1234/v1")
    }
)
.GetChatClient("gpt-oss-20b")
.CreateAIAgent(instructions: "You are a great researcher and will attempt to help the user find their answers", name: "ResearchBot");

do
{
    Console.Write("Enter your message or 'exit' to quit: ");
    var prompt = Console.ReadLine();

    if (prompt == "exit") break;
    if (string.IsNullOrWhiteSpace(prompt)) continue;

    // Invoke the agent and output the text result.
    Console.WriteLine(await agent.RunAsync(prompt));

} while (true);
