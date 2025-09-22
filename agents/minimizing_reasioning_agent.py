from textwrap import dedent
from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools
import asyncio
from agno.models.openrouter import OpenRouter
GOOGLE_API_KEY = 'AIzaSyAx65YdFAZ--Uuf93oXHjA8kpiA7SNGb4g'
async def show_reasoning_agent():
    agent = Agent(
    model= OpenRouter(id="google/gemini-2.5-flash", api_key='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'),
   
    tools=[ReasoningTools(add_instructions=True)],
    instructions=dedent("""
            You are a reasoning expert that reformats analysis in a concise, neutral style.

            When processing reasoning text:
            1. Remove obvious step numbering and formatting
            2. Combine related points into cohesive paragraphs
            3. Use natural transitions between ideas
            4. Maintain the logical flow while being more concise
            5. Remove any LLM-specific patterns or markers
            6. Present conclusions in a clear, straightforward manner
            
            Keep the essence of the reasoning while making it appear more human-written.
    """),
    markdown=True,
    # show_tool_calls=True
    )
    return agent



async def show_reasoning_finals(prompt):
    try:
        agent = await show_reasoning_agent()
        final_res = await agent.arun(
            message={
                "role": "user",
                "content": f"Summarize this reasoning concisely: {prompt}",
            },
            stream=False
        )
        return final_res.content
    except Exception as e:
        print(f"Error in show_reasoning_finals: {str(e)}")
        # Return the original prompt if processing fails
        return prompt
