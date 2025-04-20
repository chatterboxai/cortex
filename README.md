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


### Scenario walkthrough
#### Successful sync
[Success flow video](https://youtu.be/jXOXxauY0-4)

1. User upload file
1. File uploaded to S3, return success to client
1. Start a temporal workflow that:
  1. Generate a presigned S3 url to pass to Mistral OCR API to parse PDF
  1. Convert the parsed pdf text into chunks
  1. Generate embeddings from each chunk
  1. Store the embeddings into vector store
  1. Update the sync status of the document to `Synced`
If there are exceptions e.g. Mistral API rate limit
Retry policy will be carried out by the temporal server.
[Failed retry video](https://youtu.be/5G3DYwdefK8)


#### Chat walkthrough
1. User submits question
1. Question gets passed to agent workflow
1. Agent workflow has its tools (search_info_from_documents) and the agent (function calling LLM) does:
  1. Query decomposition from complex queries into multiple single queries
    1. Routes each query into the right tools to answer the question
  1. Invoke the tools with the question based on the function arguments
1. Keep doing this (invoke the tool with arguments, decide what tool to invoke based on the answer and question to return) until the LLM thinks the tool responses can answer the question
1. Store the answer and tool call responses in the chat store for conversation


#### Rate limiting
Rate limit of 2 request per minute at the chat API endpoint level handled by SlowAPI.

### running the test cases

- Activate the virtual environment if you are not already in it
  - `source .venv/bin/activate`
- run `uv pip install -e ".[dev]"`
- run `pytest`
- current tests that work is test get user profile, test create chatbot valid and invalid
  > > > > > > > df70495 (added test stuff running to readme)


### Technologies
Frontend
1. Typescript
1. Next.js

Backend
1. Python
1. FastAPI (Web server)
1. SQLAlchemy (ORM)
1. Llama Index (RAG Framework)
1. Temporal (Workflow orchestration) To handle syncing of documents uploaded into vector store and easy configuration of retry policies in the event of activity failures e.g. Mistral OCR API rate limit, vector store not available etc

Database
1. Postgres + pgvector (for storing vector embeddings)


Infrastructure
1. AWS Cognito
2. AWS S3
Terraform for provisioning resources

Third party
1. OpenAI (for ReAct agent that powers the chat that does the query decomposition and invokes the tool to search information from the vector store)
2. Mistral OCR API

