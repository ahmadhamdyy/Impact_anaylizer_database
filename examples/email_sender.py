"""
Example Email Sender Module
Demonstrates email functionality and external dependencies.
"""
import smtplib
from email.mime.text import MIMEText
from typing import Optional


class EmailSender:
    """Handles email sending operations."""
    
    def __init__(self, smtp_server: str = 'smtp.example.com', port: int = 587):
        """Initialize email sender with SMTP configuration."""
        self.smtp_server = smtp_server
        self.port = port
        self.connection = None
    
    def connect(self):
        """Establish SMTP connection."""
        self.connection = smtplib.SMTP(self.smtp_server, self.port)
        self.connection.starttls()
    
    def send_welcome_email(self, recipient: str) -> bool:
        """Send a welcome email to a new user."""
        subject = "Welcome!"
        body = "Thank you for joining us!"
        return self._send_email(recipient, subject, body)
    
    def send_notification(self, recipient: str, message: str) -> bool:
        """Send a notification email."""
        subject = "Notification"
        return self._send_email(recipient, subject, message)
    
    def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Internal method to send an email."""
        try:
            if not self.connection:
                self.connect()
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = 'noreply@example.com'
            msg['To'] = recipient
            
            self.connection.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def disconnect(self):
        """Close SMTP connection."""
        if self.connection:
            self.connection.quit()
            self.connection = None


class EmailTemplate:
    """Utility class for email templates."""
    
    @staticmethod
    def get_welcome_template(username: str) -> str:
        """Generate welcome email template."""
        return f"Hello {username}, welcome to our platform!"
    
    @staticmethod
    def get_reset_password_template(token: str) -> str:
        """Generate password reset email template."""
        return f"Click here to reset your password: {token}"




