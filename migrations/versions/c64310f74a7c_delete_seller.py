"""DELETE SELLER

Revision ID: c64310f74a7c
Revises: 7f3750dc3440
Create Date: 2026-06-25 09:11:20.091318

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c64310f74a7c'
down_revision: Union[str, Sequence[str], None] = '7f3750dc3440'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Delete associated shipment tags first (link table)
    op.execute("""
               DELETE
               FROM shipment_tag
               WHERE shipment_id IN (SELECT id FROM shipment WHERE seller_id = '2a579216-d8c9-4a85-928f-b8a54b6c0c0b');
               """)

    # 2. Delete shipment events
    op.execute("""
               DELETE
               FROM shipment_event
               WHERE shipment_id IN (SELECT id FROM shipment WHERE seller_id = '2a579216-d8c9-4a85-928f-b8a54b6c0c0b');
               """)

    # 3. Delete reviews (if your schema has them, you must clear these before shipments)
    op.execute("""
               DELETE
               FROM review
               WHERE shipment_id IN (SELECT id FROM shipment WHERE seller_id = '2a579216-d8c9-4a85-928f-b8a54b6c0c0b');
               """)

    # 4. Delete the shipments
    op.execute("""
               DELETE
               FROM shipment
               WHERE seller_id = '2a579216-d8c9-4a85-928f-b8a54b6c0c0b';
               """)

    # 5. Finally, delete the seller
    op.execute("""
               DELETE
               FROM seller
               WHERE id = '2a579216-d8c9-4a85-928f-b8a54b6c0c0b';
               """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
