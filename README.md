# chatterbox-backend

This is the backend for the Chatterbox project. Uses FastAPI as the backend framework and Prisma as the ORM.

## Installation

- install `uv` [here](https://docs.astral.sh/uv/getting-started/installation/#homebrew) for dependency management
- use python 3.12 if you don't have it
  - `uv python install 3.12.9`
- activate the venv
  - `uv venv` to create the venv
  - `source .venv/bin/activate` to use the venv
- run `uv sync` within the virtual environment to sync the dependencies from the uv.lock file into your virtual environment

## Development

- You should always be in the virtual environment when developing e.g. this `(chatterbox-backend) $` should be present in your terminal
- Activate the virtual environment if you are not already in it
  - `source .venv/bin/activate`
- Load the environment variables using direnv. Install direnv if you don't have it [here](https://direnv.net/docs/installation.html)
  - `direnv allow .`
- `uvicorn app.main:app --reload` to start the development server

## Prisma

### Updating the schema

- Edit the schema in `prisma/schema.prisma`
- Run `prisma db push` to generate the Prisma client and push the schema to the database
- Run `prisma generate` to update the schema to the Prisma client i.e. to have the latest types for the client for code completion while developing
