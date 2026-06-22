import os
from google import genai

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY belum diisi di .env")
        _client = genai.Client(api_key=api_key)
    return _client


def tanya_llm(system_prompt: str, pesan_user: str) -> str:
    try:
        client = _get_client()
        prompt = f"{system_prompt}\n\nPelanggan: {pesan_user}"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"[LLM_ERROR] {e}")
        return "Maaf, asisten AI sedang tidak tersedia. Silakan coba lagi nanti."
