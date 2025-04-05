import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as PineconeStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec

logger = logging.getLogger(__name__)

if os.getenv("RAILWAY_ENVIRONMENT_NAME") is None:
    from dotenv import load_dotenv
    load_dotenv()


async def init_pinecone(enable_scraping: bool = False):
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        embeddings = HuggingFaceEmbeddings(model_name="./models/paraphrase-MiniLM-L3-v2")
        index_name = "promptior-knowledge"

        if enable_scraping:
            logger.info("Scraping Enabled - Getting Fresh Data")
            from app.scraper import scrape_promptior

            # 1. Scrap content
            scraped_data = await scrape_promptior()
            documents = [
                f"Title: {item['url']}\nContent: {item['content'][:5000]}"
                for item in scraped_data
            ]

            # 2. Split files
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.create_documents(documents)

            # 3. Create index if not exists
            if index_name not in pc.list_indexes().names():
                pc.create_index(
                    name=index_name,
                    dimension=384,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )

            return PineconeStore.from_documents(
                splits,
                embeddings,
                index_name=index_name
            )
        else:
            logger.info("Using existing index (without scraping)")
            if index_name not in pc.list_indexes().names():
                raise ValueError("Index doesn't exists and scrapping is not enabled")

            return PineconeStore.from_existing_index(
                index_name,
                embeddings
            )

    except Exception as e:
        logger.error(f"Error initializing Pinecone: {str(e)}")
        raise
