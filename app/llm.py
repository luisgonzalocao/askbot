from google.generativeai import GenerativeModel, configure
import os
import logging
from typing import Union, Dict, Any
from app.main import app


logger = logging.getLogger(__name__)


if os.getenv("RAILWAY_ENVIRONMENT_NAME") is None:
    from dotenv import load_dotenv
    load_dotenv()


class GeminiAI:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", None)
        if api_key is None:
            msg = "Gemini API Key is missing."
            logger.error(msg)
            raise ValueError(msg)

        configure(api_key=api_key)
        model_name = 'models/gemini-1.5-pro-latest'

        try:
            self.model = GenerativeModel(model_name)
            app.state.model_name = model_name
            logger.info(f"Selected model: {model_name}")

        except Exception as e:
            logger.error(f"Error setting Gemini model: {str(e)}")
            raise

    def generate(self, input_data: Union[str, Dict, Any]) -> str:
        try:
            if isinstance(input_data, dict) and 'messages' in input_data:
                if hasattr(input_data['messages'][0], 'content'):
                    prompt = input_data['messages'][0].content
                else:
                    prompt = str(input_data['messages'][0])
            elif isinstance(input_data, str):
                prompt = input_data
            else:
                prompt = str(input_data)

            logger.debug(f"Generating response for prompt: {prompt[:100]}...")
            response = self.model.generate_content(prompt)

            if not response.text:
                logger.warning("The model returned an empty response")
                return "Sorry, I couldn't generate a response. Please try again."

            return response.text

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise RuntimeError(f"Error generating content: {str(e)}")
