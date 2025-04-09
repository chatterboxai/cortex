from uuid import UUID
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI
from app.services.rag.vsi import VsiService


async def search_info_from_documents(ctx: Context, question: str) -> str:
    """
    Search through documents to find answers. 
    Use this tool to search for information from documents.
    """
    try:
        state = await ctx.get("state")

        chatbot_id = state['chatbot_id']

        vsi = VsiService.get_vsi(UUID(chatbot_id))

        # llm should be obtained from chatbot settings but j hard code it for now
        llm = OpenAI(model="gpt-4o-mini")

        query_engine = vsi.as_query_engine(llm=llm)

        response = await query_engine.aquery(question)
        return response.response
    
    except Exception as e:
        return "😞 I'm sorry, I don't have enough information to answer that question."

