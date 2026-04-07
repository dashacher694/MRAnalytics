# Database Migrations Guide

## Overview
MRAnalytics uses Alembic for database schema management. This guide covers all migration operations.

## Setup

### Initial Setup
```bash
# Install dependencies
make install

# Initialize database and run migrations
make db-init
```

### Environment Configuration
The project supports both SQLite (development) and PostgreSQL (production):

**Development (.env):**
```env
DATABASE_URL=sqlite:///./data/mr_analytics.db
```

**Production (.env):**
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mr_analytics
```

## Migration Commands

### Create New Migration
```bash
# Create migration with message
make migration-revision MSG="Add new table for user settings"

# Or directly with alembic
alembic revision --autogenerate -m "Add user settings table"
```

### Run Migrations
```bash
# Run all pending migrations
make migrate

# Or directly with alembic
alembic upgrade head
```

### Rollback Migration
```bash
# Rollback last migration
make migration-down

# Rollback to specific revision
alembic downgrade <revision_id>
```

### Migration Status
```bash
# Show current migration
make migration-current

# Show migration history
make migration-history
```

## Migration Files Structure

```
migrations/
|-- versions/
|   |-- 001_initial.py          # Initial migration
|   |-- 002_add_user_settings.py # User settings migration
|   |-- __init__.py
|-- env.py                      # Alembic environment configuration
|-- script.py.mako              # Migration template
|-- README.md                   # This file
```

## Writing Migrations

### Manual Migration
```python
"""Add user preferences table

Revision ID: 002_add_user_preferences
Revises: 001_initial
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_add_user_preferences'
down_revision = '001_initial'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('theme', sa.String(), nullable=True),
        sa.Column('notifications_enabled', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'])

def downgrade() -> None:
    # Drop table
    op.drop_table('user_preferences')
```

### Auto-generated Migration
```bash
# After changing models, run:
make migration-revision MSG="Update metrics table with new columns"
```

## Best Practices

### 1. Always Review Auto-generated Migrations
Auto-generated migrations may include:
- Unnecessary column drops
- Incorrect constraint changes
- Missing indexes

### 2. Use Descriptive Messages
```bash
# Good
make migration-revision MSG="Add index on metrics.author for performance"

# Bad
make migration-revision MSG="new migration"
```

### 3. Test Migrations
```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test upgrade again
alembic upgrade head
```

### 4. Never Modify Existing Migrations
- Always create new migrations instead of modifying existing ones
- If a migration is wrong, create a new migration to fix it

### 5. Use Reversible Operations
```python
def upgrade() -> None:
    op.add_column('metrics', sa.Column('new_field', sa.String()))

def downgrade() -> None:
    op.drop_column('metrics', 'new_field')
```

## Data Migrations

### Simple Data Migration
```python
def upgrade() -> None:
    # Add new column
    op.add_column('metrics', sa.Column('status', sa.String(), default='active'))
    
    # Update existing data
    op.execute("UPDATE metrics SET status = 'active' WHERE status IS NULL")

def downgrade() -> None:
    op.drop_column('metrics', 'status')
```

### Complex Data Migration
```python
from sqlalchemy.orm import sessionmaker
from alembic import op

def upgrade() -> None:
    # Get bind for session
    bind = op.get_bind()
    session = sessionmaker(bind=bind)()
    
    try:
        # Add new column
        op.add_column('metrics', sa.Column('calculated_score', sa.Float()))
        
        # Calculate and update scores
        from src.persistance.mr_metrics.entity import MRMetricsModel
        metrics = session.query(MRMetricsModel).all()
        
        for metric in metrics:
            metric.calculated_score = calculate_score(metric)
        
        session.commit()
    finally:
        session.close()
```

## Troubleshooting

### Migration History Conflicts
```bash
# Check current state
make migration-current

# Check for conflicts
alembic heads

# Resolve conflicts by creating new migration
make migration-revision MSG="Resolve migration conflicts"
```

### Database Lock Issues
```bash
# For SQLite, ensure no connections are active
# For PostgreSQL, check for active locks
SELECT * FROM pg_locks WHERE relation IS NOT NULL;
```

### Migration Performance
For large tables:
```python
def upgrade() -> None:
    # Add column as nullable first
    op.add_column('metrics', sa.Column('new_field', sa.String(), nullable=True))
    
    # Update data in batches
    connection = op.get_bind()
    for offset in range(0, 1000000, 1000):
        connection.execute(
            "UPDATE metrics SET new_field = 'default' WHERE id >= %s AND id < %s",
            (offset, offset + 1000)
        )
    
    # Make column non-nullable after data update
    op.alter_column('metrics', 'new_field', nullable=False)
```

## Integration with Application

### Application Startup
```python
# In your application startup
async def init_app():
    # Run migrations automatically (optional)
    if settings.auto_migrate:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
```

### Testing
```python
# In test setup
@pytest.fixture
async def test_db():
    # Create test database
    test_engine = create_engine("sqlite:///:memory:")
    
    # Run migrations on test database
    with test_engine.begin() as conn:
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations
        
        migration_context = MigrationContext.configure(conn)
        operations = Operations(migration_context)
        
        # Run migrations programmatically
        # ... migration logic
        
    yield test_engine
```

## Production Deployment

### Pre-deployment Checklist
1. **Backup database**
2. **Test migrations on staging**
3. **Review migration files**
4. **Plan rollback strategy**

### Deployment Steps
```bash
# 1. Deploy new code
# 2. Run migrations
make migrate

# 3. Verify application works
# 4. If issues, rollback
make migration-down
```

### Zero-Downtime Migrations
For critical production databases:
1. Add new columns as nullable
2. Deploy code that handles both old/new schema
3. Backfill data
4. Make columns non-nullable
5. Remove old code paths

This approach ensures your database schema evolves safely and predictably.
