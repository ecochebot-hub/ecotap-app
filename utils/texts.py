# utils/texts.py

def format_welcome_message(user_name: str, progress: dict) -> str:
    """Formats the welcome message with user progress."""
    return (
        f"Welcome back, {user_name}!\n\n"
        "Your progress:\n"
        f"🌳 Trees: {progress.get('trees', 0)}\n"
        f"✨ Points: {progress.get('points', 0)}\n"
        f"⭐ Level: {progress.get('level', 1)}\n"
        f"⚡️ Energy: {progress.get('energy', 100)}/100\n"
        f"👆 Total Taps: {progress.get('total_taps', 0)}\n\n"
        "Keep growing your forest!"
    )

# You can add more text functions here
# For example, a function for the leaderboard text
# def format_leaderboard(leaders: list) -> str:
#     ...
