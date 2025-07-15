How I’m Using Claude Code Hooks (Newest Feature) To Fully Automate My Workflow
Joe Njenga
Joe Njenga

Following
9 min read
·
1 day ago
17







Claude Code Hooks — Featured Image / By Author
Claude Code has introduced hooks that now automate your development workflow in a way similar to using triggers.

I have just tested it with my custom script, and it’s mind-blowing how it integrates into your coding process, automatically executing your preferred commands.

Claude Code hooks are user-defined shell commands that execute at various points in Claude Code’s lifecycle.

This feature provides control over Claude Code’s behavior, ensuring certain actions always happen rather than relying on the LLM to choose to run them.

Claude Code Hooks
If you are not a premium member, you can read the story here, but also consider supporting by following me here on Medium and my YouTube channel to learn more about Claude Code

Hooks can be configured to run at four key points:

PreToolUse — before tool execution
PostToolUse — after successful tool completion
Notification — when notifications are sent
Stop — when Claude finishes responding
Each hook can target specific tools through matcher patterns and execute custom shell commands with full user permissions.

In this article, I will take you through how hooks work, share a practical example you can implement immediately, and demonstrate the configuration options available for automating your development workflow.

Understanding the Four Hook Types
Now let’s break down each hook type.

PreToolUse Hooks
PreToolUse hooks run before Claude executes any tool. This is your quality control checkpoint. These hooks are your first line of defense. They can validate inputs, check permissions, or completely block dangerous operations.

Use Cases

Block edits to production configuration files
Validate code syntax before Claude writes it
Check if required dependencies exist
Enforce naming conventions
When a PreToolUse hook exits with code 2, it stops Claude. The hook can send feedback directly to Claude about what went wrong, and Claude will adjust and try again.

PostToolUse Hooks
PostToolUse hooks run immediately after Claude completes a tool operation. This is where you can format code, run tests, and make documentation updates.

Use Cases

Auto-format code with Prettier or Black
Run relevant tests after file changes
Generate documentation from code comments
Log changes for compliance tracking
PostToolUse hooks can provide feedback to Claude about what just happened. If your tests fail, Claude can see the results and fix the issues.

Notification Hooks
Notification hooks trigger when Claude sends you notifications, such as asking for permission or reporting task completion. Don’t like Claude’s default notifications? Replace them entirely.

Use Cases

Send Slack messages to your team channel
Email reports to the team
Desktop notifications with custom styling
Integration with monitoring systems
You can suppress Claude’s default notifications and implement your system that fits your workflow.

Stop Hooks
Stop hooks run when Claude finishes responding and is about to stop. This can be used to trigger the next steps automatically.

Use Cases

Automatically deploy after successful tests
Trigger CI/CD pipelines
Generate reports and summaries
Start related tasks
Stop hooks can prevent Claude from stopping by returning the right exit code. This lets you build complex, multi-step workflows.

Now that we understand the different types of hooks, let's create our first hook.

Creating Your First Claude Code Hook
Hooks Claude Code Screenshot
Hooks Claude Code Screenshot
Let’s create your first hook. We’ll use the bash command logging example from the documentation.

This hook will log every shell command that Claude runs to a file. Perfect for debugging or compliance tracking.

Requirements
Before we start, make sure you have jq installed it. It's a command-line JSON processor.

Install jq:

Mac: brew install jq
Ubuntu: sudo apt install jq
Windows: Download from https://jqlang.github.io/jq/
WSL Installation: When you try to install directly, if you are using WSL, it will not work from the Claude terminal.

Instead, run this command from a new terminal window :

Claude Code Hooks
Open your WSL terminal and run

sudo apt update && sudo apt install jq
Note: You may have to restart Claude Code.

Before starting, ensure you have the latest version of Claude Code. You can update it by running the command clause update; it may require you to upgrade some dependencies and follow the update steps.

Claude Code Hooks
Step 1: Open the Hooks Configuration
In Claude Code, run the /hooks command.

This opens the hooks configuration interface. Select PreToolUse from the hook events list.

Claude Code Hooks
We’re using PreToolUse because we want to log commands before they execute.

Step 2: Add a Matcher
Click + Add new matcher…

Claude Code Hooks
Type Bash as the matcher.

Claude Code Hooks
This tells the hook to only run when Claude uses the Bash tool (shell commands). We don’t want to log file edits or other operations.

Step 3: Create the Hook Command
Click + Add new hook… and enter this command:

jq -r '"\(.tool_input.command) - \(.tool_input.description // "No description")"' >> ~/.claude/bash-command-log.txt
Claude Code Hooks
What the Code Does
jq -r processes the JSON input and outputs raw text
\(.tool_input.command) extracts the actual command
\(.tool_input.description // "No description") gets the description or defaults to "No description"
>> ~/.claude/bash-command-log.txt appends the result to a log file
Step 4: Save Your Configuration
For storage location, select User settings. This makes the hook apply to all your projects.

Claude Code Hooks
Press Esc until you return to the REPL. Your hook is now active!

Claude Code Hooks
You can confirm if the tool has been added to the server

Claude Code Hooks
Step 5: Test It Out
Ask Claude to run a simple command:

“List the files in the current directory.”

Claude will execute ls and your hook will log it to ~/.claude/bash-command-log.txt.

Check the log file:

cat ~/.claude/bash-command-log.txt
Understanding the Configuration
Your hook is now saved in ~/.claude/settings.json. Here's what it looks like:

Claude Code Hooks
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '\"\\(.tool_input.command) - \\(.tool_input.description // \"No description\")\"' >> ~/.claude/bash-command-log.txt"
          }
        ]
      }
    ]
  }
}
"PreToolUse" - The hook event type
"matcher": "Bash" - Only trigger for Bash commands
"type": "command" - Execute a shell command
The actual command with escaped quotes
Now you have a working hook! Every bash command Claude runs gets logged automatically.

Claude Code PreUseTool Hook Example: Automatic Code Quality Enforcement
For a practical use case of Claude Code hooks, we can create a hook that automatically runs ESLint on JavaScript files and blocks the operation if there are errors:

Note: I’m implementing this in WSL, where I am running the Claude Code installation but, the steps will be similar for the other setups — Maybe I should do the Mac too — let me know in comments!

Step 1: Create the validation script (~/scripts/eslint-validator.py)
Claude Code Hooks
I have created the two files for the two scripts we will be testing the Claude Code hooks.

(~/scripts/eslint-validator.py) we will add the following code :

#!/usr/bin/env python3
import json
import sys
import subprocess
import os

def main():
    try:
        # Read hook input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        
        # Only process JavaScript/TypeScript files
        if not file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            sys.exit(0)  # Success, but do nothing
            
        # Check if file exists and run ESLint
        if os.path.exists(file_path):
            result = subprocess.run(
                ['npx', 'eslint', file_path, '--format', 'json'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Parse ESLint output
                try:
                    lint_results = json.loads(result.stdout)
                    if lint_results and lint_results[0].get('messages'):
                        errors = [msg for msg in lint_results[0]['messages'] 
                                if msg['severity'] == 2]
                        if errors:
                            error_summary = f"ESLint found {len(errors)} error(s) in {file_path}:\n"
                            for error in errors[:3]:  # Show first 3 errors
                                error_summary += f"  Line {error['line']}: {error['message']}\n"
                            print(error_summary, file=sys.stderr)
                            sys.exit(2)  # Block the operation
                except json.JSONDecodeError:
                    pass
                    
        sys.exit(0)  # Success
        
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(1)  # Non-blocking error

if __name__ == "__main__":
    main()
Step 2: Configure the hook in Claude Code
Claude Code Hooks
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/scripts/eslint-validator.py"
          }
        ]
      }
    ]
  }
}
What Hook Does:

Claude Code Hooks
Before Claude writes or edits any file, the hook runs — It's a PreToolUse hook
If it’s a JavaScript/TypeScript file, ESLint validates the code
If there are errors, the hook blocks the operation and tells Claude what’s wrong
Claude then fixes the issues and tries again
Claude Code Hooks
Delete a Hook
You can also select the hook and delete it when you no longer need it :


Claude Code PostUseHook Example: Smart Documentation Generator
I created this example of a post-use hook that automatically generates documentation when certain files are modified:

The Documentation Hook (~/scripts/doc-generator.sh) this file I created in the step above, and you can add the code and test the hook:

#!/bin/bash

# Read JSON input
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
tool_name=$(echo "$input" | jq -r '.tool_name // empty')

# Only process API files
if [[ "$file_path" =~ \.(py|js|ts)$ ]] && [[ "$file_path" =~ (api|service|controller) ]]; then
    
    # Generate documentation
    doc_file="${file_path%.*}.md"
    
    echo "Generating documentation for $file_path..."
    
    # Use a documentation tool (example with a Python script)
    if [[ "$file_path" =~ \.py$ ]]; then
        python3 ~/scripts/py-to-docs.py "$file_path" > "$doc_file"
    elif [[ "$file_path" =~ \.(js|ts)$ ]]; then
        npx jsdoc2md "$file_path" > "$doc_file"
    fi
    
    # Return success with feedback
    cat << EOF
{
    "suppressOutput": false,
    "continue": true
}
EOF
    
    echo "Documentation generated: $doc_file" >&2
fi
Configuration for the documentation hook:
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command", 
            "command": "~/scripts/doc-generator.sh"
          }
        ]
      }
    ]
  }
}
Hook Configuration Hierarchy
Hooks can be configured at different levels:

User settings (~/.claude/settings.json) - Apply to all projects
Project settings (.claude/settings.json) - Apply to current project
Local settings (.claude/settings.local.json) - Local overrides, not committed
Enterprise policies — Managed by your organization
Security Considerations
Important: Hooks run with your full user permissions automatically. Always:

Validate and sanitize inputs
Use absolute paths for scripts
Quote shell variables properly: "$VAR" not $VAR
Test hooks in safe environments first
Avoid processing sensitive files (.env, .git/, keys)
Final Thoughts
I see a lot of potential in how we can now use Claude Code with these hooks to improve the workflow automation.

This feature transforms how Claude Code works by embedding your preferences directly into Claude’s decision-making process.

I recommend starting with simple command logging or basic file validation, then moving to more complex workflows that enforce your coding standards.

The potential is huge from automatic code formatting and testing to deployment triggers and team notifications.