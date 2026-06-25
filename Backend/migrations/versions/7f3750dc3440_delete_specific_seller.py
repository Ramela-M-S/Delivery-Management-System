"""delete_specific_seller

Revision ID: 7f3750dc3440
Revises: 42a57e5382f2
Create Date: 2026-06-25 08:52:02.436555

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f3750dc3440'
down_revision: Union[str, Sequence[str], None] = '42a57e5382f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
               DELETE
               FROM shipment_tag
               WHERE shipment_id IN (SELECT id FROM shipment WHERE seller_id = '570f9e4e-048f-4b33-b2b1-be8aa6cde0f2');
               """)

    # 2. Delete the next child level (events)
    op.execute("""
               DELETE
               FROM shipment_event
               WHERE shipment_id IN (SELECT id FROM shipment WHERE seller_id = '570f9e4e-048f-4b33-b2b1-be8aa6cde0f2');
               """)

    # 3. Delete the parent of those children (shipments)
    op.execute("""
               DELETE
               FROM shipment
               WHERE seller_id = '570f9e4e-048f-4b33-b2b1-be8aa6cde0f2';
               """)

    # 4. Finally, delete the seller
    op.execute("""
               DELETE
               FROM seller
               WHERE id = '570f9e4e-048f-4b33-b2b1-be8aa6cde0f2';
               """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
