from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.openbb import OpenBBTools
from agno.models.openrouter import OpenRouter

import os
from dotenv import load_dotenv
import argparse

# Set the path to your .env file
env_path = r"D:\finsocial\Multi model adding for the trading\.env"
load_dotenv(dotenv_path=env_path)

def generate_suggestions(last_response: str, user_input: str):
    """Generate follow-up prompt suggestions based on the conversation context"""
    suggestion_agent = Agent(
        model=OpenRouter(id=os.getenv("suggestion_model"),  api_key=os.getenv("OPENROUTER_suggestion_API_KEY")),
        description=(
            "You are a suggestion generator that creates relevant follow-up prompts based on "
            "trading and financial conversations. Generate 3-4 short, actionable suggestions."
        ),
        instructions=[
            "Based on the user's question and the response, generate 3-4 relevant follow-up questions",
            "Keep suggestions short and specific (max 10 words each)",
            "Focus on trading, financial analysis, and stock market topics",
            "Format each suggestion on a new line with a number",
            "Make suggestions actionable and related to the current context",
            "If the conversation was about stock prices, suggest technical analysis, news, or comparison queries",
            "If about trading, suggest risk management, strategy, or market timing questions"
        ]
    )
    
    prompt = f"""
    User asked: "{user_input}"
    Assistant responded: "{last_response[:500]}..."
    
    Generate 3-4 relevant follow-up questions the user might want to ask next.
    """
    
    suggestions = suggestion_agent.run(prompt)
    return suggestions.content


def suggestion_list(suggestions):
    """Display suggestions in a formatted way"""
    list_of_suggestions = [line.strip() for line in suggestions.split('\n') if line.strip()]

    return list_of_suggestions


def create_suggested_agent(response, user_input):
    """Create a suggestion agent to generate follow-up prompts."""
    suggestions = generate_suggestions(response, user_input)
    results = suggestion_list(suggestions)
    return results
 
