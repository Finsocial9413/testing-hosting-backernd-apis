from typing import List, Dict
from agno.agent import Agent
from agno.tools import Toolkit
import re
import requests
import json
from .routes_Data import routes_Database
ROUTES = routes_Database()

# Build mappings
valid_pages = [route[0] for route in ROUTES]
keyword_to_page = {}
for page, keywords in ROUTES:
    for kw in keywords:
        keyword_to_page[kw.lower()] = page

class NavigationTools(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="navigation_tools", tools=[self.navigate_to_page, self.smart_navigate], **kwargs)

    def navigate_to_page(self, page: str) -> str:
        """
        Navigate to a specific page on the website.
        """
        page_lower = page.lower().strip()
        if page_lower in valid_pages:
            return f"NAVIGATE_TO:{page_lower}"
        else:
            return f"NAVIGATION_ERROR:Page '{page}' not found. Available: {', '.join(valid_pages)}"

    def smart_navigate(self, instruction: str) -> str:
        """
        Intelligently parse user instructions and provide navigation steps.
        Handles page navigation only.
        """
        instruction_lower = instruction.lower().strip()
        steps = []

        # Navigation patterns
        nav_patterns = [
            r"(?:navigate|go|take\s+me)\s+to\s+(?:the\s+)?([a-zA-Z0-9\- ]+?)(?:\s+page)?",
            r"open\s+(?:the\s+)?([a-zA-Z0-9\- ]+?)(?:\s+page)?",
            r"show\s+(?:me\s+)?(?:the\s+)?([a-zA-Z0-9\- ]+?)(?:\s+page)?"
        ]

        # Check for explicit navigation commands
        nav_found = False
        for pattern in nav_patterns:
            nav_match = re.search(pattern, instruction_lower)
            if nav_match:
                page = nav_match.group(1).replace("page", "").strip()
                mapped_page = self._map_to_page(page)
                if mapped_page:
                    steps.append(f"NAVIGATE_TO:{mapped_page}")
                    steps.append(f"STEP_COMPLETE:Successfully navigated to {mapped_page} page")
                else:
                    steps.append(f"NAVIGATION_ERROR:Page '{page}' not found.")
                nav_found = True
                break

        # Fallback logic for simple page names
        if not nav_found:
            mapped_page = self._map_to_page(instruction_lower)
            if mapped_page:
                steps.append(f"NAVIGATE_TO:{mapped_page}")
                steps.append(f"STEP_COMPLETE:Successfully navigated to {mapped_page} page")
            else:
                # If nothing matches, suggest alternatives
                steps.append(f"NAVIGATION_ERROR:Could not understand '{instruction}'. Try 'navigate to [page]' or specify a valid page name")

        return " | ".join(steps)

    def _map_to_page(self, text: str) -> str:
        """Helper method to map text to actual page names"""
        text = text.strip().lower()
        if text in valid_pages:
            return text
        for kw, page in keyword_to_page.items():
            if kw in text:
                return page
        return None