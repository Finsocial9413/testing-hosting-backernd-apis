from agno.agent import Agent
from agno.models.openai import OpenAIChat

def simple_test_tool():
    """A simple test tool to check if the model can call functions"""
    return "Tool call successful!"

def test_Tool_bro(model_name):
    agent = Agent(
    model=OpenAIChat(id=model_name,api_key="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"),  # api_key read from env
    tools=[
        simple_test_tool,
        # calc  # if the library expects an instance
    ],
    
    markdown=False,
    )
    prompt = "Please call simple_test_tool to verify tool support."
    try:
        resp = agent.run(prompt)
        return True
        print("Model response:", resp.content)
    except Exception as e:
        return False
    