"""This module implements the game state management and logic as ADK tools.
State is managed as a module-level dictionary to persist across turns.
"""
import random
from typing import Literal

# Valid moves in the game
VALID_MOVES = {"rock", "paper", "scissors", "bomb"}

# Win conditions: key beats values
BEATS = {
    "rock": ["scissors"],
    "paper": ["rock"],
    "scissors": ["paper"],
    "bomb": ["rock", "paper", "scissors"]  # bomb beats all except bomb
}

# Global game state - persists across function calls
game_state = {
    "current_round": 1,
    "max_rounds": 3,
    "user_score": 0,
    "bot_score": 0,
    "user_bomb_used": False,
    "bot_bomb_used": False,
    "game_over": False,
    "game_result": None,
    "round_history": []
}


def reset_game_state() -> dict:
    
    # Reset the game state for a new game.
    
    global game_state
    game_state = {
        "current_round": 1,
        "max_rounds": 3,
        "user_score": 0,
        "bot_score": 0,
        "user_bomb_used": False,
        "bot_bomb_used": False,
        "game_over": False,
        "game_result": None,
        "round_history": []
    }
    return game_state


def get_game_state() -> dict:
    # Get the current game state.
    return game_state.copy()


def validate_move(move: str, player: Literal["user", "bot"]) -> dict:
    """
    Validate a move for a player, checking if it's legal.
    
    Args:
        move: The move to validate (rock, paper, scissors, or bomb).
        player: Who is making the move - either "user" or "bot".
        
    Returns:
        dict: Validation result with 'valid' boolean and 'reason' string.
    """
    move_lower = move.lower().strip()
    
    # Check if game is already over
    if game_state["game_over"]:
        return {
            "valid": False,
            "reason": "Game is already over. Start a new game to play again.",
            "move": move_lower
        }
    
    # Check if move is in valid moves set
    if move_lower not in VALID_MOVES:
        return {
            "valid": False,
            "reason": f"Invalid move '{move}'. Valid moves are: rock, paper, scissors, bomb.",
            "move": move_lower
        }
    
    # Check bomb usage
    if move_lower == "bomb":
        bomb_used_key = f"{player}_bomb_used"
        if game_state[bomb_used_key]:
            return {
                "valid": False,
                "reason": f"{'You have' if player == 'user' else 'Bot has'} already used the bomb this game. Choose rock, paper, or scissors.",
                "move": move_lower
            }
    
    return {
        "valid": True,
        "reason": "Valid move.",
        "move": move_lower
    }


def get_bot_move() -> str:
    """
    Generate a random move for the bot, respecting bomb usage rules.
    
    Returns:
        str: The bot's chosen move.
    """
    available_moves = ["rock", "paper", "scissors"]
    
    # Bot can use bomb if not already used (with some probability)
    if not game_state["bot_bomb_used"]:
        # 20% chance to use bomb if available
        if random.random() < 0.2:
            return "bomb"
    
    return random.choice(available_moves)


def resolve_round(user_move: str, bot_move: str) -> dict:
    """
    Determine the winner of a round based on moves played.
    
    Args:
        user_move: The user's move (must be validated first).
        bot_move: The bot's move.
        
    Returns:
        dict: Round result with winner, moves, and explanation.
    """
    user_move = user_move.lower().strip()
    bot_move = bot_move.lower().strip()
    
    # Determine winner
    if user_move == bot_move:
        winner = "draw"
        explanation = f"Both played {user_move}. It's a draw!"
    elif bot_move in BEATS.get(user_move, []):
        winner = "user"
        explanation = f"{user_move.capitalize()} beats {bot_move}. You win this round!"
    else:
        winner = "bot"
        explanation = f"{bot_move.capitalize()} beats {user_move}. Bot wins this round!"
    
    return {
        "user_move": user_move,
        "bot_move": bot_move,
        "winner": winner,
        "explanation": explanation,
        "round": game_state["current_round"]
    }


def update_game_state(user_move: str, bot_move: str, round_winner: Literal["user", "bot", "draw"]) -> dict:
    """
    Update the game state after a round is played.
    
    Args:
        user_move: The user's move that was played.
        bot_move: The bot's move that was played.
        round_winner: Who won the round - "user", "bot", or "draw".
        
    Returns:
        dict: Updated game state with new scores and status.
    """
    global game_state
    
    # Track bomb usage
    if user_move.lower() == "bomb":
        game_state["user_bomb_used"] = True
    if bot_move.lower() == "bomb":
        game_state["bot_bomb_used"] = True
    
    # Update scores
    if round_winner == "user":
        game_state["user_score"] += 1
    elif round_winner == "bot":
        game_state["bot_score"] += 1
    # Draw doesn't change scores
    
    # Record round history
    game_state["round_history"].append({
        "round": game_state["current_round"],
        "user_move": user_move,
        "bot_move": bot_move,
        "winner": round_winner
    })
    
    # Check if game should end (after 3 rounds)
    if game_state["current_round"] >= game_state["max_rounds"]:
        game_state["game_over"] = True
        
        # Determine final result
        if game_state["user_score"] > game_state["bot_score"]:
            game_state["game_result"] = "user_wins"
        elif game_state["bot_score"] > game_state["user_score"]:
            game_state["game_result"] = "bot_wins"
        else:
            game_state["game_result"] = "draw"
    else:
        # Move to next round
        game_state["current_round"] += 1
    
    return game_state.copy()


def play_round(user_move: str) -> dict:
    """
    Play a complete round: validate user move, get bot move, resolve, and update state.
    This is the main tool that orchestrates a round of the game.
    """
    # Check if game is over
    if game_state["game_over"]:
        return {
            "success": False,
            "error": "Game is already over!",
            "final_result": game_state["game_result"],
            "user_score": game_state["user_score"],
            "bot_score": game_state["bot_score"],
            "message": "Start a new game to play again."
        }
    
    # Validate user's move
    validation = validate_move(user_move, "user")
    if not validation["valid"]:
        # Invalid move wastes the round
        round_num = game_state["current_round"]
        game_state["current_round"] += 1
        game_state["round_history"].append({
            "round": round_num,
            "user_move": user_move,
            "bot_move": None,
            "winner": "invalid",
            "reason": validation["reason"]
        })
        
        # Check if this was the last round
        if game_state["current_round"] > game_state["max_rounds"]:
            game_state["game_over"] = True
            if game_state["user_score"] > game_state["bot_score"]:
                game_state["game_result"] = "user_wins"
            elif game_state["bot_score"] > game_state["user_score"]:
                game_state["game_result"] = "bot_wins"
            else:
                game_state["game_result"] = "draw"
        
        return {
            "success": False,
            "error": validation["reason"],
            "round": round_num,
            "round_wasted": True,
            "current_round": game_state["current_round"],
            "game_over": game_state["game_over"],
            "user_score": game_state["user_score"],
            "bot_score": game_state["bot_score"]
        }
    
    # Get bot's move
    bot_move = get_bot_move()
    
    # Mark bomb as used if bot uses it
    if bot_move == "bomb":
        game_state["bot_bomb_used"] = True
    
    # Resolve the round
    round_result = resolve_round(validation["move"], bot_move)
    
    # Update game state
    updated_state = update_game_state(
        validation["move"], 
        bot_move, 
        round_result["winner"]
    )
    
    return {
        "success": True,
        "round": round_result["round"],
        "user_move": round_result["user_move"],
        "bot_move": round_result["bot_move"],
        "round_winner": round_result["winner"],
        "explanation": round_result["explanation"],
        "user_score": updated_state["user_score"],
        "bot_score": updated_state["bot_score"],
        "game_over": updated_state["game_over"],
        "game_result": updated_state["game_result"],
        "next_round": updated_state["current_round"] if not updated_state["game_over"] else None
    }
