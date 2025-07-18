import os
from openai import OpenAI
from anthropic import Anthropic

# Constants for LLM configuration
TEMPERATURE = 0.6
MAX_TOKENS = 500

def get_available_models():
    # Check available LLMs based on API keys
    models = []
    if os.getenv("ANTHROPIC_API_KEY"):
        models.append("Claude (Anthropic)")
    if os.getenv("OPENAI_API_KEY"):
        models.append("GPT-4o (OpenAI)")
    return models

# Get selected model based on user preference or default to Claude (if available)
def get_selected_model(available_models, use_custom_selection, user_selection=None):
    # Decide which LLM to use
    if len(available_models) == 1:
        return available_models[0]
    if "Claude (Anthropic)" in available_models and not use_custom_selection:
        return "Claude (Anthropic)"
    return user_selection or available_models[0]

def call_llm(model_name, prompt):
    # Route the prompt to selected LLM and return formatted response
    if "Claude" in model_name:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system="You are an expert resume critiquer and reviewer with years of experience in the field.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return "".join(
            block.text if hasattr(block, "text") else str(block)
            for block in response.content
        )

    elif "OpenAI" in model_name:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert resume critiquer and reviewer with years of experience in the field."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        return response.choices[0].message.content

    else:
        return "Unsupported model selected."
