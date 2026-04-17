# Prep Agent — Local LLM Character Creation

Standalone agent that uses a local LLM to build PF1e characters by calling MCP tool functions directly (no MCP protocol overhead).

## Prerequisites

- llama.cpp server running with a capable model (Gemma 4 26B A4B recommended)
- The pathfinder-mcp venv (`mcp-server/.venv/`) with dependencies installed

## Usage

```bash
# Start the LLM server
~/workspace/models/serve-model.sh gemma-4-26b-a4b-it -c 32768

# Build a character (output to stdout as JSON)
cd pathfinder/agent
mcp-server/.venv/bin/python prep-agent/agent.py "reach-based combat patrol inquisitor, level 8, human"

# Build and persist to a game session
mcp-server/.venv/bin/python prep-agent/agent.py \
    --persist --session-id abc123 \
    "dwarven stonelord paladin, level 5"

# Build, persist, and render as Markdown
mcp-server/.venv/bin/python prep-agent/agent.py \
    --persist --session-id abc123 --render-md \
    "elven wizard conjurer, level 10"

# Use a different LLM endpoint
mcp-server/.venv/bin/python prep-agent/agent.py \
    --url http://localhost:11434 --model qwen3.5:14b \
    "halfling rogue, level 3"
```

## How It Works

1. Imports MCP tool functions directly from `mcp-server/server.py` as Python functions
2. Builds OpenAI-format tool schemas from function signatures
3. Sends the character concept + system prompt to the local LLM
4. The LLM iteratively calls tools (search feats, check prerequisites, look up classes, etc.)
5. Agent dispatches each tool call to the Python function and feeds results back
6. Once the LLM produces a final JSON character, the agent outputs it

Typical run: 15-25 tool calls over 2-3 minutes.

## Prompts

- `prompts/chargen.md` — Character creation system prompt
- `prompts/npc_gen.md` — NPC generation system prompt (use with `--prompt npc_gen` once supported)
