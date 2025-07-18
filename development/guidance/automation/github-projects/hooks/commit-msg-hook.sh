#!/bin/sh
# Commit message hook to enforce IntelForge phase-based format

commit_msg_file=$1

# Regex pattern for IntelForge phase-based commits
# Format: phase_XX: description OR docs: description OR config: description
pattern="^(phase_[0-9]+|docs|config|fix|test): .{1,72}"

if ! grep -qE "$pattern" "$commit_msg_file"; then
  echo "ERROR: Commit message does not follow IntelForge format."
  echo ""
  echo "Required format: <type>: <description>"
  echo ""
  echo "Valid types:"
  echo "  phase_XX  - Development work on phase modules (e.g., phase_01, phase_02)"
  echo "  docs      - Documentation updates"
  echo "  config    - Configuration changes"
  echo "  fix       - Bug fixes"
  echo "  test      - Testing-related changes"
  echo ""
  echo "Examples:"
  echo "  phase_01: implement reddit scraping with PRAW"
  echo "  docs: update session handover documentation"
  echo "  config: add reddit API configuration"
  echo "  fix: handle rate limiting in reddit module"
  echo ""
  echo "Please update your commit message and try again."
  exit 1
fi

exit 0
