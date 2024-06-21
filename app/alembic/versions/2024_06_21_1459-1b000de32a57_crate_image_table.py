"""Crate image table

Revision ID: 1b000de32a57
Revises: 40593dd5f01e
Create Date: 2024-06-21 14:59:13.674989

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1b000de32a57"
down_revision: Union[str, None] = "40593dd5f01e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "images",
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column(
            "state",
            sa.Enum(
                "INIT",
                "UPLOADED",
                "PROCESSING",
                "DONE",
                "ERROR",
                name="stateenum",
            ),
            nullable=False,
        ),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("original", sa.String(), nullable=True),
        sa.Column("thumb", sa.String(), nullable=True),
        sa.Column("big_thumb", sa.String(), nullable=True),
        sa.Column("big_1920", sa.String(), nullable=True),
        sa.Column("d2500", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("images")
    # ### end Alembic commands ###
