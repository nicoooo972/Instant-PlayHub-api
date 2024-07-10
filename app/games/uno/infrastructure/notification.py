from app.core.notification.infrastructure.notification_interface import \
    NotificationInterface


class Notification(NotificationInterface):
    def __init__(self, context: str):
        self.context = context

    def success(self, message: str):
        print(f"[SUCCESS] [{self.context}] {message}")

    def warn(self, message: str):
        print(f"[WARN] [{self.context}] {message}")

    def error(self, message: str):
        print(f"[ERROR] [{self.context}] {message}")