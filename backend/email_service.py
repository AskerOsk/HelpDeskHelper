"""
Email Service - SMTP notifications for escalated tickets
Sends HTML emails to managers when AI escalates conversation
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from dotenv import load_dotenv
from constants import (
    EMAIL_ESCALATION_SUBJECT,
    EMAIL_FROM_NAME,
    SENDER_USER,
    SENDER_AI
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EmailService:
    """Email notification service for manager escalations"""

    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.manager_email = os.getenv('MANAGER_EMAIL')
        self.from_email = self.smtp_username
        self.from_name = EMAIL_FROM_NAME

        # Validate configuration
        if not all([self.smtp_username, self.smtp_password, self.manager_email]):
            logger.warning(
                "Email service not fully configured. "
                "Set SMTP_USERNAME, SMTP_PASSWORD, MANAGER_EMAIL in .env"
            )
        else:
            logger.info(
                f"Email service initialized | SMTP: {self.smtp_host}:{self.smtp_port} | "
                f"Manager: {self.manager_email}"
            )

    def _format_timestamp(self, timestamp: str) -> str:
        """Format ISO timestamp to readable Russian format"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%d.%m.%Y %H:%M')
        except Exception:
            return timestamp

    def _build_html_email(
        self,
        ticket_number: str,
        user_info: Dict,
        conversation_history: List[Dict],
        ai_summary: str,
        ticket_id: int
    ) -> str:
        """
        Build HTML email template for escalation

        Args:
            ticket_number: Unique ticket identifier
            user_info: User details (username, user_id)
            conversation_history: Full conversation messages
            ai_summary: AI-generated summary
            ticket_id: Database ticket ID

        Returns:
            HTML email body
        """
        # Build conversation HTML
        messages_html = []
        for msg in conversation_history:
            sender = "👤 Клиент" if msg['sender_type'] == SENDER_USER else "🤖 AI"
            timestamp = self._format_timestamp(msg.get('created_at', ''))
            content = msg['content']
            media_info = ""

            if msg.get('media_type'):
                media_type = msg['media_type']
                media_url = msg.get('media_url', '')
                media_info = f"<br><em>[{media_type.upper()}]: <a href='{media_url}'>Посмотреть</a></em>"

            # Color code based on sender
            bg_color = "#FFF3E0" if msg['sender_type'] == SENDER_USER else "#E8F5E9"
            border_color = "#FF6B35" if msg['sender_type'] == SENDER_USER else "#00FF41"

            messages_html.append(f"""
                <div style="margin: 15px 0; padding: 12px; background: {bg_color};
                            border-left: 4px solid {border_color}; border-radius: 4px;">
                    <div style="font-weight: bold; margin-bottom: 5px;">
                        {sender} <span style="color: #666; font-size: 0.9em;">({timestamp})</span>
                    </div>
                    <div style="white-space: pre-wrap;">{content}</div>
                    {media_info}
                </div>
            """)

        conversation_block = "\n".join(messages_html)

        # Build full HTML email
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
                   color: #00FF41; padding: 25px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .alert {{ background: #FF6B35; color: white; padding: 15px; text-align: center;
                  font-weight: bold; font-size: 18px; }}
        .info-box {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .info-row {{ display: flex; margin: 8px 0; }}
        .info-label {{ font-weight: bold; width: 150px; color: #555; }}
        .info-value {{ flex: 1; }}
        .summary-box {{ background: #FFF9C4; border: 2px solid #FBC02D;
                        padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .conversation {{ margin: 20px 0; }}
        .footer {{ background: #f5f5f5; padding: 15px; text-align: center;
                   border-radius: 0 0 8px 8px; color: #666; font-size: 14px; }}
        a {{ color: #00FF41; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Sulpak AI HelpDesk</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Система автоматической поддержки клиентов</p>
        </div>

        <div class="alert">
            🚨 ТРЕБУЕТСЯ ЭСКАЛАЦИЯ - AI передал обращение менеджеру
        </div>

        <div class="info-box">
            <h2 style="margin-top: 0; color: #000;">📋 Информация о тикете</h2>
            <div class="info-row">
                <div class="info-label">Номер тикета:</div>
                <div class="info-value"><strong>{ticket_number}</strong></div>
            </div>
            <div class="info-row">
                <div class="info-label">ID тикета:</div>
                <div class="info-value">#{ticket_id}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Пользователь:</div>
                <div class="info-value">@{user_info.get('telegram_username', 'Unknown')}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Telegram ID:</div>
                <div class="info-value">{user_info.get('telegram_user_id', 'N/A')}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Дата эскалации:</div>
                <div class="info-value">{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
            </div>
        </div>

        <div class="summary-box">
            <h3 style="margin-top: 0; color: #F57C00;">💡 Резюме от AI</h3>
            <p style="margin: 0; white-space: pre-wrap;">{ai_summary}</p>
        </div>

        <div class="conversation">
            <h2 style="color: #000;">💬 Полная история беседы</h2>
            {conversation_block}
        </div>

        <div class="footer">
            <p><strong>Действия:</strong></p>
            <p>1. Изучите беседу и резюме AI<br>
            2. Свяжитесь с клиентом в Telegram: @{user_info.get('telegram_username', 'Unknown')}<br>
            3. Обновите статус тикета в системе после решения</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 15px 0;">
            <p style="font-size: 12px; color: #999;">
                Это автоматическое уведомление от Sulpak AI HelpDesk<br>
                Пожалуйста, не отвечайте на это письмо
            </p>
        </div>
    </div>
</body>
</html>
        """

        return html

    async def send_escalation_email(
        self,
        ticket_number: str,
        ticket_id: int,
        user_info: Dict,
        conversation_history: List[Dict],
        ai_summary: str
    ) -> bool:
        """
        Send escalation notification email to manager

        Args:
            ticket_number: Unique ticket identifier
            ticket_id: Database ticket ID
            user_info: User details
            conversation_history: Full conversation
            ai_summary: AI-generated summary

        Returns:
            True if email sent successfully, False otherwise
        """
        if not all([self.smtp_username, self.smtp_password, self.manager_email]):
            logger.error("Email service not configured. Skipping email send.")
            return False

        try:
            logger.info(f"Sending escalation email for ticket {ticket_number}")

            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = f"{EMAIL_ESCALATION_SUBJECT} | {ticket_number}"
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = self.manager_email

            # Build HTML body
            html_body = self._build_html_email(
                ticket_number=ticket_number,
                user_info=user_info,
                conversation_history=conversation_history,
                ai_summary=ai_summary,
                ticket_id=ticket_id
            )

            # Attach HTML
            html_part = MIMEText(html_body, 'html', 'utf-8')
            message.attach(html_part)

            # Send email via SMTP
            use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
            use_ssl = os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'

            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                start_tls=use_tls,
                use_tls=use_ssl
            )

            logger.info(
                f"Escalation email sent successfully for ticket {ticket_number} "
                f"to {self.manager_email}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to send escalation email for ticket {ticket_number}: {e}",
                exc_info=True
            )
            return False


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create email service singleton"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
