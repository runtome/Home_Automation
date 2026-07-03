# docker/

Service Dockerfiles live next to their source: `backend/Dockerfile` and `frontend/Dockerfile`. This
folder is reserved for shared Docker helpers (e.g. multi-stage build fragments, `.dockerignore`
templates) if the project outgrows per-service Dockerfiles.
