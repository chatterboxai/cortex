# Cortex

This is the backend for the Chatterbox project. Uses FastAPI as the backend framework and SQLAlchemy as the ORM.

## Development

### Set up environment variables

We use direnv to manage environment variables, it can be installed [here](https://direnv.net/docs/installation.html)

- `cp .envrc.example .envrc`
- `direnv allow .`
  Fill in the environment variables in the `.envrc` file.

### Installation

#### Prerequisites

- Install `uv` [here](https://docs.astral.sh/uv/getting-started/installation/#homebrew) for dependency management
- use python 3.12 if you don't have it
  - `uv python install 3.12.9`
- activate the venv
  - `uv venv` to create the venv
  - `source .venv/bin/activate` to use the venv
- run `uv sync` within the virtual environment to sync the dependencies from the uv.lock file into your virtual environment

### Running the development server

- You should always be in the virtual environment when developing e.g. this `(cortex) $` should be present in your terminal
- Activate the virtual environment if you are not already in it
  - `source .venv/bin/activate`
- Load the environment variables using `direnv allow .`
- `fastapi dev app/main.py` to start the development server. This will automatically reload when you make changes to the code.

### Getting a Cognito token

- Use the following to get a cognito access token to simulate a user login to access authenticated endpoints

```sh
aws cognito-idp initiate-auth \
   --auth-flow USER_PASSWORD_AUTH \
   --client-id ${COGNITO_CLIENT_ID} \
  --auth-parameters USERNAME=${username},PASSWORD=${password} \
   --query 'AuthenticationResult.AccessToken' \
  --output text
```

## Running Celery

We use Celery to run background tasks and a celery beat to schedule tasks e.g. syncs dialogues and documents uploaded to the vector store at a fixed interval.

### Command to start the celery worker

Run this in the virtual environment in a separate terminal

```sh
celery -A app.core.celery worker --loglevel=info
```

### Command to start the celery beat

Run this in the virtual environment in a separate terminal

```sh
celery -A app.core.celery beat --loglevel=info
```
