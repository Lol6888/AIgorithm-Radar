# monitor/i18n.py
import os, requests

LT_URL = os.getenv("LIBRETRANSLATE_URL")  # ví dụ: https://libretranslate.com
LT_API_KEY = os.getenv("LIBRETRANSLATE_API_KEY", "")  # thường không cần cho instance public

def translate_text(text: str, target_lang: str, source_lang: str = "auto", timeout=20) -> str:
    """
    Dịch qua LibreTranslate nếu LIBRETRANSLATE_URL có cấu hình. Ngược lại, trả nguyên văn.
    target_lang: "vi" hoặc "en".
    """
    if not LT_URL or not text or not text.strip():
        return text
    try:
        resp = requests.post(
            f"{LT_URL}/translate",
            timeout=timeout,
            data={
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text",
                "api_key": LT_API_KEY,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("translatedText", text)
    except Exception:
        return text  # fallback an toàn
