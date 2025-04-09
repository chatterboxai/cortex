from typing import AsyncGenerator
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import AgentStream
from llama_index.core.workflow.handler import WorkflowHandler
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.storage.chat_store.postgres import PostgresChatStore
import os
from app.agents.tools import search_info_from_documents

DB_URL = os.getenv('DATABASE_URL')
if not DB_URL:
    raise ValueError('DATABASE_URL is not set')


class QaAgentWorkflow:

    chatbot_id: str

    def __init__(self, chatbot_id: str):
        self.chatbot_id = chatbot_id

    async def arespond(self, question: str, thread_id: str) -> AsyncGenerator[str, None]:
        llm = OpenAI(model='gpt-4o-mini')

        workflow = AgentWorkflow.from_tools_or_functions(
            [search_info_from_documents],
            llm=llm,
            system_prompt=(
                "You are a helpful assistant that helps answer questions from using internal knowledge base. Always call the search_info_from_documents tool to answer questions. If the answer is not found in the knowledge base, just say you don't have enough information to answer the question."
            ),
            initial_state={'chatbot_id': self.chatbot_id}
        )

        ctx = Context(workflow)
        chat_store = PostgresChatStore.from_uri(DB_URL)
        memory = ChatMemoryBuffer.from_defaults(
            chat_store=chat_store,
            chat_store_key=thread_id,
        )
        handler = workflow.run(
            # user_msg='How can dentist help with snoring? What causes snoring? How is sleep apnea diagnosed?',
            user_msg=question,
            ctx=ctx,
            memory=memory,
            chat_history=memory.get_all()
        )

        async for event in handler.stream_events():
            if isinstance(event, AgentStream):
                yield event.response
