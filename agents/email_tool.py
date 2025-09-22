import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from agno.tools import Toolkit
from agno.utils.log import logger

import os

import os
from dotenv import load_dotenv

# Set the path to your .env file
env_path = r"D:\finsocial\Multi model adding for the trading\.env"
load_dotenv(dotenv_path=env_path)



class EmailTools(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(
            name="email_tools", 
            tools=[self.send_email, self.send_email_with_content], 
            **kwargs
        )
        
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        
    def send_email(self, recipient_email: str, subject: str, content: str) -> str:
        """
        Send email to any email address.
        
        Args:
            recipient_email (str): Recipient's email address
            subject (str): Email subject line
            content (str): Email content/body
            
        Returns:
            str: Success or error message
        """
        return self._send_email_internal(recipient_email, subject, content, "html")
    
    def send_email_with_content(self, subject: str, content: str, recipient_email: Optional[str] = None) -> str:
        """
        Send email with specified content. Email address is required.
        
        Args:
            subject (str): Email subject line
            content (str): Email content/body
            recipient_email (str, optional): Recipient's email address
            
        Returns:
            str: Success or error message
        """
        # 🚨 NO DEFAULT EMAIL - User must provide email address
        if not recipient_email:
            return "ERROR: Email address is required. Please ask the user: 'What email address should I send this to?' and then call this tool again with the email address."
            
        return self._send_email_internal(recipient_email, subject, content, "html")
    
    def _format_content_for_email(self, content: str) -> str:
        """Format content for better email display"""
        import re
        
        # Convert triple backtick code blocks (```language\ncode\n```)
        content = re.sub(r'```(\w+)?\n(.*?)\n```', 
                        lambda m: f'<div style="background-color: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; margin: 15px 0; font-family: \'Courier New\', monospace; white-space: pre-wrap; overflow-x: auto; border-left: 4px solid #ff9900;"><strong style="color: #ff9900;">{m.group(1) or "Code"}:</strong><br><br>{m.group(2)}</div>', 
                        content, flags=re.DOTALL)
        
        # Convert single backtick code blocks (```code```)
        content = re.sub(r'```([^`\n]+?)```', 
                        r'<div style="background-color: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; margin: 15px 0; font-family: \'Courier New\', monospace; white-space: pre-wrap; overflow-x: auto; border-left: 4px solid #ff9900;"><strong style="color: #ff9900;">Code:</strong><br><br>\1</div>', 
                        content)
        
        # Convert inline code
        content = re.sub(r'`([^`]+)`', r'<code style="background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: \'Courier New\', monospace; color: #d63384;">\1</code>', content)
        
        # Convert numbered lists (1. item)
        content = re.sub(r'^\d+\.\s+(.+)$', r'<li style="margin: 8px 0;">\1</li>', content, flags=re.MULTILINE)
        
        # Convert bullet points (* item)
        content = re.sub(r'^\*\s+(.+)$', r'<li style="margin: 8px 0;">\1</li>', content, flags=re.MULTILINE)
        
        # Wrap consecutive list items in ol/ul tags
        content = re.sub(r'(<li[^>]*>.*?</li>(?:\s*<li[^>]*>.*?</li>)*)', r'<ul style="padding-left: 20px; margin: 15px 0;">\1</ul>', content, flags=re.DOTALL)
        
        # Convert bold text
        content = re.sub(r'\*\*([^*]+)\*\*', r'<strong style="color: #333;">\1</strong>', content)
        
        # Convert headers (# Header)
        content = re.sub(r'^#+\s+(.+)$', r'<h3 style="color: #ff9900; margin: 20px 0 10px 0;">\1</h3>', content, flags=re.MULTILINE)
        
        # Convert line breaks to HTML (but preserve existing HTML)
        content = re.sub(r'\n(?![<>])', '<br>', content)
        
        # Clean up extra br tags around block elements
        content = re.sub(r'<br>\s*(<div|<ul|<h)', r'\1', content)
        content = re.sub(r'(</div>|</ul>|</h\d>)\s*<br>', r'\1', content)
        
        # Add some spacing after paragraphs
        content = re.sub(r'(<br>){2,}', '<br><br>', content)
        
        return content

    def _send_email_internal(self, recipient_email: str, subject: str, content: str, format_type: str) -> str:
        """
        Internal method to handle the actual email sending.
        """
        try:
            # Validate email configuration
            if not self.sender_email or not self.sender_password:
                return "ERROR: Email configuration not set. Please configure SENDER_EMAIL and SENDER_PASSWORD environment variables."
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add HindAI branding to content
            branded_content = self._add_branding(content, format_type)
            
            # Attach content based on format
            if format_type.lower() == 'html':
                msg.attach(MIMEText(branded_content, 'html'))
            else:
                msg.attach(MIMEText(branded_content, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            success_msg = f"Email sent successfully to {recipient_email}"
            logger.info(success_msg)
            return f"SUCCESS: {success_msg}"
            
        except Exception as e:
            error_msg = f"Failed to send email to {recipient_email}: {str(e)}"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"
    
    def _add_branding(self, content: str, format_type: str) -> str:
        """Add HindAI branding to email content with proper formatting."""
        if format_type.lower() == 'html':
            # Convert markdown-style formatting to HTML
            formatted_content = self._format_content_for_email(content)
            
            return f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #1e1e1e; color: #fff; padding: 20px; text-align: center;">
                    <h2 style="margin: 0; color: #ff9900;">HindAI</h2>
                    <p style="margin: 5px 0 0 0; font-size: 14px;">Powered by Finsocial Digital Systems</p>
                </div>
                <div style="padding: 20px; background-color: #f9f9f9; line-height: 1.6;">
                    {formatted_content}
                </div>
                <div style="background-color: #1e1e1e; color: #888; padding: 15px; text-align: center; font-size: 12px;">
                    <p>This email was sent by HindAI - Developed by Finsocial Digital Systems</p>
                    <p>© 2025 Finsocial Digital Systems. All rights reserved.</p>
                </div>
            </div>
            """
        else:
            return f"""
    HindAI - Powered by Finsocial Digital Systems
    ============================================

    {content}

    ---
    This email was sent by HindAI
    Developed by Finsocial Digital Systems
    © 2025 Finsocial Digital Systems. All rights reserved.
            """

