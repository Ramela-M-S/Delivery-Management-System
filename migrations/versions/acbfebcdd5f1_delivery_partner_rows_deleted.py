"""delivery partner rows deleted

Revision ID: acbfebcdd5f1
Revises: 4bd28ce3eb25
Create Date: 2026-06-25 09:55:02.868575

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acbfebcdd5f1'
down_revision: Union[str, Sequence[str], None] = '4bd28ce3eb25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DELETE FROM servicable_location;")

    # 2. Update shipments to NULL or delete them
    # Note: If shipments are linked to delivery partners, you must handle them.
    # If they are NOT nullable, you must delete the shipments first.
    op.execute("DELETE FROM shipment;")

    # 3. Finally, delete all delivery partners
    op.execute("DELETE FROM delivery_partner;")


def downgrade() -> None:
    """Downgrade schema."""
    pass
