from temporalio.client import Client

_client = None

async def get_client():
    global _client
    if _client is None:
        _client = await Client.connect("127.0.0.1:7233")
    return _client
