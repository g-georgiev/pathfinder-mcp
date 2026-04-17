"""Game state MCP tools — registered with the FastMCP server via register_all()."""


def register_all(mcp):
    """Register all game state tools with the MCP server instance."""
    from tools.session import (
        create_session, get_session, list_sessions, join_session,
        save_session, load_session,
    )
    from tools.character import persist_character, get_character, list_characters
    from tools.character_updates import (
        update_character_hp, update_character_conditions,
        update_character_inventory, update_character_spells, apply_level_up,
    )
    from tools.npc import persist_npc, get_npc, list_npcs, update_npc
    from tools.combat import (
        start_combat, get_combat_state, resolve_attack, resolve_save,
        resolve_skill_check, advance_turn, end_combat,
    )
    from tools.campaign import (
        log_event, recall_events, add_quest, update_quest, list_quests,
        add_foreshadow, get_foreshadow_threads, resolve_foreshadow,
    )
    from tools.rendering import render_character_md, import_character_md

    all_tools = [
        # Session
        create_session, get_session, list_sessions, join_session,
        save_session, load_session,
        # Character
        persist_character, get_character, list_characters,
        # Character updates
        update_character_hp, update_character_conditions,
        update_character_inventory, update_character_spells, apply_level_up,
        # NPC
        persist_npc, get_npc, list_npcs, update_npc,
        # Combat
        start_combat, get_combat_state, resolve_attack, resolve_save,
        resolve_skill_check, advance_turn, end_combat,
        # Campaign memory
        log_event, recall_events, add_quest, update_quest, list_quests,
        add_foreshadow, get_foreshadow_threads, resolve_foreshadow,
        # Rendering
        render_character_md, import_character_md,
    ]
    for fn in all_tools:
        mcp.add_tool(fn)
