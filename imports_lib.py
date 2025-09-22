"""
A centralized imports module for the Finsocial MCP LLMs project.
Import all dependencies from this file using:
    from imports_lib import *
"""

# Standard library imports
import asyncio
from textwrap import dedent  # Fixed typo from dedentc

# Agno core imports
from agno.agent import Agent
from agno.models.openai.like import OpenAILike

from agno.db.sqlite import SqliteDb


# Agno tools imports
from agno.tools.mcp import MultiMCPTools
from agno.tools.python import PythonTools
from agno.tools.youtube import YouTubeTools
from agno.tools.wikipedia import WikipediaTools

from agno.tools.pubmed import PubmedTools
from agno.tools.jina import JinaReaderTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools

# Third-party imports
from rich.pretty import pprint


from components.translator import show_language_menu
from components.translator import LanguageTranslator
from components.instructions import instructions_steps
import random
from components.generate_unique_chat_id import generate_unique_id

from agents.reasioning_agent import get_detailed_reasoning
from components.savingintoJson import save_message_to_json, update_json_entry
# Define exports for "from imports_lib import *"
__all__ = [
    'get_detailed_reasoning','save_message_to_json','update_json_entry',
    'show_language_menu', 'LanguageTranslator',
    'asyncio', 'dedent','instructions_steps', 'generate_unique_id',
     'random',
    'Agent', 'OpenAILike', 'SqliteDb',
    'MultiMCPTools',
    'PythonTools', 'YouTubeTools', 'WikipediaTools',
    'PubmedTools', 'JinaReaderTools',
    'YFinanceTools', 'Newspaper4kTools', 'DuckDuckGoTools',
    'ReasoningTools', 'pprint'
]