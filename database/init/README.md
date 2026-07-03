# database/init/

Optional Postgres init SQL scripts (e.g. extensions) mounted into the `postgres` container's
`/docker-entrypoint-initdb.d/`. Empty for this pass — the schema is fully managed by Alembic
migrations in `backend/alembic/versions/`.
