using System.ClientModel;
using System.Diagnostics;
using System.Linq;
using System.Text.RegularExpressions;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.AI.Evaluation;
using Microsoft.Extensions.AI.Evaluation.Quality;
using OpenAI;
using Thoughtworks.Katas.Agents;

await new CodeReviewAgent().GivenCodeWithASqlInjectionVulnerability_WhenTheAgentIsAskedToReviewIt_TheAgentFlagsTheVulnerability();

public class CodeReviewAgent
{
    private static string AgentName = nameof(CodeReviewAgent);
    private static readonly ActivitySource AgentActivitySource = new ActivitySource(AgentName);

    private const string AgentInstructions = """

        You are an experienced, detail-oriented code reviewer. Analyze the code provided and 
        offer constructive review feedback. Focus on identifying issues and providing actionable
        suggestions.

        Code issues to check for:
        - Security vulnerabilities (SQL injection, XSS, etc.)
        - Performance issues (N+1 queries, inefficient algorithms)
        - Code quality (naming, complexity, code duplication)
        - Best practices for the language/framework
        - Potential bugs or edge cases
        - Error handling and logging
        - Testing considerations (testability)

        Review guidelines:
        - Be constructive and specific
        - Suggest concrete improvements
        - Explain the "why" behind suggestions
        - Highlight both issues and good practices
        - Consider maintainability and readability
        - Provide feedback with specific line comments and suggestions
    """;  

    [Fact]
    public async Task GivenCodeWithASqlInjectionVulnerability_WhenTheAgentIsAskedToReviewIt_TheAgentFlagsTheVulnerability()
    {
        // Arrange
        var codeToReview = @"public User GetUser(string userId)
        {
            return connection.Query<User>($""SELECT * FROM users WHERE id = {userId}"")
            .FirstOrDefault();
        }";
        
        var evaluationSuccessMeans = "Review should identify SQL injection vulnerability and suggest parameterized queries.";

        // Act
        var metric = await ReviewCode(codeToReview, evaluationSuccessMeans);

        // Assert
        PerformStandardMetricAssertions(metric);
    }

    [Fact]
    public async Task GivenCodeWithPerformanceIssues_WhenTheAgentIsAskedToReviewIt_TheAgentFlagsTheIssues()
    {
        // Code review for performance issues (N+1 queries, inefficient algorithms)

        // Arrange
        var codeToReview = """
            public Dictionary<UserId, IEnumerable<Post>> GetUserPosts(IEnumerable<UserId> userIds)
            {
                var userPosts = new Dictionary<UserId, IEnumerable<Post>>();
                foreach(UserId userId in userIds)
                {
                    var posts = connection.Query<Post>("SELECT * FROM posts WHERE user_id = ?", userId);
                    userPosts.Add(userId, posts);
                }
            }
        """;

        var evaluationSuccessMeans = "Review should identify N+1 query problem and suggest batching or JOIN";

        // Act
        var metric = await ReviewCode(codeToReview, evaluationSuccessMeans);

        // Assert
        PerformStandardMetricAssertions(metric);
    }

    [Fact]
    public async Task GivenCodeWithMissingErrorHandling_WhenTheAgentIsAskedToReviewIt_TheAgentFlagsTheIssues()
    {
        // Code review for code quality (naming, complexity, duplication)

        var codeToReview = """
            public async Task<string> ProcessPayment(decimal amount, string cardToken)
            {
                var charge = stripe.Charge.Process(
                    amount: amount,
                    currency: 'usd',
                    source: card_token);

                return charge.id;
            }
        """;

        var evaluationSuccessMeans = "Review should identify missing error handling for payment processing and suggest try/catch";

                // Act
        var metric = await ReviewCode(codeToReview, evaluationSuccessMeans);

        // Assert
        PerformStandardMetricAssertions(metric);
    }

    [Fact]
    public async Task GivenCodeWithDuplication_WhenTheAgentIsAskedToReviewIt_TheAgentFlagsTheIssues()
    {
        var codeToReview = """
            public static decimal CalculateTaxUS(decimal amount)
            {
                var baseRate = 0.08M;
                var destateRate = 0.02M;
                return amount * (baseRate + stateRate);
            }

            public static decimal CalculateTaxCanada(decimal amount)
            {
                var baseRate = 0.05M;
                var stateRate = 0.03M;
                return amount * (baseRate + stateRate);
            }
        """;

        var evaluationSuccessMeans = "Review should identify code duplication and suggest extracting common tax calculation logic";

        // Act
        var metric = await ReviewCode(codeToReview, evaluationSuccessMeans);

        // Assert
        PerformStandardMetricAssertions(metric);
    }

    public async Task GivenCodeWithPoorPractices_WhenTheAgentIsAskedToReviewIt_TheAgentFlagsTheIssues()
    {
        var codeToReview = """
            public User CreateUser(string email, string name)
            {
                // Create a new user with validation
                if(!email.Contains("@")
                    throw InvalidArgumentException("Invalid email address");
     
                // Check to see if user already exists
                var existingUser = Users.GetByEmailAddress(email);
                if(existingUser != null)
                    throw UserAlreadyExistsException();

                var user = Users.Create(
                    email: email.ToLower().Trim(),
                    name: name.Trim());

                logger.LogInformation($"Created user {user.id} with email {email}");

                return user;
            }
        """;

        var evaluationSuccessMeans = "Review should recognize good practices like input validation, logging, and type hints";

        // Act
        var metric = await ReviewCode(codeToReview, evaluationSuccessMeans);

        // Assert
        PerformStandardMetricAssertions(metric);
    }

    /// <summary>
    /// Performs the standard Microsoft-recommended assertions on EvaluationMetrics
    /// </summary>
    /// <param name="metric">The evaluation metric to assert against</param>
    private static void PerformStandardMetricAssertions(EvaluationMetric metric)
    {
        // These are the standard assertions for 
        // Microsoft.Extensions.AI.Evaluation evaluators:

        // 1. Check that the evaluation didn't fail
        Assert.False(metric.Interpretation!.Failed,
            $"Evaluation failed: {metric.Reason}");

        // 2. Check the rating (should be Exceptional, 
        // but loosen as required)
        Assert.True(metric.Interpretation.Rating is
            // Loosen the eval: EvaluationRating.Good or
            EvaluationRating.Exceptional,
            $"Unexpected rating: {metric.Interpretation.Rating}. Reason: {metric.Reason}");

        // Optional: Check for diagnostice errors (may contain parsing issues with local LLM)
        Assert.False(metric.ContainsDiagnostics((EvaluationDiagnostic diagnostic) =>
        {
            return diagnostic.Severity == EvaluationDiagnosticSeverity.Error;
        }),
        "Evaluation errors occurred");
    }

    /// <summary>
    /// Reviews a code snippet and returns an evaluation metric
    /// </summary>
    /// <param name="codeToReview">The code snippet to review</param>
    /// <param name="evaluationSuccessMeans">The types of issues flagged if the agent reviewed the code as expected.</param>
    /// <returns>An evaluation metric which can be asserted against</returns>
    private async Task<EvaluationMetric> ReviewCode(
        string codeToReview,
        string evaluationSuccessMeans)
    {

        var (agent, chatClient, logger, meter) = InstrumentedAgents.Build<CodeReviewAgent>(
                agentName: AgentName,
                instructions: AgentInstructions,
                model: "unsloth/gpt-oss-20b",
                openAiApiKey: "no-key-needed",
                activitySource: AgentActivitySource);

        // START KATA (remove for workshops)

        // Wrap the code to be reviewed in a ChatMessage
        var message = new ChatMessage(ChatRole.User, codeToReview);

        // Send the chat prompt and get the response
        var agentResponse = await agent.RunAsync(message);

        Console.WriteLine($"Agent response: {agentResponse}");

        var evaluator = new CompletenessEvaluator();
        var evaluatorContext = new CompletenessEvaluatorContext(evaluationSuccessMeans);

        // EvaluateAsync with ground truth context (passed as a collection)
        EvaluationResult result = await evaluator.EvaluateAsync(
            message,
            agentResponse.AsChatResponse(),
            new ChatConfiguration(chatClient),
            [evaluatorContext]
        );

        var metric = result.Get<NumericMetric>(CompletenessEvaluator.CompletenessMetricName);

        return metric;

        // END KATA
    }

}