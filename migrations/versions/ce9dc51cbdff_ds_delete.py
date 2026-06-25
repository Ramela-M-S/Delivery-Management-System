"""ds delete

Revision ID: ce9dc51cbdff
Revises: acbfebcdd5f1
Create Date: 2026-06-25 10:03:06.176399

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce9dc51cbdff'
down_revision: Union[str, Sequence[str], None] = 'acbfebcdd5f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
               DELETE
               FROM shipment_tag
               WHERE shipment_id IN (SELECT id FROM shipment WHERE seller_id = '0c7abbf0-57d5-4d9f-a167-88a53465a169');
               """)

    # 2. Delete shipment events
    op.execute("""
               DELETE
               FROM shipment_event
               WHERE shipment_id IN (SELECT id FROM shipment WHERE seller_id = '0c7abbf0-57d5-4d9f-a167-88a53465a169');
               """)

    # 3. Delete reviews (if your schema has them, you must clear these before shipments)
    op.execute("""
               DELETE
               FROM review
               WHERE shipment_id IN (SELECT id FROM shipment WHERE seller_id = '0c7abbf0-57d5-4d9f-a167-88a53465a169');
               """)

    # 4. Delete the shipments
    op.execute("""
               DELETE
               FROM shipment
               WHERE seller_id = '0c7abbf0-57d5-4d9f-a167-88a53465a169';
               """)

    # 5. Finally, delete the seller
    op.execute("""
               DELETE
               FROM seller
               WHERE id = '0c7abbf0-57d5-4d9f-a167-88a53465a169';
               """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
