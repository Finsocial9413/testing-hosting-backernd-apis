import os
import sys
import django

import asyncio
from asgiref.sync import sync_to_async
# Add the project root to the Python path




# importing all agno modal liberies 
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
from agno.models.nebius import Nebius

from agno.models.nvidia import Nvidia

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HindAi_project.settings')
django.setup()

from platforms.models import AvailablePlatforms, UserConnect, PlatformModel


async def choose_models(username, reasoning_model_platform, final_model_platform,reasoning_model_name,final_model_name, reasoning):
    reasoning_model_platform_api_key = ''
    final_model_platform_api_key= ''
    res_available =  False
    final_model_available = False
    # ensure configs always exist to avoid UnboundLocalError
    reasoning_model_config, final_model_config = None, None
    # checking if the platform exist or not first 
    # first check reasoning platform 
    if reasoning == True:    
        try:
            platform_obj = await sync_to_async(AvailablePlatforms.objects.get)(platform_name=str(reasoning_model_platform))
            reasoning_platform = await sync_to_async(UserConnect.objects.get)(user__username=username, platform=platform_obj)
            # checking if the user provided model is available for them
            for i in reasoning_platform.model_name.split(","):
                # use strip() to avoid whitespace mismatches
                if i.strip() == reasoning_model_name:
                    res_available = True
                    reasoning_model_platform_api_key = reasoning_platform.api_key
                    break
        except (UserConnect.DoesNotExist, AvailablePlatforms.DoesNotExist):
            reasoning_platform = None
            print("it's not available reasoning")

    try:
        platform_obj = await sync_to_async(AvailablePlatforms.objects.get)(platform_name=str(final_model_platform))
        final_platform = await sync_to_async(UserConnect.objects.get)(user__username=username, platform=platform_obj)
        # checking if the user provided model is available for them
       
        for i in final_platform.model_name.split(","):
            # use strip() to avoid whitespace mismatches
            if i.strip() == final_model_name:
                final_model_available = True
                final_model_platform_api_key = final_platform.api_key
                break
    except (UserConnect.DoesNotExist, AvailablePlatforms.DoesNotExist):
        final_platform = None
        print("it's not available final")
    
    # first setting up the final model
    if final_model_available == True:
        if final_model_platform == 'Open Router':
            final_model_config = OpenRouter(id=final_model_name,api_key=final_model_platform_api_key,
        max_tokens=1024)
        elif final_model_platform == 'Google Gemini':
            final_model_config = Gemini(id=final_model_name,api_key=final_model_platform_api_key,
        max_tokens=1024 )
        elif final_model_platform == 'OpenAIChat':
            final_model_config = OpenAIChat(id=final_model_name,api_key=final_model_platform_api_key,
        max_tokens=1024)
        elif final_model_platform == 'Sambanova':
            final_model_config = Sambanova(id=final_model_name,api_key=final_model_platform_api_key,
        max_tokens=1024)
        elif final_model_platform =='NVIDIA':
            final_model_config = Nvidia(id=final_model_name,api_key=final_model_platform_api_key,
        max_tokens=1024)
        elif final_model_platform == 'Nebius':
            final_model_config = Nebius(id=final_model_name,api_key=final_model_platform_api_key,
        max_tokens=1024)
        elif final_model_platform == 'Mistral AI':
            final_model_config = MistralChat(id=final_model_name,api_key=final_model_platform_api_key,
        max_tokens=1024)
        # elif final_model_platform == 'Claude':
        #     final_model_config = Claude(id=final_model_name,api_key=final_model_platform_api_key)
        # elif final_model_platform == 'DeepInfra':
        #     final_model_config = DeepInfra(id=final_model_name,api_key=final_model_platform_api_key)
        # elif final_model_platform == 'DeepSeek':
        #     final_model_config = DeepSeek(id=final_model_name,api_key=final_model_platform_api_key)
            

    if reasoning == True and res_available== True:
        
        if reasoning_model_platform == 'Open Router':
            # do not overwrite final_model_config here — only set the reasoning model
            reasoning_model_config = OpenRouter(id=reasoning_model_name,api_key=reasoning_model_platform_api_key,
        max_tokens=1024)
        elif reasoning_model_platform == 'OpenAIChat':
            reasoning_model_config = OpenAIChat(id=reasoning_model_name,api_key=reasoning_model_platform_api_key,
        max_tokens=1024)
        elif reasoning_model_platform == 'Sambanova':
            reasoning_model_config = Sambanova(id=reasoning_model_name,api_key=reasoning_model_platform_api_key,
        max_tokens=1024)
        elif final_model_platform == 'Google Gemini':
            final_model_config = GoogleGemini(id=reasoning_model_name,api_key=reasoning_model_platform_api_key,
        max_tokens=1024)
        elif final_model_platform == 'NVIDIA':
            final_model_config = Nvidia(id=reasoning_model_name,api_key=reasoning_model_platform_api_key,
        max_tokens=1024)
        elif final_model_platform == 'Nebius':
            final_model_config = Nebius(id=reasoning_model_name,api_key=reasoning_model_platform_api_key,
        max_tokens=1024)
        elif final_model_platform == 'Mistral AI':
            final_model_config = MistralChat(id=reasoning_model_name,api_key=reasoning_model_platform_api_key,
        max_tokens=1024)

        # elif reasoning_model_platform == 'Claude':
        #     reasoning_model_config = Claude(id=reasoning_model_name,api_key=reasoning_model_platform_api_key)
        # elif reasoning_model_platform == 'DeepInfra':
        #     reasoning_model_config = DeepInfra(id=reasoning_model_name,api_key=reasoning_model_platform_api_key)
        # elif reasoning_model_platform == 'DeepSeek':
        #     reasoning_model_config = DeepSeek(id=reasoning_model_name,api_key=reasoning_model_platform_api_key)
        return {
            "reasoning_model": reasoning_model_config,
            "final_model": final_model_config
        }


    return {
        "final_model": final_model_config,
    }
