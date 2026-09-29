"""Notification manager for SCDO"""
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class NotificationManager:
    def __init__(self):
        self._notifications: Dict[str, List[Dict[str, Any]]] = {}
        self._preferences: Dict[str, Dict[str, bool]] = {}

    def add_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "info",
    ) -> str:
        notif_id = f"notif_{datetime.utcnow().timestamp()}"
        if user_id not in self._notifications:
            self._notifications[user_id] = []

        self._notifications[user_id].append({
            "id": notif_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "read": False,
            "created_at": datetime.utcnow(),
        })
        return notif_id

    def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
    ) -> List[Dict[str, Any]]:
        notifs = self._notifications.get(user_id, [])
        if unread_only:
            notifs = [n for n in notifs if not n["read"]]
        return sorted(notifs, key=lambda x: x["created_at"], reverse=True)

    def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        for n in self._notifications.get(user_id, []):
            if n["id"] == notification_id:
                n["read"] = True
                return True
        return False

    def mark_all_as_read(self, user_id: str) -> int:
        count = 0
        for n in self._notifications.get(user_id, []):
            if not n["read"]:
                n["read"] = True
                count += 1
        return count

    def get_preferences(self, user_id: str) -> Dict[str, bool]:
        return self._preferences.get(user_id, {
            "email_on_complete": True,
            "email_on_error": True,
            "in_app_notifications": True,
        })

    def update_preferences(self, user_id: str, prefs: Dict[str, bool]) -> bool:
        self._preferences[user_id] = prefs
        return True


class EmailNotifier:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_pass = os.getenv("SMTP_PASS", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@scdo.local")
        self._available = all([self.smtp_host, self.smtp_user, self.smtp_pass])

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        if not self._available:
            logger.warning("Email not configured — skipping email notification")
            return False

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_task_complete_email(
        self,
        to_email: str,
        task_type: str,
        course_title: str,
    ) -> bool:
        subject = f"SCDO: {task_type} complete for {course_title}"
        body = f"Your {task_type} for '{course_title}' has been completed."
        return self.send_email(to_email, subject, body)

    def send_task_error_email(
        self,
        to_email: str,
        task_type: str,
        course_title: str,
        error: str,
    ) -> bool:
        subject = f"SCDO: {task_type} failed for {course_title}"
        body = f"Your {task_type} for '{course_title}' failed with error: {error}"
        return self.send_email(to_email, subject, body)


notification_manager = NotificationManager()
email_notifier = EmailNotifier()
