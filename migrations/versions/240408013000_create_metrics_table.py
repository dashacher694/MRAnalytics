"""
Create metrics table for MR Analytics

Creates the metrics table with UUID primary key, timestamp fields,
and indexes for efficient querying by mr_iid, author, and created_at.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '240408013000'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create metrics table with UUID primary key and timestamp fields
    op.create_table(
        'metrics',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('modifiedon', sa.DateTime(timezone=True), nullable=True),
        sa.Column('mr_iid', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('author', sa.String(), nullable=False),
        sa.Column('merged_at', sa.DateTime(), nullable=False),
        sa.Column('web_url', sa.String(), nullable=False),
        sa.Column('additions', sa.Integer(), nullable=True),
        sa.Column('deletions', sa.Integer(), nullable=True),
        sa.Column('time_to_merge', sa.Float(), nullable=True),
        sa.Column('review_rounds', sa.Integer(), nullable=True),
        sa.Column('comment_density', sa.Float(), nullable=True),
        sa.Column('formal_approval', sa.Integer(), nullable=True),
        sa.Column('response_time_hours', sa.Float(), nullable=True),
        sa.Column('num_comments', sa.Integer(), nullable=True),
        sa.Column('num_approvals', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('mr_iid')
    )
    op.create_index(op.f('ix_metrics_mr_iid'), 'metrics', ['mr_iid'], unique=False)
    op.create_index(op.f('ix_metrics_author'), 'metrics', ['author'], unique=False)
    op.create_index(op.f('ix_metrics_created_at'), 'metrics', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_metrics_created_at'), table_name='metrics')
    op.drop_index(op.f('ix_metrics_author'), table_name='metrics')
    op.drop_index(op.f('ix_metrics_mr_iid'), table_name='metrics')
    op.drop_table('metrics')
