import os
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.llm import GeminiAI
from app.vector_db import init_pinecone

logger = logging.getLogger(__name__)

if os.getenv("RAILWAY_ENVIRONMENT_NAME") is None:
    from dotenv import load_dotenv
    load_dotenv()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


async def setup_rag_chain():
    try:
        logger.info("Initializing RAG chain...")

        enable_scraping = os.getenv("ENABLE_SCRAPING", "false").lower() == "true"
        vectorstore = await init_pinecone(enable_scraping=enable_scraping)

        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3}
        )

        template = """Answer the question based only on the following context:
        {context}
        
        Question: {question}"""
        
        prompt = ChatPromptTemplate.from_template(template)
        llm = GeminiAI()

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm.generate
            | StrOutputParser()
        )

        logger.info("✅ RAG chain initialized successfully")
        return rag_chain
    except Exception as e:
        logger.error(f"Error setting up RAG chain: {str(e)}")
        raise
