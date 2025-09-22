


from agno.agent import Agent

from agno.models.openrouter import OpenRouter
model = "gemini-2.0-flash-exp"  # Keep using your preferred model

# Initialize the HTML generator agent
html_generator = Agent(
    name="HTML Generator",
    model= OpenRouter(id="google/gemini-2.5-flash", api_key='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',
        max_tokens=4000),
    description="You are an expert HTML code generator. Your task is to take the complete content provided by the user and create an HTML webpage that represents the content exactly as given, without adding or altering any part of it.",
    instructions=[
        "Use modern HTML5 elements and best practices.",
        "Do not add any extra content, animations, or interactive elements not explicitly provided by the user.",
        "Ensure that the generated HTML faithfully represents the user's input.",
        "Use semantic HTML elements such as header, nav, main, section, article, and footer only where applicable.",
        "Apply only minimal inline CSS if necessary, strictly for layout purposes without modifying the user content.",
        "Output only the complete HTML wrapped in ```html tags, without any additional commentary.",
        "The webpage should have dark mode styling by default.",
        """Add the company branding: include 'Hind AI' prominently and a footer note stating "Developed by the finsocial digital systems""",
    ]
)
def generate_html(prompt: str) -> str:
    """
    Generate HTML based on the user's prompt
    
    Args:
        prompt: Description of the HTML to generate
        
    Returns:
        Generated HTML code
    """
    try:
        print("i am here for generating the htmml page")
        # Run the agent with the prompt
        response = html_generator.run(prompt)
        
        # Extract and return the generated HTML
        if response and response.content:
            return response.content
        return "Error: No content generated"
        
    except Exception as e:
        return f"Error generating HTML: {str(e)}"


