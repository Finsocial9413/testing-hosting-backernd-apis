from agno.agent import Agent
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

from agno.models.google import Gemini
def simple_test_tool():
    """A simple test tool to check if the model can call functions"""
    return "Tool call successful!"
def check_platform_apis(platform, api_key):
    if platform=='OpenAIChat':
        try:
                # Create agent with a simple test tool
            agent = Agent(
                    model=OpenAIChat(id='gpt-4o', api_key=api_key),  # Replace with your model
                    tools=[simple_test_tool],
                    # show_tool_calls=True
                )
                # Ask the agent to use the tool
            response = agent.run("Please call the simple_test_tool function")
                
                # Check if tool was called by looking at tool calls in the response
            if hasattr(response, 'tool_calls') and response.tool_calls:
                
                return {'api_working':'yes'}
                
            # Alternative check: look for tool call evidence in the response content
            if "simple_test_tool" in str(response.content).lower():
                return {'api_working':'yes'}

            return { 'api_working':'yes'}

        except Exception as e:
            error = str(e)
            return { 'api_working':'not working'}

    elif platform=='Open Router':
        try:
                # Create agent with a simple test tool
            agent = Agent(
                    model=OpenRouter(id='gpt-4o', api_key=api_key),  # Replace with your model
                    tools=[simple_test_tool],
                    # show_tool_calls=True
                )
                # Ask the agent to use the tool
            response = agent.run("Please call the simple_test_tool function")
                
                # Check if tool was called by looking at tool calls in the response
            if hasattr(response, 'tool_calls') and response.tool_calls:
                
                return {'api_working':'yes'}
                
            # Alternative check: look for tool call evidence in the response content
            if "simple_test_tool" in str(response.content).lower():
                return {'api_working':'yes'}

            return { 'api_working':'yes'}

        except Exception as e:
            error = str(e)
            return { 'api_working':'not working'}
        
    elif platform=='Mistral AI':
        try:
                # Create agent with a simple test tool
            agent = Agent(
                    model=MistralChat(id='Qwen/Qwen2.5-32B-Instruct', api_key=api_key),  # Replace with your model
                    tools=[simple_test_tool],
                    # show_tool_calls=True
                )
                # Ask the agent to use the tool
            response = agent.run("Please call the simple_test_tool function")
                
                # Check if tool was called by looking at tool calls in the response
            if hasattr(response, 'tool_calls') and response.tool_calls:
                
                return {'api_working':'yes'}
                
            # Alternative check: look for tool call evidence in the response content
            if "simple_test_tool" in str(response.content).lower():
                return {'api_working':'yes'}

            return { 'api_working':'yes'}

        except Exception as e:
            error = str(e)
            return { 'api_working':'not working'}
        
    elif platform=='NVIDIA':
        try:
                # Create agent with a simple test tool
            agent = Agent(
                    model=Nvidia(id='ai21labs/jamba-1.5-large-instruct', api_key=api_key),  # Replace with your model
                    tools=[simple_test_tool],
                    # show_tool_calls=True
                )
                # Ask the agent to use the tool
            response = agent.run("Please call the simple_test_tool function")
                
                # Check if tool was called by looking at tool calls in the response
            if hasattr(response, 'tool_calls') and response.tool_calls:
                
                return {'api_working':'yes'}
                
            # Alternative check: look for tool call evidence in the response content
            if "simple_test_tool" in str(response.content).lower():
                return {'api_working':'yes'}

            return { 'api_working':'yes'}

        except Exception as e:
            error = str(e)
            return { 'api_working':'not working'}
        
    elif platform=='Nebius':
        try:
                # Create agent with a simple test tool
            agent = Agent(
                    model=Nebius(id='Qwen/Qwen2.5-32B-Instruct', api_key=api_key),  # Replace with your model
                    tools=[simple_test_tool],
                    # show_tool_calls=True
                )
                # Ask the agent to use the tool
            response = agent.run("Please call the simple_test_tool function")
                
                # Check if tool was called by looking at tool calls in the response
            if hasattr(response, 'tool_calls') and response.tool_calls:
                
                return {'api_working':'yes'}
                
            # Alternative check: look for tool call evidence in the response content
            if "simple_test_tool" in str(response.content).lower():
                return {'api_working':'yes'}

            return { 'api_working':'yes'}

        except Exception as e:
            error = str(e)
            return { 'api_working':'not working'}
        
    elif platform=='Sambanova':
        try:
                # Create agent with a simple test tool
            agent = Agent(
                    model=Sambanova(id='DeepSeek-R1-0528', api_key=api_key),  # Replace with your model
                    tools=[simple_test_tool],
                    # show_tool_calls=True
                )
                # Ask the agent to use the tool
            response = agent.run("Please call the simple_test_tool function")
                
                # Check if tool was called by looking at tool calls in the response
            if hasattr(response, 'tool_calls') and response.tool_calls:
                
                return {'api_working':'yes'}
                
            # Alternative check: look for tool call evidence in the response content
            if "simple_test_tool" in str(response.content).lower():
                return {'api_working':'yes'}

            return { 'api_working':'yes'}

        except Exception as e:
            error = str(e)
            return { 'api_working':'not working'}
        
    elif platform=='Google gemini':
        try:
                # Create agent with a simple test tool
            agent = Agent(
                    model=Gemini(id='gemini-2.0-flash', api_key=api_key),  # Replace with your model
                    tools=[simple_test_tool],
                    # show_tool_calls=True
                )
                # Ask the agent to use the tool
            response = agent.run("Please call the simple_test_tool function")
                
                # Check if tool was called by looking at tool calls in the response
            if hasattr(response, 'tool_calls') and response.tool_calls:
                
                return {'api_working':'yes'}
                
            # Alternative check: look for tool call evidence in the response content
            if "simple_test_tool" in str(response.content).lower():
                return {'api_working':'yes'}

            return { 'api_working':'yes'}

        except Exception as e:
            return { 'api_working':'not working'}
    return { 'api_working':'not working', 'platform':"This platform is not valid"}





def test(platform, api_key):
    supports_tools = check_platform_apis(platform, api_key)

    if len(supports_tools) > 1:
        valid = {}
        valid['api_working'] =supports_tools['api_working']
        valid['platform'] =supports_tools['platform']
        return valid
    else:
        valid = ''
        valid =  supports_tools['api_working']
        return valid
        
        

