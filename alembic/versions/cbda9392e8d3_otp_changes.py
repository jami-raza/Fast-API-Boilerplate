"""otp changes

Revision ID: cbda9392e8d3
Revises: dbfab3d0e467
Create Date: 2025-05-02 11:06:55.926134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cbda9392e8d3'
down_revision: Union[str, None] = 'dbfab3d0e467'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop indexes and devices table
    op.drop_index('ix_devices_device_id', table_name='devices')
    op.drop_index('ix_devices_token', table_name='devices')
    op.drop_table('devices')

    # Drop old reset token columns
    op.drop_column('users', 'reset_token')
    op.drop_column('users', 'reset_token_expiry')

    # Add new OTP-related columns
    op.add_column('users', sa.Column('otp_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('otp_token_expiry', sa.DateTime(), nullable=True))

    # Define and create enum
    otp_enum = sa.Enum('REGISTER', 'FORGOT', name='otp_enum')
    otp_enum.create(op.get_bind(), checkfirst=True)

    # Step 1: Add nullable otp_type with default
    op.add_column(
        'users',
        sa.Column('otp_type', otp_enum, nullable=True, server_default='REGISTER')
    )

    # Step 2: Set existing null values to 'REGISTER'
    op.execute("UPDATE users SET otp_type = 'REGISTER' WHERE otp_type IS NULL")

    # Step 3: Alter column to NOT NULL and remove default
    op.alter_column('users', 'otp_type', nullable=False, server_default=None)


def downgrade() -> None:
    # Revert OTP fields
    op.add_column('users', sa.Column('reset_token_expiry', postgresql.TIMESTAMP(), nullable=True))
    op.add_column('users', sa.Column('reset_token', sa.VARCHAR(), nullable=True))
    op.drop_column('users', 'otp_type')
    op.drop_column('users', 'otp_token_expiry')
    op.drop_column('users', 'otp_token')

    # Recreate devices table
    op.create_table(
        'devices',
        sa.Column('token', sa.VARCHAR(), nullable=False),
        sa.Column('user_id', sa.INTEGER(), nullable=False),
        sa.Column('device_name', sa.VARCHAR(), nullable=True),
        sa.Column('device_id', sa.VARCHAR(), nullable=True),
        sa.Column('mac_address', sa.VARCHAR(), nullable=True),
        sa.Column('ip_address', sa.VARCHAR(), nullable=True),
        sa.Column('location', sa.VARCHAR(), nullable=True),
        sa.Column('expires_at', postgresql.TIMESTAMP(), nullable=True),
        sa.Column('revoked', sa.BOOLEAN(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='devices_user_id_fkey'),
        sa.PrimaryKeyConstraint('token', name='devices_pkey')
    )
    op.create_index('ix_devices_token', 'devices', ['token'], unique=False)
    op.create_index('ix_devices_device_id', 'devices', ['device_id'], unique=False)

    # Drop enum
    sa.Enum(name='otp_enum').drop(op.get_bind(), checkfirst=True)
