from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status, Form
from fastapi.templating import Jinja2Templates

from app.utils import TEMPLATE_DIR, generate_url_safe_token, decode_url_safe_token

from ..dependencies import DeliveryPartnerDep, SellerDep, ShipmentServiceDep, SessionDep
from ..schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate
from ...config import app_settings
from ...database.models import TagName

router = APIRouter(prefix="/shipment", tags=["Shipment"])


templates = Jinja2Templates(TEMPLATE_DIR)


### Tracking details of shipment
@router.get("/track")
async def get_tracking(request: Request, id: UUID, service: ShipmentServiceDep):
    # Check for shipment with given id
    shipment = await service.get(id)

    context = shipment.model_dump()
    context["status"] = shipment.status
    context["partner"] = shipment.delivery_partner.name
    context["timeline"] = shipment.timeline
    context["timeline"].reverse()

    return templates.TemplateResponse(
        request=request,
        name="track.html",
        context=context,
    )


### Read a shipment by id
@router.get("/", response_model=ShipmentRead)
async def get_shipment(id: UUID, service: ShipmentServiceDep):
    # Check for shipment with given id
    shipment = await service.get(id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesn't exist!",
        )

    return shipment


### Create a new shipment
@router.post("/", response_model=ShipmentRead)
async def submit_shipment(
    seller: SellerDep,
    shipment: ShipmentCreate,
    service: ShipmentServiceDep,
):
    return await service.add(shipment, seller)


### Update fields of a shipment
@router.patch("/", response_model=ShipmentRead)
async def update_shipment(
    id: UUID,
    shipment_update: ShipmentUpdate,
    partner: DeliveryPartnerDep,
    service: ShipmentServiceDep,
):
    # Update data with given fields
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    return await service.update(id, shipment_update, partner)


### Cancel a shipment by id
@router.get("/cancel", response_model=ShipmentRead)
async def cancel_shipment(
    id: UUID,
    seller: SellerDep,
    service: ShipmentServiceDep,
):
    return await service.cancel(id, seller)


@router.post("/review")
async def submit_review(
        token: str,
        rating: Annotated[int, Form(ge=1, le=5)],
        comment: Annotated[str | None, Form()],
        service: ShipmentServiceDep,
):
    # Use the DECODE function
    print(f"DEBUG: Received token type: {type(token)}, value: {token}")

    token_str = str(token)
    payload = decode_url_safe_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid token")

    shipment_id = payload.get("id")
    await service.rate(str(UUID(shipment_id)), rating, comment)
    return {"detail": "Review submitted successfully"}


### Sumbit a reivew for a shipment
@router.get("/review")
async def submit_review_page(request: Request, token: str):
    # Decode to verify it's valid and get the ID
    payload = decode_url_safe_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid token")

    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={
            "review_url": f"http://{app_settings.APP_DOMAIN}/shipment/review?token={token}",
            "shipment_id": payload.get("id")  # Pass this so the hidden input works
        },
    )


### Add a tag to a shipment
@router.get("/tag", response_model=ShipmentRead)
async def add_tag_to_shipment(
    id: UUID,
    tag_name: TagName,
    service: ShipmentServiceDep,
):
    return await service.add_tag(id, tag_name)


### Remove a tag from a shipment
@router.delete("/tag", response_model=ShipmentRead)
async def remove_tag_from_shipment(
    id: UUID,
    tag_name: TagName,
    service: ShipmentServiceDep,
):
    return await service.remove_tag(id, tag_name)


## Get all shipments with a tag
# @router.get("/tagged", response_model=list[ShipmentRead])
# async def get_shipments_with_tag(
#     tag_name: TagName,
#     session: SessionDep,
# ):
#     tag = await tag_name.tag(session)
#     return tag.shipments