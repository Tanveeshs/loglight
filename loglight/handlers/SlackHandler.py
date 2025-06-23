import sys
import requests
import json

from loglight.handlers.BaseHandler import BaseHandler


class SlackHandler(BaseHandler):
    def __init__(self, webhook_url, channel=None, username="loglight", icon_emoji=":speech_balloon:", timeout=5,
                 enable_internal_logging=True):
        super().__init__(enable_internal_logging)
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self.icon_emoji = icon_emoji
        self.timeout = timeout

    def emit(self, log_str: str):
        try:
            log_entry = json.loads(log_str)
            text = f"*[{log_entry.get('level', '')}]* {log_entry.get('event', '')}\n```{json.dumps(log_entry.get('details', {}), indent=2)}```"
            payload = {
                "text": text,
                "username": self.username,
                "icon_emoji": self.icon_emoji,
            }
            if self.channel:
                payload["channel"] = self.channel

            response = requests.post(self.webhook_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:

            self.log_internal_error("slack_emit_failed", e, context={"url": self.webhook_url})
