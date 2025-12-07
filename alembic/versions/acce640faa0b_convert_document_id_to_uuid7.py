"""convert_document_id_to_uuid7

Revision ID: acce640faa0b
Revises:
Create Date: 2025-12-07 17:50:32.931326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'acce640faa0b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing documents table
    # WARNING: This will delete all existing data
    op.drop_table('documents')

    # Recreate documents table with UUID7 primary key
    op.create_table(
        'documents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('document_type', sa.String(), nullable=True),
        sa.Column('extracted_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create index on id column
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)


def downgrade() -> None:
    # Drop the UUID-based documents table
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')

    # Recreate documents table with integer primary key
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('document_type', sa.String(), nullable=True),
        sa.Column('extracted_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create index on id column
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
