from temporalio.client import Client
import os

TEMPORAL_SERVER_URL = os.getenv('TEMPORAL_SERVER_URL') or 'localhost:7233'

_client = None


async def get_client() -> Client:
    global _client
    if _client is None:
        _client = await Client.connect(TEMPORAL_SERVER_URL)
    return _client
