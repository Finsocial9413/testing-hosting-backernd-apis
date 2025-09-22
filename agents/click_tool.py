from typing import List, Dict
from agno.agent import Agent
from agno.tools import Toolkit
import re
from .routes_Data import buttons_info

class ClickTools(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="click_tools", tools=[self.click_button, self.smart_click], **kwargs)
        self.button_keywords = buttons_info()

    def click_button(self, button: str) -> str:
        """
        Click on a specific button on the website.
        """
        button_lower = button.lower().strip()
        
        # Direct match first
        for key, value in self.button_keywords.items():
            if key.lower() == button_lower:
                return f"CLICK_BUTTON:{value}"
        
        # Partial match
        for key, value in self.button_keywords.items():
            if button_lower in key.lower() or key.lower() in button_lower:
                return f"CLICK_BUTTON:{value}"
        
        return f"CLICK_ERROR:Button '{button}' not found. Available buttons include: {', '.join(list(self.button_keywords.keys())[:10])}..."

    def smart_click(self, instruction: str) -> str:
        """
        Intelligently parse user instructions for button clicking.
        Handles various click command formats.
        """
        instruction_lower = instruction.lower().strip()
        steps = []

        # Enhanced click patterns
        click_patterns = [
            r"click\s+(?:on\s+)?(?:the\s+)?([a-zA-Z0-9\-\s&()]+?)(?:\s+button)?(?:\s+please)?$",
            r"press\s+(?:the\s+)?([a-zA-Z0-9\-\s&()]+?)(?:\s+button)?",
            r"tap\s+(?:on\s+)?(?:the\s+)?([a-zA-Z0-9\-\s&()]+?)(?:\s+button)?",
            r"hit\s+(?:the\s+)?([a-zA-Z0-9\-\s&()]+?)(?:\s+button)?",
            r"select\s+(?:the\s+)?([a-zA-Z0-9\-\s&()]+?)(?:\s+button)?",
            r"choose\s+(?:the\s+)?([a-zA-Z0-9\-\s&()]+?)(?:\s+button)?"
        ]

        # Check for explicit click commands
        click_found = False
        for pattern in click_patterns:
            click_match = re.search(pattern, instruction_lower)
            if click_match:
                button = click_match.group(1).strip()
                click_result = self.click_button(button)
                steps.append(click_result)
                if "CLICK_BUTTON" in click_result:
                    steps.append(f"STEP_COMPLETE:Successfully clicked on {button} button")
                click_found = True
                break

        # Fallback for button-related keywords
        if not click_found:
            if any(word in instruction_lower for word in ['button', 'btn', 'click', 'press', 'tap', 'hit', 'select', 'choose']):
                # Extract potential button name
                button_words = re.sub(r'\b(button|btn|click|press|tap|hit|on|the|please|select|choose)\b', '', instruction_lower)
                button = button_words.strip()
                if button:
                    click_result = self.click_button(button)
                    steps.append(click_result)
                    if "CLICK_BUTTON" in click_result:
                        steps.append(f"STEP_COMPLETE:Successfully clicked on {button} button")
                else:
                    steps.append("CLICK_ERROR:Could not identify button to click")
            else:
                # Try direct button name match
                click_result = self.click_button(instruction_lower)
                if "CLICK_BUTTON" in click_result:
                    steps.append(click_result)
                    steps.append(f"STEP_COMPLETE:Successfully clicked on {instruction_lower} button")
                else:
                    steps.append(f"CLICK_ERROR:'{instruction}' does not appear to be a valid button command")

        return " | ".join(steps)

    def list_buttons(self) -> str:
        """
        List all available buttons that can be clicked.
        """
        buttons_list = list(self.button_keywords.keys())
        return f"AVAILABLE_BUTTONS:{', '.join(buttons_list)}"
