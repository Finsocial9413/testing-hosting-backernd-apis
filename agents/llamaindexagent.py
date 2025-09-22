from typing import Optional
import requests
from agno.tools import Toolkit
from agno.utils.log import logger

class DropboxTools(Toolkit):
    def __init__(self, api_url="https://llamaindex.codewizzz.com", **kwargs):
        self.api_url = api_url
        self.current_session_id = None
        super().__init__(
            name="dropbox_tools", 
            tools=[self.get_answer_from_dropbox],
            **kwargs
        )

    def get_answer_from_dropbox(self, url: str, question: str = "What are the key concepts covered in this document?") -> str:
        """
        Get answer to a question about a document stored on Dropbox.
        
        Args:
            url (str): URL to the Dropbox file
            question (str): Question to ask about the document
            
        Returns:
            str: The answer to the question
        """
        try:
            # Extract question from the input if it's in the URL
            actual_question = question
            if "what are the key conecpt of this doc?" in url.lower():
                actual_question = "What are the key concepts covered in this document?"
                url = url.split("?")[0] + "?" + "&".join([param for param in url.split("?")[1].split("&") if "what are" not in param.lower()])

            logger.info(f"Uploading file from Dropbox: {url}")
            upload_response = requests.post(
                f"{self.api_url}/upload-from-dropbox",
                json={"url": url},
                timeout=60
            )
            upload_response.raise_for_status()
            
            self.current_session_id = upload_response.json().get('session_id')
            if not self.current_session_id:
                raise Exception("No session ID returned from the server")

            # Query the document with the question
            logger.info(f"Querying document with question: {actual_question}")
            query_response = requests.post(
                f"{self.api_url}/query",
                json={
                    "question": actual_question,
                    "session_id": self.current_session_id
                },
                timeout=60
            )
            query_response.raise_for_status()
            
            return query_response.json().get('response', 'No response received')
            
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get('detail', str(e))
                    error_message = f"API Error: {error_detail}"
                except:
                    pass
            logger.error(f"Error processing Dropbox request: {error_message}")
            return f"Error: {error_message}"