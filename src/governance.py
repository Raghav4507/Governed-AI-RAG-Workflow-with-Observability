import re
from openai import OpenAI
from .config import OPENAI_API_KEY, MODERATION_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

PROFANITY_PATTERN = re.compile(
    r"\b(fuck|shit|bitch|bastard|asshole|motherfucker|cunt)\b",
    re.IGNORECASE
)

def basic_profanity_detect(text: str) -> bool:
    return bool(PROFANITY_PATTERN.search(text))

def openai_moderate(text: str) -> dict:
    resp = client.moderations.create(
        model=MODERATION_MODEL,
        input=text
    )
    result = resp.results[0]
    return {
        "flagged": result.flagged,
        "categories": result.categories,
        "category_scores": result.category_scores,
    }

def enforce_input_policy(user_input: str) -> tuple[bool, str]:
    """
    Returns (allowed, message_if_blocked)
    """
    if basic_profanity_detect(user_input):
        return False, "Your request contains profanity and cannot be processed."

    mod = openai_moderate(user_input)
    if mod["flagged"]:
        return False, "Your request violates safety or content policy and cannot be processed."

    return True, ""