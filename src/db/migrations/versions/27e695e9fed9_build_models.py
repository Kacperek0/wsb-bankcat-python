"""build models

Revision ID: 27e695e9fed9
Revises: 
Create Date: 2022-12-24 13:15:13.797981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27e695e9fed9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_name', table_name='users')
    op.drop_index('ix_users_surname', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_budgets_id', table_name='budgets')
    op.drop_index('ix_budgets_value', table_name='budgets')
    op.drop_table('budgets')
    op.drop_index('ix_categories_id', table_name='categories')
    op.drop_index('ix_categories_name', table_name='categories')
    op.drop_table('categories')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('categories_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('budget_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['budget_id'], ['budgets.id'], name='categories_budget_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='categories_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='categories_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_categories_name', 'categories', ['name'], unique=False)
    op.create_index('ix_categories_id', 'categories', ['id'], unique=False)
    op.create_table('budgets',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('value', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('category_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='budgets_category_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='budgets_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='budgets_pkey')
    )
    op.create_index('ix_budgets_value', 'budgets', ['value'], unique=False)
    op.create_index('ix_budgets_id', 'budgets', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('surname', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey')
    )
    op.create_index('ix_users_surname', 'users', ['surname'], unique=False)
    op.create_index('ix_users_name', 'users', ['name'], unique=False)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    # ### end Alembic commands ###
