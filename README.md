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

#### Starting the database

```bash
docker compose up -d
```

#### Start the web server

```bash
fastapi dev app/main.py
```

#### Running the temporal server

Open another terminal and run the following command to start the temporal server

```bash
temporal server start-dev
```

#### Running the temporal worker

```bash
chmod +x app/temporal/run_worker.sh
app/temporal/run_worker.sh
```

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

### running the test cases

- Activate the virtual environment if you are not already in it
  - `source .venv/bin/activate`
- run `uv pip install -e ".[dev]"`
- run `pytest`
- current tests that work is test get user profile, test create chatbot valid and invalid

<<<<<<< HEAD

### Scenario walkthrough

=======

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

### running the test cases

- Activate the virtual environment if you are not already in it
  - `source .venv/bin/activate`
- run `uv pip install -e ".[dev]"`
- run `pytest`
- current tests that work is test get user profile, test create chatbot valid and invalid
  > > > > > > > df70495 (added test stuff running to readme)

### running the test cases

- Activate the virtual environment if you are not already in it
  - `source .venv/bin/activate`
- run `uv pip install -e ".[dev]"`
- run `pytest`
- current tests that work is test get user profile, test create chatbot valid and invalid
  > > > > > > > df70495 (added test stuff running to readme)

### running the test cases

- Activate the virtual environment if you are not already in it
  - `source .venv/bin/activate`
- run `uv pip install -e ".[dev]"`
- run `pytest`
- current tests that work is test get user profile, test create chatbot valid and invalid
