from fastapi import BackgroundTasks
from pydantic import EmailStr
from twilio.rest import Client
from twilio.http.async_http_client import AsyncTwilioHttpClient
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from app.config import notification_settings
from app.utils import TEMPLATE_DIR


class NotificationService:
    def __init__(self, tasks: BackgroundTasks):
        self.tasks = tasks
        self.fastmail = FastMail(
            ConnectionConfig(
                **notification_settings.model_dump(exclude={"TWILIO_SID", "TWILIO_AUTH_TOKEN", "TWILIO_NUMBER"}),
                TEMPLATE_FOLDER=TEMPLATE_DIR,
            )
        )
        self.twilio_sid = notification_settings.TWILIO_SID
        self.twilio_auth_token = notification_settings.TWILIO_AUTH_TOKEN
        self._twilio_client = None

    def _get_twilio_client(self):
        # 2. Lazy load the client: create it only when needed.
        if self._twilio_client is None:
            self._twilio_client = Client(
                username=self.twilio_sid,
                password=self.twilio_auth_token,
                http_client=AsyncTwilioHttpClient()
            )
        return self._twilio_client

    async def send_email(self, recipients: list[EmailStr], subject: str, body: str):
        self.tasks.add_task(
            self.fastmail.send_message,
            message=MessageSchema(
                recipients=recipients,
                subject=subject,
                body=body,
                subtype=MessageType.plain,
            )
        )

    async def send_email_with_template(self, recipients: list[EmailStr], subject: str, context: dict, template_name: str):
        self.tasks.add_task(
            self.fastmail.send_message,
            message=MessageSchema(
                recipients=recipients,
                subject=subject,
                template_body=context,
                subtype=MessageType.html,
            ),
            template_name=template_name,
        )

    async def send_sms(self, to: str, body: str):
        # 3. Access the client through the getter.
        # This is called inside an 'async' route where the event loop is active.
        client = self._get_twilio_client()
        await client.messages.create_async(
            from_=notification_settings.TWILIO_NUMBER,
            to=to,
            body=body,
        )