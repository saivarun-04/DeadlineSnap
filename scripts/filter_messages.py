#!/usr/bin/env python3
"""Filter git commit messages to remove Claude/Anthropic references."""
import sys

for line in sys.stdin:
    # Skip lines with Co-Authored-By mentioning Claude or Anthropic
    if "Co-Authored-By" in line and ("Claude" in line or "Anthropic" in line):
        continue
    # Skip lines with "Generated with Claude Code"
    if "Generated with" in line and "Claude" in line:
        continue
    sys.stdout.write(line)
