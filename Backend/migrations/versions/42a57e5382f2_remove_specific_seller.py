"""remove_specific_seller

Revision ID: 42a57e5382f2
Revises: 859b847a087c
Create Date: 2026-06-25 08:26:31.683483

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42a57e5382f2'
down_revision: Union[str, Sequence[str], None] = '859b847a087c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
               DELETE
               FROM shipment_tag
               WHERE shipment_id IN (SELECT id FROM shipment WHERE seller_id = '95936fb3-ef34-4c4a-ac44-b9685b37e79d');
               """)

    # 2. Delete the next child level (events)
    op.execute("""
               DELETE
               FROM shipment_event
               WHERE shipment_id IN (SELECT id FROM shipment WHERE seller_id = '95936fb3-ef34-4c4a-ac44-b9685b37e79d');
               """)

    # 3. Delete the parent of those children (shipments)
    op.execute("""
               DELETE
               FROM shipment
               WHERE seller_id = '95936fb3-ef34-4c4a-ac44-b9685b37e79d';
               """)

    # 4. Finally, delete the seller
    op.execute("""
               DELETE
               FROM seller
               WHERE id = '95936fb3-ef34-4c4a-ac44-b9685b37e79d';
               """)

def downgrade() -> None:
    """Downgrade schema."""
    pass
