"""crear_tablas_iniciales_sprint_1

Revision ID: 0001_sprint_1
Revises: 
Create Date: 2026-09-26 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_sprint_1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tabla: rol
    op.create_table(
        'rol',
        sa.Column('id_rol', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(length=50), nullable=False),
        sa.Column('descripcion', sa.String(length=255), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id_rol', name='pk_rol')
    )
    op.create_index(op.f('ix_rol_nombre'), 'rol', ['nombre'], unique=True)

    # 2. Tabla: ubicacion
    op.create_table(
        'ubicacion',
        sa.Column('id_ubicacion', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('direccion', sa.String(length=255), nullable=False),
        sa.Column('zona', sa.String(length=100), nullable=True),
        sa.Column('ciudad', sa.String(length=100), nullable=False),
        sa.Column('latitud', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitud', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('referencia', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id_ubicacion', name='pk_ubicacion')
    )

    # 3. Tabla: categoria
    op.create_table(
        'categoria',
        sa.Column('id_categoria', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.String(length=255), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id_categoria', name='pk_categoria')
    )
    op.create_index(op.f('ix_categoria_nombre'), 'categoria', ['nombre'], unique=True)

    # 4. Tabla: preferencia
    op.create_table(
        'preferencia',
        sa.Column('id_preferencia', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=True),
        sa.Column('descripcion', sa.String(length=255), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id_preferencia', name='pk_preferencia')
    )
    op.create_index(op.f('ix_preferencia_nombre'), 'preferencia', ['nombre'], unique=True)

    # 5. Tabla: ingrediente
    op.create_table(
        'ingrediente',
        sa.Column('id_ingrediente', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('unidad_medida', sa.String(length=50), nullable=False),
        sa.Column('precio_estimado', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('descripcion', sa.String(length=255), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=False, server_default='ACTIVO'),
        sa.CheckConstraint('precio_estimado IS NULL OR precio_estimado >= 0', name='chk_ingrediente_precio_estimado_no_negativo'),
        sa.PrimaryKeyConstraint('id_ingrediente', name='pk_ingrediente')
    )
    op.create_index(op.f('ix_ingrediente_nombre'), 'ingrediente', ['nombre'], unique=True)

    # 6. Tabla: usuario
    op.create_table(
        'usuario',
        sa.Column('id_usuario', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombres', sa.String(length=100), nullable=False),
        sa.Column('apellidos', sa.String(length=100), nullable=False),
        sa.Column('correo', sa.String(length=150), nullable=False),
        sa.Column('contrasena_hash', sa.String(length=255), nullable=False),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=False, server_default='ACTIVO'),
        sa.Column('fecha_registro', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id_rol', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_rol'], ['rol.id_rol'], name='fk_usuario_id_rol', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id_usuario', name='pk_usuario')
    )
    op.create_index(op.f('ix_usuario_correo'), 'usuario', ['correo'], unique=True)

    # 7. Tabla: restaurante
    op.create_table(
        'restaurante',
        sa.Column('id_restaurante', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(length=150), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('nit', sa.String(length=30), nullable=True),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('correo', sa.String(length=150), nullable=True),
        sa.Column('horario_apertura', sa.Time(), nullable=True),
        sa.Column('horario_cierre', sa.Time(), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=False, server_default='ACTIVO'),
        sa.Column('fecha_registro', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id_usuario_responsable', sa.Integer(), nullable=False),
        sa.Column('id_ubicacion', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_ubicacion'], ['ubicacion.id_ubicacion'], name='fk_restaurante_id_ubicacion', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['id_usuario_responsable'], ['usuario.id_usuario'], name='fk_restaurante_id_usuario_responsable', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id_restaurante', name='pk_restaurante'),
        sa.UniqueConstraint('nit', name='uq_restaurante_nit')
    )
    op.create_index(op.f('ix_restaurante_nombre'), 'restaurante', ['nombre'], unique=False)

    # 8. Tabla: plato
    op.create_table(
        'plato',
        sa.Column('id_plato', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(length=150), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('precio', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('tipo_comida', sa.String(length=50), nullable=True),
        sa.Column('personas_cubiertas', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('disponible', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('estado', sa.String(length=20), nullable=False, server_default='ACTIVO'),
        sa.Column('fecha_registro', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id_restaurante', sa.Integer(), nullable=False),
        sa.Column('id_categoria', sa.Integer(), nullable=False),
        sa.CheckConstraint('precio >= 0', name='chk_plato_precio_no_negativo'),
        sa.CheckConstraint('personas_cubiertas > 0', name='chk_plato_personas_cubiertas_mayor_cero'),
        sa.ForeignKeyConstraint(['id_categoria'], ['categoria.id_categoria'], name='fk_plato_id_categoria', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['id_restaurante'], ['restaurante.id_restaurante'], name='fk_plato_id_restaurante', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_plato', name='pk_plato')
    )
    op.create_index(op.f('ix_plato_nombre'), 'plato', ['nombre'], unique=False)

    # 9. Tabla: plato_ingrediente
    op.create_table(
        'plato_ingrediente',
        sa.Column('id_plato_ingrediente', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cantidad', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('unidad_medida', sa.String(length=50), nullable=False),
        sa.Column('id_plato', sa.Integer(), nullable=False),
        sa.Column('id_ingrediente', sa.Integer(), nullable=False),
        sa.CheckConstraint('cantidad > 0', name='chk_plato_ingrediente_cantidad_mayor_cero'),
        sa.ForeignKeyConstraint(['id_ingrediente'], ['ingrediente.id_ingrediente'], name='fk_plato_ingrediente_id_ingrediente', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['id_plato'], ['plato.id_plato'], name='fk_plato_ingrediente_id_plato', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_plato_ingrediente', name='pk_plato_ingrediente'),
        sa.UniqueConstraint('id_plato', 'id_ingrediente', name='uq_plato_ingrediente')
    )

    # 10. Tabla: usuario_preferencia
    op.create_table(
        'usuario_preferencia',
        sa.Column('id_usuario_preferencia', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('id_preferencia', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_preferencia'], ['preferencia.id_preferencia'], name='fk_usuario_preferencia_id_preferencia', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], name='fk_usuario_preferencia_id_usuario', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_usuario_preferencia', name='pk_usuario_preferencia'),
        sa.UniqueConstraint('id_usuario', 'id_preferencia', name='uq_usuario_preferencia')
    )

    # Inserción idempotente de los roles iniciales del sistema
    op.execute(
        """
        INSERT INTO rol (nombre, descripcion, activo)
        VALUES 
            ('CLIENTE', 'Usuario consumidor de la plataforma', true),
            ('RESTAURANTE', 'Representante o administrador de restaurante gastronómico', true),
            ('ADMINISTRADOR', 'Administrador global del sistema MenuOpt', true)
        ON CONFLICT (nombre) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.drop_table('usuario_preferencia')
    op.drop_table('plato_ingrediente')
    op.drop_index(op.f('ix_plato_nombre'), table_name='plato')
    op.drop_table('plato')
    op.drop_index(op.f('ix_restaurante_nombre'), table_name='restaurante')
    op.drop_table('restaurante')
    op.drop_index(op.f('ix_usuario_correo'), table_name='usuario')
    op.drop_table('usuario')
    op.drop_index(op.f('ix_ingrediente_nombre'), table_name='ingrediente')
    op.drop_table('ingrediente')
    op.drop_index(op.f('ix_preferencia_nombre'), table_name='preferencia')
    op.drop_table('preferencia')
    op.drop_index(op.f('ix_categoria_nombre'), table_name='categoria')
    op.drop_table('categoria')
    op.drop_table('ubicacion')
    op.drop_index(op.f('ix_rol_nombre'), table_name='rol')
    op.drop_table('rol')
