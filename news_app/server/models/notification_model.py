from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class UserNotification:
    id: int
    user_id: int
    keywords: Optional[str]
    notify_via_email: bool = True
    enabled: bool = True
    last_notification_time: Optional[datetime] = None
