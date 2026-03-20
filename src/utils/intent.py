"""Intent classification utility."""

from litellm import completion

from src.config.settings import INTENT_MODEL


def classify_intent(text: str) -> str:
    """Returns 'upload' or 'query' using a fast Groq model."""
    prompt = (
        "Classify this user message as exactly one word: 'upload' or 'query'.\n"
        "'upload' = user wants to upload or add a health report.\n"
        "'query' = user is asking a question about their health data.\n"
        f"Message: {text}\nAnswer:"
    )
    response = completion(model=INTENT_MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=5)
    label = response.choices[0].message.content.strip().lower()
    return "upload" if "upload" in label else "query"
