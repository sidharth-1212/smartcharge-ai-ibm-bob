"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-05-15 16:17:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create telemetry table
    op.create_table(
        'telemetry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('solar_generation_kw', sa.Float(), nullable=False),
        sa.Column('solar_capacity_kw', sa.Float(), nullable=False),
        sa.Column('grid_price_per_kwh', sa.Float(), nullable=False),
        sa.Column('grid_carbon_intensity', sa.Float(), nullable=True),
        sa.Column('battery_soc_percent', sa.Float(), nullable=False),
        sa.Column('battery_capacity_kwh', sa.Float(), nullable=False),
        sa.Column('battery_health_percent', sa.Float(), nullable=True),
        sa.Column('charging_power_kw', sa.Float(), nullable=False),
        sa.Column('charging_mode', sa.String(length=50), nullable=True),
        sa.Column('temperature_celsius', sa.Float(), nullable=True),
        sa.Column('cloud_cover_percent', sa.Float(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telemetry_id'), 'telemetry', ['id'], unique=False)
    op.create_index(op.f('ix_telemetry_timestamp'), 'telemetry', ['timestamp'], unique=False)

    # Create decisions table
    op.create_table(
        'decisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.String(length=100), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('charging_mode', sa.String(length=50), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('estimated_time_hours', sa.Float(), nullable=True),
        sa.Column('renewable_percentage', sa.Float(), nullable=True),
        sa.Column('telemetry_id', sa.Integer(), nullable=True),
        sa.Column('applied', sa.Boolean(), nullable=True),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('overridden', sa.Boolean(), nullable=True),
        sa.Column('override_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['telemetry_id'], ['telemetry.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decisions_id'), 'decisions', ['id'], unique=False)
    op.create_index(op.f('ix_decisions_request_id'), 'decisions', ['request_id'], unique=True)
    op.create_index(op.f('ix_decisions_timestamp'), 'decisions', ['timestamp'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('preferred_charging_mode', sa.String(length=50), nullable=True),
        sa.Column('max_charging_cost_per_day', sa.Float(), nullable=True),
        sa.Column('min_battery_soc_percent', sa.Float(), nullable=True),
        sa.Column('target_battery_soc_percent', sa.Float(), nullable=True),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=True),
        sa.Column('notification_email', sa.String(length=255), nullable=True),
        sa.Column('preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=True)

    # Create charging_sessions table
    op.create_table(
        'charging_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('energy_delivered_kwh', sa.Float(), nullable=True),
        sa.Column('energy_from_solar_kwh', sa.Float(), nullable=True),
        sa.Column('energy_from_grid_kwh', sa.Float(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.Column('average_price_per_kwh', sa.Float(), nullable=True),
        sa.Column('starting_soc_percent', sa.Float(), nullable=True),
        sa.Column('ending_soc_percent', sa.Float(), nullable=True),
        sa.Column('soc_gained_percent', sa.Float(), nullable=True),
        sa.Column('charging_modes_used', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('decisions_count', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_charging_sessions_id'), 'charging_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_charging_sessions_session_id'), 'charging_sessions', ['session_id'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_charging_sessions_session_id'), table_name='charging_sessions')
    op.drop_index(op.f('ix_charging_sessions_id'), table_name='charging_sessions')
    op.drop_table('charging_sessions')
    
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    op.drop_index(op.f('ix_decisions_timestamp'), table_name='decisions')
    op.drop_index(op.f('ix_decisions_request_id'), table_name='decisions')
    op.drop_index(op.f('ix_decisions_id'), table_name='decisions')
    op.drop_table('decisions')
    
    op.drop_index(op.f('ix_telemetry_timestamp'), table_name='telemetry')
    op.drop_index(op.f('ix_telemetry_id'), table_name='telemetry')
    op.drop_table('telemetry')

# Made with Bob
