# chatterbox-backend

This is the backend for the Chatterbox project. Uses FastAPI as the backend framework and SQLAlchemy as the ORM.

## Set up environment variables

- `cp .envrc.example .envrc`
- `direnv allow .`
  Fill in the environment variables in the `.envrc` file.

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
- `uv run uvicorn app.main:app --reload` to start the development server

- use the following to get a cognito token
- aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id ${COGNITO_CLIENT_ID} \
  --auth-parameters USERNAME=${username},PASSWORD=${password} \
  --query 'AuthenticationResult.AccessToken' \
 --output text