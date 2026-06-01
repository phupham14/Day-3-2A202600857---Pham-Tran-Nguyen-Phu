import os
from dotenv import load_dotenv
from src.core.llm_provider import LLMProvider

load_dotenv()


def create_provider() -> LLMProvider:
    provider = os.getenv("DEFAULT_PROVIDER", "openai").lower()
    model = os.getenv("DEFAULT_MODEL", "gpt-4o")

    if provider == "openai":
        from src.core.openai_provider import OpenAIProvider
        api_key = os.getenv("OPENAI_API_KEY")
        return OpenAIProvider(model_name=model, api_key=api_key)

    elif provider == "google":
        from src.core.gemini_provider import GeminiProvider
        api_key = os.getenv("GEMINI_API_KEY")
        return GeminiProvider(model_name=model, api_key=api_key)

    elif provider == "local":
        from src.core.local_provider import LocalProvider
        model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        return LocalProvider(model_path=model_path)

    else:
        raise ValueError(f"Unknown provider: '{provider}'. Choose from: openai, google, local")
