#!/usr/bin/env python3
"""Prep agent for PF1e character creation using a local LLM.

Imports MCP tool functions directly (no MCP protocol) and drives a local LLM
through an agent loop to research, validate, and build PF1e characters.

Usage:
    python agent.py "reach-based combat patrol inquisitor, level 8, human"
    python agent.py --persist --session-id abc123 "dwarven stonelord paladin, level 5"
"""

import argparse
import inspect
import json
import re
import sys
from pathlib import Path

# Add mcp-server to path for direct imports
MCP_SERVER_DIR = str(Path(__file__).parent.parent / "mcp-server")
sys.path.insert(0, MCP_SERVER_DIR)

from llm_client import LLMClient

# Import MCP tool functions directly — no protocol overhead
from server import (
    search_feats, search_classes, search_archetypes, search_spells,
    search_races, search_equipment, search_items, search_class_options,
    get_detail, get_skills, check_feat_prerequisites, check_archetype_compatibility,
    search_guides, get_guide_index,
)
from tools.character import persist_character
from tools.rendering import render_character_md

# Tools available to the LLM during chargen
TOOL_FUNCTIONS = {
    "search_feats": search_feats,
    "search_classes": search_classes,
    "search_archetypes": search_archetypes,
    "search_spells": search_spells,
    "search_races": search_races,
    "search_equipment": search_equipment,
    "search_items": search_items,
    "search_class_options": search_class_options,
    "get_detail": get_detail,
    "get_skills": get_skills,
    "check_feat_prerequisites": check_feat_prerequisites,
    "check_archetype_compatibility": check_archetype_compatibility,
    "search_guides": search_guides,
    "get_guide_index": get_guide_index,
}


def _python_type_to_json_schema(annotation) -> dict:
    """Convert a Python type annotation to a JSON schema type."""
    if annotation is inspect.Parameter.empty or annotation is None:
        return {"type": "string"}
    if annotation is str:
        return {"type": "string"}
    if annotation is int:
        return {"type": "integer"}
    if annotation is float:
        return {"type": "number"}
    if annotation is bool:
        return {"type": "boolean"}
    if annotation is list or (hasattr(annotation, "__origin__") and annotation.__origin__ is list):
        return {"type": "array", "items": {"type": "string"}}
    if annotation is dict:
        return {"type": "object"}
    return {"type": "string"}


def build_tool_schemas(functions: dict[str, callable]) -> list[dict]:
    """Build OpenAI-format tool schemas from Python function signatures."""
    tools = []
    for name, fn in functions.items():
        sig = inspect.signature(fn)
        doc = inspect.getdoc(fn) or ""
        # Extract first line of docstring as description
        description = doc.split("\n")[0] if doc else name

        properties = {}
        required = []
        for param_name, param in sig.parameters.items():
            prop = _python_type_to_json_schema(param.annotation)
            # Extract param description from docstring Args section
            arg_match = re.search(
                rf"{param_name}:\s*(.+?)(?:\n\s*\w+:|$)",
                doc, re.DOTALL,
            )
            if arg_match:
                prop["description"] = arg_match.group(1).strip()
            properties[param_name] = prop
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        })
    return tools


def dispatch_tool_call(call: dict, functions: dict[str, callable]) -> str:
    """Execute a tool call and return the result as a JSON string."""
    fn_name = call["function"]["name"]
    if fn_name not in functions:
        return json.dumps({"error": f"Unknown tool: {fn_name}"})

    try:
        args_str = call["function"]["arguments"]
        args = json.loads(args_str) if isinstance(args_str, str) else args_str
    except (json.JSONDecodeError, TypeError):
        return json.dumps({"error": f"Failed to parse arguments for {fn_name}"})

    fn = functions[fn_name]
    try:
        result = fn(**args)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": f"{fn_name} raised: {str(e)}"})


def load_prompt(prompt_name: str = "chargen") -> str:
    """Load a system prompt from the prompts/ directory."""
    prompt_path = Path(__file__).parent / "prompts" / f"{prompt_name}.md"
    if not prompt_path.exists():
        print(f"Warning: prompt file {prompt_path} not found, using default")
        return "You are a Pathfinder 1st Edition character creation assistant."
    return prompt_path.read_text()


def run_agent(
    concept: str,
    llm: LLMClient,
    prompt_name: str = "chargen",
    max_iterations: int = 40,
    verbose: bool = True,
) -> dict:
    """Run the chargen agent loop.

    The LLM researches and builds a character through iterative tool calls,
    then outputs the final character as structured JSON.

    Args:
        concept: Natural language description of the desired character.
        llm: LLM client instance.
        prompt_name: Which system prompt to use.
        max_iterations: Safety limit on agent loop iterations.
        verbose: Print progress to stderr.

    Returns:
        Dict with the character data, or {"error": "..."} on failure.
    """
    system_prompt = load_prompt(prompt_name)
    tools = build_tool_schemas(TOOL_FUNCTIONS)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": concept},
    ]

    for i in range(max_iterations):
        if verbose:
            print(f"\n--- Iteration {i + 1} ---", file=sys.stderr)

        response = llm.chat(messages, tools=tools)

        # If model produced text, add it to conversation
        if response.text:
            if verbose:
                # Show a preview
                preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"LLM: {preview}", file=sys.stderr)

        # If model made tool calls, execute them
        if response.tool_calls:
            # Add the assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": response.text,
                "tool_calls": response.tool_calls,
            })

            for call in response.tool_calls:
                fn_name = call["function"]["name"]
                if verbose:
                    args = call["function"].get("arguments", "{}")
                    print(f"  Tool: {fn_name}({args[:100]}...)" if len(str(args)) > 100
                          else f"  Tool: {fn_name}({args})", file=sys.stderr)

                result = dispatch_tool_call(call, TOOL_FUNCTIONS)

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.get("id", f"call_{i}"),
                    "content": result,
                })

            continue  # Let the LLM process tool results

        # No tool calls — model is done. Try to extract character JSON.
        if response.text and not response.tool_calls:
            messages.append({"role": "assistant", "content": response.text})

            # Try to extract JSON from the response
            char_data = _extract_character_json(response.text)
            if char_data:
                if verbose:
                    print(f"\nCharacter extracted: {char_data.get('name', 'Unknown')}", file=sys.stderr)
                return char_data

            # If no JSON found, ask the model to output it
            if i < max_iterations - 1:
                messages.append({
                    "role": "user",
                    "content": (
                        "Please output the final character as a JSON object matching the "
                        "persist_character schema. Wrap it in ```json ... ``` code blocks."
                    ),
                })
                continue

    return {"error": "Max iterations reached without producing a character"}


def _extract_character_json(text: str) -> dict | None:
    """Try to extract a character JSON object from LLM output."""
    # Try code-fenced JSON first
    json_match = re.search(r"```json\s*\n(.*?)\n```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding a raw JSON object with "name" key
    brace_match = re.search(r'\{[^{}]*"name"[^{}]*\{.*\}.*\}', text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def main():
    parser = argparse.ArgumentParser(
        description="PF1e character creation agent powered by a local LLM",
    )
    parser.add_argument(
        "concept",
        help="Character concept description (e.g., 'dwarven stonelord paladin, level 5')",
    )
    parser.add_argument(
        "--url", default="http://localhost:8080",
        help="LLM server URL (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--model", default="gemma-4-26b-a4b",
        help="Model name for the API (default: gemma-4-26b-a4b)",
    )
    parser.add_argument(
        "--persist", action="store_true",
        help="Persist the character to game_state.db after creation",
    )
    parser.add_argument(
        "--session-id", default="",
        help="Session ID for persistence (required with --persist)",
    )
    parser.add_argument(
        "--player-id", default="",
        help="Player ID for persistence",
    )
    parser.add_argument(
        "--render-md", action="store_true",
        help="Also render the character as FORMAT.md-spec Markdown",
    )
    parser.add_argument(
        "--max-iterations", type=int, default=40,
        help="Max agent loop iterations (default: 40)",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="Suppress progress output",
    )

    args = parser.parse_args()

    llm = LLMClient(base_url=args.url, model=args.model)

    print(f"Building character: {args.concept}", file=sys.stderr)
    print(f"LLM: {args.url} ({args.model})", file=sys.stderr)
    print("", file=sys.stderr)

    result = run_agent(
        concept=args.concept,
        llm=llm,
        verbose=not args.quiet,
        max_iterations=args.max_iterations,
    )

    if "error" in result:
        print(f"\nError: {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Output the character JSON to stdout
    print(json.dumps(result, indent=2))

    # Optionally persist
    if args.persist:
        if not args.session_id:
            print("\nError: --session-id required with --persist", file=sys.stderr)
            sys.exit(1)
        persisted = persist_character(args.session_id, args.player_id, result)
        if "error" in persisted:
            print(f"\nPersist error: {persisted['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"\nPersisted as: {persisted['character_id']}", file=sys.stderr)

        # Optionally render
        if args.render_md:
            md = render_character_md(args.session_id, persisted["character_id"])
            if isinstance(md, str):
                md_path = Path(f"{persisted['character_id']}.md")
                md_path.write_text(md)
                print(f"Rendered to: {md_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
