"""Unir las ramas de biblioteca de recetas y area de restaurante.

Revision ID: 9c4e7b2a1d60
Revises: a1b2c3d4e5f6, f7a2c91d6e40
Create Date: 2026-11-19
"""
from typing import Sequence, Union


revision: str = "9c4e7b2a1d60"
down_revision: Union[str, Sequence[str], None] = ("a1b2c3d4e5f6", "f7a2c91d6e40")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
