# Rock-Paper-Scissors-Bomb AI Game Referee

An AI-powered game referee for Rock-Paper-Scissors-Bomb, built with Google ADK (Agent Development Kit).

## Quick Start

```bash
# Install dependencies (using uv)
uv add google-adk python-dotenv

# Run the game (interactive web UI)
adk web # Default ADK WEB UI

# Or run in terminal
uv run adk run rps_plus_agent
```

## State Model

The game state is managed as a module-level dictionary in `tools.py`:

```python
game_state = {
    "current_round": 1,       # Current round (1-3)
    "user_score": 0,          # User's win count
    "bot_score": 0,           # Bot's win count
    "user_bomb_used": False,  # Has user used bomb?
    "bot_bomb_used": False,   # Has bot used bomb?
    "game_over": False,       # Is game finished?
    "game_result": None,      # Final result
    "round_history": []       # History of all rounds
}
```

**Why module-level state?** ADK tools are Python functions called by the agent. State persists naturally across function calls within the same session without needing a database.

## Agent/Tool Design

### Architecture
```
User Input → Agent (Intent Understanding) → Tools (Game Logic) → Agent (Response Generation) → User
```

### Tools Defined

| Tool | Purpose |
|------|---------|
| `play_round(user_move)` | Main orchestrator - validates move, gets bot move, resolves round, updates state |
| `get_game_state()` | Returns current game state for the agent to reference |
| `reset_game_state()` | Resets state for a new game |

### Supporting Functions (Internal)
- `validate_move()` - Checks if a move is valid and bomb usage rules
- `resolve_round()` - Determines round winner using RPS-Plus rules
- `update_game_state()` - Updates scores, round count, checks game end

### Separation of Concerns
1. **Intent Understanding**: Agent interprets what the user wants (play a move, check score, start new game)
2. **Game Logic**: Tools handle validation, resolution, and state mutation
3. **Response Generation**: Agent formats results into friendly messages

## Game Rules

- **Best of 3 rounds**
- **Valid moves**: rock, paper, scissors, bomb
- **Standard RPS**: rock→scissors→paper→rock
- **Bomb**: Beats all moves except another bomb (one use per player)
- **Invalid input**: Round is wasted

## Tradeoffs Made

1. **Single `play_round` tool vs separate tools**: Combined validation, resolution, and state update into one tool call to reduce agent complexity and token usage. Individual functions still exist for clarity.

2. **Module-level state vs class-based**: Chose simplicity over OOP since ADK tools work best as decorated functions. State persists naturally in Python's module scope.

3. **Bot uses bomb randomly (20% chance)**: Simple strategy instead of complex game theory. The bot plays fair but unpredictable.

4. **Invalid input wastes round**: As per requirements, this creates strategic tension - users must be careful with input.

## What I Would Improve With More Time

1. **Smarter bot strategy**: Track user patterns and adapt (e.g., if user often opens with bomb, wait for round 3)

2. **Session management**: Handle multiple concurrent games with user IDs

3. **Structured output schemas**: Use ADK's JSON schema support for more consistent tool responses

4. **Unit tests**: Add pytest suite for game logic edge cases

5. **Rich terminal UI**: Use `rich` library for colored output and animations

## Project Structure

```
assignment/
├── rps_plus_agent/
│   ├── __init__.py      # Package exports
│   ├── agent.py         # ADK agent definition
│   └── tools.py         # Game logic & state
├── .env                 # API key
├── requirements.txt     # Dependencies
└── README.md            # This file
```

## Requirements

- Python 3.10+
- Google API Key (Gemini)
