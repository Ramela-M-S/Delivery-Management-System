from random import randint
from typing import Optional

from app.config import app_settings
from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.database.redis import add_shipment_verification_code
from app.services.base import BaseService
from app.utils import generate_url_safe_token
from app.worker.tasks import send_sms, send_email_with_template


class ShipmentEventService(BaseService):
    def __init__(self, session):
        super().__init__(ShipmentEvent, session)


    async def add(
            self,
            shipment: Shipment,
            location: Optional[str] = None,  # Changed to str to match your Pydantic schema!
            status: Optional[ShipmentStatus] = None,
            description: Optional[str] = None,
    ) -> ShipmentEvent:

        last_event = await self.get_latest_event(shipment)

        # 1. Resolve Status (Genesis vs Inheritance)
        if status is None:
            status = last_event.status if last_event else ShipmentStatus.PENDING

        # 2. Resolve Location (Genesis vs Inheritance)
        if location is None:
            if last_event:
                location = last_event.location
            else:
                # THE GENESIS BACKSTOP: Default starting point for brand new packages
                location = "Origin Facility"
        new_event = ShipmentEvent(
            location=location,
            status=status,
            description=description
            if description
            else self._generate_description(
                status,
                location,
            ),
            shipment_id=shipment.id,
        )

        await self._notify(shipment, status)

        return await self._add(new_event)

    async def get_latest_event(self, shipment: Shipment):
        timeline = shipment.timeline
        if not shipment.timeline:
            return None
        sorted_timeline = sorted(shipment.timeline, key=lambda e: e.created_at)
        return sorted_timeline[-1]

    def _generate_description(self, status: ShipmentStatus, location: int):
        match status:
            case ShipmentStatus.placed:
                return "assigned delivery partner"
            case ShipmentStatus.out_for_delivery:
                return "shipment out for delivery"
            case ShipmentStatus.delivered:
                return "successfully delivered"
            case ShipmentStatus.cancelled:
                return "cancelled by seller"
            case _:  # and ShipmentStatus.in_transit
                return f"scanned at {location}"

    async def _notify(self, shipment: Shipment, status: ShipmentStatus):

        if status == ShipmentStatus.in_transit:
            return

        # Provided a default subject to prevent UnboundLocalError
        subject: str = f"Update on your order from {shipment.seller.name}"
        status_text = status.name.replace("_", " ").title()

        context = {
            "tracking_url": f"http://{app_settings.APP_DOMAIN}/shipment/track?id={shipment.id}",
            "tracking_id": str(shipment.id)[:8].upper(),
            "seller": shipment.seller.name,
            "partner": shipment.delivery_partner.name,
            "status_text": status_text
        }
        template_name: str = "email.html"

        match status:
            case ShipmentStatus.placed:
                subject = "Your Order is Placed 🚛"

            case ShipmentStatus.out_for_delivery:
                subject = "Your Order is Arriving Soon 🛵"

                code = randint(100000, 999999)
                await add_shipment_verification_code(shipment.id, code)

                if shipment.client_contact_phone:
                    send_sms.delay(
                        to=shipment.client_contact_phone,
                        body=f"Your order is arriving soon! Share the {code} code with your "
                             "delivery executive to receive your package."
                    )
                else:
                    context["verification_code"] = code

            case ShipmentStatus.delivered:
                subject = "Your Order is Delivered ✅"
                token = generate_url_safe_token({"id": str(shipment.id)})
                context["review_url"] = f"http://{app_settings.APP_DOMAIN}/shipment/review?token={token}"

            case ShipmentStatus.cancelled:
                subject = "Your Order is Cancelled ❌"

        # Fixed the indentation so it aligns perfectly with the logic flow
        send_email_with_template.delay(
            recipients=[shipment.client_contact_email],
            subject=subject,
            context=context,
            template_name=template_name,
        )