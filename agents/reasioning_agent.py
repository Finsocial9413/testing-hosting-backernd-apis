from agno.agent.agent import Agent
# from agno.memory.v2.db.sqlite import SqliteMemoryDb
# from agno.memory.v2.memory import Memory

from agno.db.sqlite import SqliteDb


from .navigations_tool import NavigationTools
from .email_tool import EmailTools

from .click_tool import ClickTools
from .charts import ChartTools

from .visualization import VisualizationTools


from agno.models.openai.like import OpenAILike
from agno.models.anthropic import Claude
# from agno.models.cohere import Cohere
from agno.models.deepinfra import DeepInfra
from agno.models.deepseek import DeepSeek
from agno.models.fireworks import Fireworks
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.models.lmstudio import LMStudio
from agno.models.meta import Llama
from agno.models.mistral import MistralChat
from agno.models.nvidia import Nvidia
from agno.models.nebius import Nebius
from agno.models.openai import OpenAIChat
from agno.models.openrouter import OpenRouter
from agno.models.perplexity import Perplexity
from agno.models.sambanova import Sambanova
from agno.models.together import Together
from agno.models.vercel import v0
from agno.models.xai import xAI

from agno.tools.openbb import OpenBBTools
from agno.tools.tavily import TavilyTools

import os
from dotenv import load_dotenv

# Set the path to your .env file
env_path = r"D:\finsocial\Multi model adding for the trading\.env"
load_dotenv(dotenv_path=env_path)


# Create reasoning-only agent
async def create_reasoning_agent(model_name,chat_id, username,current_time,base_path,api,model_config):
    """Create a reasoning agent with specific instructions."""
        # Setup memory database with read-only setting
    # Create SQLite storage with proper initialization
    memory_db = SqliteDb(
        db_file=f"{base_path}/{username}/SqlDB/{chat_id}.db"
    )
  
    # Define the agent with detailed reasoning instructions
    reasoning_agent = Agent(
        model= OpenRouter(id=model_name, api_key=os.getenv("OPENROUTER_API_KEY"),
        max_tokens=1024) if api == 'no' else model_config,
        tools=[ OpenBBTools(enable_get_stock_price=True, enable_search_company_symbol=True, enable_get_company_news=True, enable_get_company_profile=True, enable_get_price_targets=True,all=True),
                VisualizationTools(output_dir="D:/finsocial/Multi model adding for the trading/agents/charts/", enable_all=True),
               TavilyTools(api_key='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'),
               ChartTools(),
               NavigationTools(),
               ClickTools()],
        db=memory_db,
        session_id=chat_id,
        user_id=username,
        enable_user_memories=False,
        add_history_to_context=True,
        read_chat_history=True,
        instructions=[
            "You are a detailed reasoning engine that breaks down complex problems into comprehensive analytical steps.",
            f"Current time = {current_time}",
                "For each question:",
                "1. First, identify the key components or aspects that need analysis",
                "2. For each component, provide detailed reasoning steps",
                "3. Consider multiple perspectives and angles",
                "4. Examine potential implications and consequences",
                "5. Analyze relationships between different aspects",
                "6. Consider relevant context and background information",
                "7. Identify any assumptions being made",
                "8. Do NOT provide final conclusions or answers",
                "Format each step as 'Reasoning Step X.Y:', where X is the component number and Y is the step number within that component",
                "Make each step detailed and thorough"
        ]
    )
    
    return reasoning_agent

async def get_detailed_reasoning(*, reasoning_model, question, chat_id, username, current_time, base_path, api, model_config):
    try:
        if api =='no':
            reasoning_agent = await create_reasoning_agent(reasoning_model,chat_id, username,current_time,base_path,api,model_config)

            # Get detailed reasoning response with simplified prompt to reduce processing time
            response = await reasoning_agent.arun(
                f"""
                Provide a concise analysis of this question:
                {question}
                
                Focus on the key points and main considerations needed to address this request effectively.
                """,
                stream=False
            )
            return response.content
        
        else:
            reasoning_agent = await create_reasoning_agent(reasoning_model,chat_id, username,current_time,base_path,api,model_config)

            # Get detailed reasoning response with simplified prompt to reduce processing time
            response = await reasoning_agent.arun(
                f"""
                Provide a concise analysis of this question:
                {question}
                
                Focus on the key points and main considerations needed to address this request effectively.
                """,
                stream=False
            )
            
            return response.content
        
    except Exception as e:
        print(f"Error in get_detailed_reasoning: {str(e)}")
        error_msg = str(e).lower()
        if 'no auth credentials found'.lower() in error_msg:
            return "Provided API is not correct check your api again_secretkey_to_remove_anyother_type_of_the_confusion123454645451215451545"
        
        # Return a fallback reasoning
        return f"Analyzing the question: '{question}'. This requires understanding the user's intent and providing an appropriate response based on available knowledge and context."
