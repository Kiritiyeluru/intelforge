Module 1: Build MCP Server
The PR Chaos at CodeCraft Studios
It’s your first week at CodeCraft Studios, and you’re witnessing something that makes every developer cringe. The team’s pull requests look like this:

“stuff”
“more changes”
“fix”
“update things”
Meanwhile, the code review backlog is growing because reviewers can’t understand what changed or why. Sarah from the backend team spent 30 minutes trying to figure out what “various improvements” actually meant, while Mike from frontend had to dig through 47 files to understand a “small fix.”

The team knows they need better PR descriptions, but everyone’s too busy shipping features to write detailed explanations. They need a solution that helps without slowing them down.

Your mission: Build an intelligent PR Agent that analyzes code changes and suggests helpful descriptions automatically.

Screencast: The PR Problem in Action 😬

What You’ll See: A real PR at CodeCraft Studios titled “various improvements” and the description simply says “Fixed some stuff and made updates”. Classic, right?

The Confusion: Watch as teammates struggle:

Sarah (3 hours ago): “What was fixed? I see changes to the User model but can’t tell if this is addressing a bug or adding features”
Jamie (3 hours ago): “There are 8 files across 4 services… are these changes related? What should I focus on during review?”
The Pain Point: The screencast shows the actual diff—8 files scattered across multiple services with zero context. Reviewers have to piece together the story themselves, wasting precious time and possibly missing critical issues.

Why This Matters: This is exactly the PR chaos your MCP server will solve! By the end of this module, you’ll turn these cryptic PRs into clear, actionable descriptions that make everyone’s life easier.

What You’ll Build
In this first module, you’ll create the foundation of CodeCraft Studios’ automation system: an MCP server that transforms how the team writes pull requests. This module focuses on core MCP concepts that you’ll build upon in Modules 2 and 3.

Screencast: Your PR Agent Saves the Day! 🚀

The Solution in Action: Watch how your MCP server will transform PR chaos into clarity:

analyze_file_changes - Grabs all the changes (453 lines across 8 files!)
get_pr_templates - Shows Claude the 7 templates to choose from
suggest_template - Claude picks “Feature” (smart choice!)
What You’ll See: Claude doesn’t just pick a template—it:

Writes a clear summary of what actually changed
Spots security issues (yikes, unhashed passwords!)
Creates a nice to-do list for follow-up work
Even prioritizes what needs fixing first
The “Wow” Moment ✨: In just seconds, your MCP server helps Claude transform the same branch into a PR that actually explains what’s going on. No more confused reviewers, no more “what does this do?” comments.

This is what you’ll build: A tool that turns PR dread into PR delight—let’s get started!

What You Will Learn
In this foundational module, you’ll master:

How to create a basic MCP server using FastMCP - The building blocks for Modules 2 and 3
Implementing MCP Tools for data retrieval and analysis - The core primitive you’ll use throughout Unit 3
Letting Claude make intelligent decisions based on raw data - A key principle for all MCP development
Testing and validating your MCP server - Essential skills for building reliable tools
Overview
Your PR Agent will solve CodeCraft Studios’ problem using a key principle of MCP development: instead of hard-coding rigid rules about what makes a good PR, you’ll provide Claude with raw git data and let it intelligently suggest appropriate descriptions.

This approach works because:

Flexible analysis: Claude can understand context that simple rules miss
Natural language: Suggestions feel human, not robotic
Adaptable: Works for any codebase or coding style
You’ll implement three essential tools that establish patterns for the entire automation system:

analyze_file_changes - Retrieves git diff information and changed files (data collection)
get_pr_templates - Lists available PR templates (resource management)
suggest_template - Allows Claude to recommend the most appropriate template (intelligent decision-making)
Getting Started
Prerequisites
Python 3.10 or higher
Git installed and a git repository to test with
uv package manager (installation guide)
Starter Code
Clone the starter code repository:

Copied
git clone https://github.com/huggingface/mcp-course.git
Navigate to the starter code directory:

Copied
cd mcp-course/projects/unit3/build-mcp-server/starter
Install dependencies:

You might want to create a virtual environment for this project:

Copied
uv venv .venv
source .venv/bin/activate # On Windows use: .venv\Scripts\activate
Copied
uv sync --all-extras
Your Task
This is your first hands-on MCP development experience! Open server.py and implement the three tools following the TODO comments. The starter code provides the basic structure - you need to:

Implement analyze_file_changes to run git commands and return diff data
⚠️ Important: You’ll likely hit a token limit error (25,000 tokens max per response)
This is a real-world constraint that teaches proper output management
See the “Handling Large Outputs” section below for the solution
⚠️ Note: Git commands will run in the MCP server’s directory by default. See “Working Directory Considerations” below for details
Implement get_pr_templates to manage and return PR templates
Implement suggest_template to map change types to templates
Don’t worry about making everything perfect - you’ll refine these skills as you progress through the unit.

Design Philosophy
Unlike traditional systems that categorize changes based on file extensions or rigid patterns, your implementation should:

Provide Claude with raw git data (diffs, file lists, statistics)
Let Claude analyze the actual code changes
Allow Claude to make intelligent template suggestions
Keep the logic simple - Claude handles the complexity
MCP Philosophy: Instead of building complex logic into your tools, provide Claude with rich data and let its intelligence make the decisions. This makes your code simpler and more flexible than traditional rule-based systems.

Testing Your Implementation
1. Validate Your Code
Run the validation script to check your implementation:

Copied
uv run python validate_starter.py
2. Run Unit Tests
Test your implementation with the provided test suite:

Copied
uv run pytest test_server.py -v
3. Test with Claude Code
Configure your server directly in Claude Code:

Copied
# Add the MCP server to Claude Code
claude mcp add pr-agent -- uv --directory /absolute/path/to/starter run server.py

# Verify the server is configured
claude mcp list
Then:

Make some changes in a git repository
Ask Claude: “Can you analyze my changes and suggest a PR template?”
Watch Claude use your tools to provide intelligent suggestions
Common first error: If you get “MCP tool response exceeds maximum allowed tokens (25000)”, this is expected! Large repositories can generate massive diffs. This is a valuable learning moment - see the “Handling Large Outputs” section for the solution.

Common Patterns
Tool Implementation Pattern
Copied

async def tool_name(param1: str, param2: bool = True) -> str:
    """Tool description for Claude.
    
    Args:
        param1: Description of parameter
        param2: Optional parameter with default
    """
    # Your implementation
    result = {"key": "value"}
    return json.dumps(result)
Error Handling
Always handle potential errors gracefully:

Copied
try:
    result = subprocess.run(["git", "diff"], capture_output=True, text=True)
    return json.dumps({"output": result.stdout})
except Exception as e:
    return json.dumps({"error": str(e)})
Error Handling: Always return valid JSON from your tools, even for errors. Claude needs structured data to understand what went wrong and provide helpful responses to users.

Handling Large Outputs (Critical Learning Moment!)
Real-world constraint: MCP tools have a token limit of 25,000 tokens per response. Large git diffs can easily exceed this limit 10x or more! This is a critical lesson for production MCP development.

When implementing analyze_file_changes, you’ll likely encounter this error:

Copied
Error: MCP tool response (262521 tokens) exceeds maximum allowed tokens (25000)
Why this happens:

A single file change can be thousands of lines
Enterprise repositories often have massive refactorings
Git diffs include full context by default
JSON encoding adds overhead
This teaches us an important principle: Always design tools with output limits in mind. Here’s the solution:

Copied

async def analyze_file_changes(base_branch: str = "main", 
                              include_diff: bool = True,
                              max_diff_lines: int = 500) -> str:
    """Analyze file changes with smart output limiting.
    
    Args:
        base_branch: Branch to compare against
        include_diff: Whether to include the actual diff
        max_diff_lines: Maximum diff lines to include (default 500)
    """
    try:
        # Get the diff
        result = subprocess.run(
            ["git", "diff", f"{base_branch}...HEAD"],
            capture_output=True, 
            text=True
        )
        
        diff_output = result.stdout
        diff_lines = diff_output.split('\n')
        
        # Smart truncation if needed
        if len(diff_lines) > max_diff_lines:
            truncated_diff = '\n'.join(diff_lines[:max_diff_lines])
            truncated_diff += f"\n\n... Output truncated. Showing {max_diff_lines} of {len(diff_lines)} lines ..."
            diff_output = truncated_diff
        
        # Get summary statistics
        stats_result = subprocess.run(
            ["git", "diff", "--stat", f"{base_branch}...HEAD"],
            capture_output=True,
            text=True
        )
        
        return json.dumps({
            "stats": stats_result.stdout,
            "total_lines": len(diff_lines),
            "diff": diff_output if include_diff else "Use include_diff=true to see diff",
            "files_changed": self._get_changed_files(base_branch)
        })
        
    except Exception as e:
        return json.dumps({"error": str(e)})
Best practices for large outputs:

Implement pagination: Break large results into pages
Add filtering options: Let users request specific files or directories
Provide summaries first: Return statistics before full content
Use progressive disclosure: Start with high-level info, allow drilling down
Set sensible defaults: Default to reasonable limits that work for most cases
Working Directory Considerations
By default, MCP servers run commands in their installation directory, not in Claude’s current working directory. This means your git commands might analyze the wrong repository!

To solve this, MCP provides roots - a way for clients to inform servers about relevant directories. Claude Code automatically provides its working directory as a root.

Here’s how to access it in your tool:

Copied

async def analyze_file_changes(...):
    # Get Claude's working directory from roots
    context = mcp.get_context()
    roots_result = await context.session.list_roots()
    
    # Extract the path from the FileUrl object
    working_dir = roots_result.roots[0].uri.path
    
    # Use it for all git commands
    result = subprocess.run(
        ["git", "diff", "--name-status"],
        capture_output=True,
        text=True,
        cwd=working_dir  # Run in Claude's directory!
    )
This ensures your tools operate on the repository Claude is actually working with, not the MCP server’s installation location.

Troubleshooting
Import errors: Ensure you’ve run uv sync

Git errors: Make sure you’re in a git repository

No output: MCP servers communicate via stdio - test with Claude Desktop

JSON errors: All tools must return valid JSON strings

Token limit exceeded: This is expected with large diffs! Implement output limiting as shown above

“Response too large” errors: Add max_diff_lines parameter or set include_diff=false

Git commands run in wrong directory: MCP servers run in their installation directory by default, not Claude’s working directory. To fix this, use MCP roots to access Claude’s current directory:

Copied
# Get Claude's working directory from roots
context = mcp.get_context()
roots_result = await context.session.list_roots()
working_dir = roots_result.roots[0].uri.path  # FileUrl object has .path property

# Use it in subprocess calls
subprocess.run(["git", "diff"], cwd=working_dir)
Claude Code automatically provides its working directory as a root, allowing your MCP server to operate in the correct location.

Next Steps
Congratulations! You’ve built your first MCP server with Tools - the foundation for everything that follows in Unit 3.

What you’ve accomplished in Module 1:
Created MCP Tools that provide Claude with structured data
Implemented the core MCP philosophy - let Claude make intelligent decisions from raw data
Built a practical PR Agent that can analyze code changes and suggest templates
Learned about real-world constraints - the 25,000 token limit and how to handle it
Established testing patterns with validation scripts and unit tests
Key patterns you can reuse:
Data collection tools that gather information from external sources
Intelligent analysis where Claude processes raw data to make decisions
Output management - truncating large responses while preserving usefulness
Error handling that returns structured JSON responses
Testing strategies for MCP server development
What to do next:
Review the solution in /projects/unit3/build-mcp-server/solution/ to see different implementation approaches
Compare your implementation with the provided solution - there’s no single “right” way to solve the problem
Test your tools thoroughly - try them with different types of code changes to see how Claude adapts
Move on to Module 2 where you’ll add real-time webhook capabilities and learn about MCP Prompts for workflow standardization
Module 2 will build directly on the server you created here, adding dynamic event handling to complement your static file analysis tools!

The story continues…
With your PR Agent working, CodeCraft Studios developers are already writing better pull requests. But next week, you’ll face a new challenge: critical CI/CD failures are slipping through unnoticed. Module 2 will add real-time monitoring to catch these issues before they reach production.
-------------------------------------------
