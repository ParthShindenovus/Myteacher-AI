from django.conf import settings
from langchain_openai import AzureChatOpenAI


class AzureServiceError(RuntimeError):
    pass


def build_azure_openai_llm() -> AzureChatOpenAI:
    if not settings.AZURE_OPENAI_API_KEY or not settings.AZURE_OPENAI_ENDPOINT:
        raise AzureServiceError("Azure OpenAI credentials are not configured")

    return AzureChatOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
        temperature=0,
    )


def speech_to_text_placeholder(audio_url: str) -> str:
    if not audio_url:
        raise AzureServiceError("Missing audio input")
    return "transcribed audio text"


def image_to_text_placeholder(image_url: str) -> tuple[str, bool]:
    if not image_url:
        raise AzureServiceError("Missing image input")
    return "parsed text from image", True
