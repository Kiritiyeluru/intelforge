There is an MCP movement happening right now!

New MCPs are released every day, and you may not be aware that they could be the missing link to your AI coding productivity.

If new to my content,

In the last 6 months, I have been working with MCP servers, building, monetizing, and now sharing my knowledge on MCPs daily here on Medium.

I have seen it all, but still feel left behind when I discover new MCPs that I missed out on, yet I’m on my daily grind here working with MCPs.

For example, I recently discovered Serena MCP, which is a powerful coding agent toolkit.

For regular updates on these MCPs, consider following me on Medium and subscribing to get notified when I post.

Joe Njenga - Medium
Read writing from Joe Njenga on Medium. Software & AI Automation Engineer, Tech Writer & Educator. Vision: Enlighten…
medium.com

In this list, we will cover those MCP servers and repos that have agentic features and are not common MCPs.

Let’s cut to the chase and see what’s on this list.

1. Serena MCP

Serena transforms your LLM into a fully-featured coding agent with IDE-level capabilities. What makes it different is its semantic approach to code understanding through Language Server Protocol integration.

While other MCP servers treat code as text, Serena understands the symbolic relationships, dependencies, and structure. The standout feature here is the autonomous workflow.

Serena can handle complete coding tasks from analysis to implementation, testing, and even version control commits without constant hand-holding.

Key Features
Semantic code retrieval and editing at the symbol level
30+ specialized functions including find_symbol and replace_symbol_body
Multi-language support (Python, Java, TypeScript, and more)
Intelligent onboarding with a project-specific memory system
Works with Claude Desktop’s free tier (no API costs)
Compatible with VSCode, Cursor, IntelliJ, Cline, and Roo Code
Agno framework integration for any LLM model
Execute shell commands and read terminal output
Autonomous perception-action loop for complete task execution
Serena is free and open-source, making it a solid alternative to expensive IDE subscriptions.

Git Link: https://github.com/oraios/serena

2. Zen MCP

Zen transforms Claude into a multi-AI orchestrator with seamless model switching and persistent conversation threading.

The feature I liked was the ability to coordinate different AI models within a single conversation, letting Claude automatically pick the best AI for each subtask. Claude can work between Gemini Pro’s deep analysis, O3’s logical reasoning, and Flash’s quick iterations.

For example, Claude can start a task with one model, switch to another mid-conversation, and return with full context preserved.

Key Features
Multi-AI orchestration with automatic model selection (Gemini Pro, O3, Flash)
Persistent conversation threading across model switches with a Redis backend
Intelligent model routing — Claude picks the optimal AI for each task type
Cross-tool continuation — seamlessly continue conversations across different analysis tools
Extended context handling — bypasses MCP’s 25K token limit automatically
Collaborative debugging with multiple AI perspectives on complex problems
Professional code reviews with severity-based prioritization across entire repositories
Pre-commit validation with multi-repository support and requirement checking
Thinking mode control for Gemini models (minimal to max depth)
Web search integration with a smart recommendation system
Docker-based setup with one-command installation and Redis persistence
Works with Claude Desktop and Claude Code with simple configuration
Zen is free and perfect for developers who want to use the power of multiple AI models collaboratively.

Git Link: https://github.com/BeehiveInnovations/zen-mcp-server

3. Lastmile MCP

Lastmile MCP transforms how you build AI agents by providing a production-ready framework built specifically for the Model Context Protocol.

Its implementation of every pattern from Anthropic’s “Building Effective Agents” research, combined with OpenAI’s Swarm multi-agent orchestration, sets the standard.

The framework handles all the tedious MCP server lifecycle management while giving you powerful workflow patterns like Evaluator-Optimizer, Orchestrator-Workers, and Parallel execution.

Key Features
Complete implementation of Anthropic’s Building Effective Agents patterns
Model-agnostic support (OpenAI, Anthropic, Azure, and more)
Automatic MCP server lifecycle management and connection pooling
Composable workflow patterns (Router, Parallel, Evaluator-Optimizer, Orchestrator)
OpenAI Swarm pattern implementation for multi-agent coordination
Human-in-the-loop workflows with signal handling and approval gates
Desktop integration examples: Streamlit, Marimo, and Claude:
Persistent memory and conversation context management
Durable execution with pause/resume capabilities (via Temporal integration)
MCPAggregator for server-of-servers functionality
Lastmile MCP is actively maintained by the team at LastMile AI. The extensive examples directory covers everything from basic file operations to complex multi-agent customer service workflows, making it easy to use.

Git Link : https://github.com/lastmile-ai/mcp-agent

4. Claude Code MCP Server

Claude Code MCP Server creates an “agent in your agent” by wrapping Anthropic’s Claude Code CLI into a streamlined MCP server.

What sets this apart is its ability to bypass permission interruptions and execute complex coding workflows in one shot.

Claude Code handles file operations more efficiently and cost-effectively, especially when paired with Anthropic’s pricing model.

Key Features
One-shot execution with automatic permission bypassing
Unified Claude code tool for all development operations
File system operations (create, read, edit, move, delete)
Git version control integration with commit and push capabilities
Terminal command execution and web browser automation
Multi-step workflow automation (version bumps, releases, PR creation)
GitHub integration for pull requests and CI status checking
Web search and summarization capabilities
Syntax error detection and automatic repair
Cost-effective operation through Claude Code’s pricing model
It’s valuable for developers who want to use Claude’s system-level access for tasks that other IDEs can’t handle.

Git Link: https://github.com/steipete/claude-code-mcp

Final Thoughts
Each one of these MPCs brings unique capabilities that can transform how you approach development.

My best recommendation is to pair Zen MCP with Claude Code, which makes an excellent workflow that will make you more productive.

You can also try out other combinations to see what works best for you.
