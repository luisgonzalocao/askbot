import os
import sys
import time
import logging
import resource

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import QuestionRequest
from app.prompts import build_defensive_prompt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

if os.getenv("RAILWAY_ENVIRONMENT_NAME") is None:
    from dotenv import load_dotenv
    load_dotenv()

mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
logger.info(f"Memory usage: {mem / 1024:.2f} MB")

app = FastAPI(
    title="Promtior RAG API",
    description="Retrieval-Augmented Generation API for Promtior content",
    version="1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


async def initialize_rag():
    try:
        from app.rag import setup_rag_chain
        # logger.info("Installing Playwright browsers if needed...")
        # import subprocess
        # subprocess.run(["playwright", "install", "chromium"], check=True)
        return await setup_rag_chain()
    except Exception as e:
        logger.error(f"Error initializing RAG: {str(e)}", exc_info=True)
        raise


@app.on_event("startup")
async def startup_event():
    logger.info("Starting application initialization...")
    try:
        app.state.startup_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        required_vars = ['PINECONE_API_KEY', 'PINECONE_ENV', 'GEMINI_API_KEY', 'PORT']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            logger.warning(f"Missing environment variables: {missing_vars}")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                app.state.rag_chain = await initialize_rag()
                logger.info("✅ RAG chain initialized successfully")
                break
            except Exception:
                if attempt == max_retries - 1:
                    raise
                wait_time = (attempt + 1) * 2
                logger.warning(f"Retry {attempt + 1}/{max_retries} in {wait_time}s...")
                time.sleep(wait_time)

    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}", exc_info=True)
        app.state.rag_chain = None

@app.get("/health")
async def health_check():
    try:
        pinecone_status = "OK"
        try:
            if os.getenv("PINECONE_API_KEY"):
                from pinecone import Pinecone
                pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
                pc.list_indexes()
            else:
                pinecone_status = "NOT_CONFIGURED"
        except Exception as e:
            pinecone_status = f"ERROR: {str(e)}"

        gemini_status = "OK"
        try:
            if os.getenv("GEMINI_API_KEY"):
                from google.generativeai import  configure, list_models
                configure(api_key=os.getenv("GEMINI_API_KEY"))
                list_models()
            else:
                gemini_status = "NOT_CONFIGURED"
        except Exception as e:
            gemini_status = f"ERROR: {str(e)}"

        import psutil
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)

        status = {
            "status": "OK" if hasattr(app.state, 'rag_chain') and app.state.rag_chain else "WARNING",
            "services": {
                "pinecone": pinecone_status,
                "gemini": gemini_status,
                "vector_db_connection": "OK" if hasattr(app.state, 'rag_chain') else "NOT_READY"
            },
            "resources": {
                "memory_usage": f"{memory.percent}%",
                "available_memory": f"{memory.available / (1024**2):.2f} MB",
                "cpu_usage": f"{cpu}%"
            },
            "environment": {
                "enable_scraping": os.getenv("ENABLE_SCRAPING", "false"),
                "model_in_use": getattr(app.state, 'model_name', 'UNKNOWN') if hasattr(app.state, 'rag_chain') else None
            },
            "timestamps": {
                "startup_time": getattr(app.state, 'startup_time', None),
                "last_request": getattr(app.state, 'last_request_time', None)
            }
        }

        if (status["status"] != "OK" or 
            "ERROR" in pinecone_status or 
            "ERROR" in gemini_status):
            raise HTTPException(
                status_code=503,
                detail={
                    "message": "Service is initializing or partially available",
                    "details": status
                }
            )

        return status

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Health check system failure",
                "error": str(e)
            }
        )

@app.post("/ask")
async def ask_question(request: QuestionRequest = Body(...)):
    app.state.last_request_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if not hasattr(app.state, 'rag_chain') or not app.state.rag_chain:
        raise HTTPException(
            status_code=503,
            detail="Service is initializing. Please try again later."
        )

    try:
        logger.info(f"Processing question: {request.question}")

        prompt = build_defensive_prompt(request.question)
        response = await app.state.rag_chain.ainvoke(prompt)
        return {"answer": response}
    except Exception as e:
        logger.exception(f"Error processing question: {str(e)}",
                         exc_info=True, stack_info=True)
        raise HTTPException(
            status_code=500,
            detail="Question processing failed. Please try again later."
        )


@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse("app/templates/index.html")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")
