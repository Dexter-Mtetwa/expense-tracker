from alembic import op


# revision identifiers, used by Alembic.
revision = "initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('USER', 'ADMIN')) DEFAULT 'USER',
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    op.execute("""
        CREATE TABLE categories (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            creator UUID NOT NULL REFERENCES users(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    op.execute("""
        CREATE UNIQUE INDEX categories_name_unique
        ON categories (LOWER(TRIM(name)));
    """)

    op.execute("""
        CREATE TABLE expenses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            description TEXT NULL,
            amount NUMERIC(12,2) NOT NULL CHECK (amount > 0),
            date DATE NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            category_id UUID NOT NULL REFERENCES categories(id) ON DELETE RESTRICT
        );
    """)

    op.execute("""
        CREATE INDEX expenses_user_id_idx
        ON expenses (user_id);
    """)

    op.execute("""
        CREATE INDEX expenses_category_id_idx
        ON expenses (category_id);
    """)


def downgrade():
    op.execute("DROP TABLE expenses;")
    op.execute("DROP INDEX categories_name_unique;")
    op.execute("DROP TABLE categories;")
    op.execute("DROP TABLE users;")