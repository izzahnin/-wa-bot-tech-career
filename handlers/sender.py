import requests
import os

_BASE_URL = "https://graph.facebook.com/v18.0"

def _headers():
    return {
        "Authorization": f"Bearer {os.getenv('TOKEN')}",
        "Content-Type": "application/json",
    }

def _post(payload: dict):
    url = f"{_BASE_URL}/{os.getenv('PHONE_ID')}/messages"
    r = requests.post(url, headers=_headers(), json=payload)
    print(f"[SEND] status={r.status_code} body={r.text[:200]}")
    return r


def kirim_teks(nomor: str, pesan: str):
    _post({
        "messaging_product": "whatsapp",
        "to": nomor,
        "type": "text",
        "text": {"body": pesan},
    })


def kirim_tombol(nomor: str, body: str, footer: str, buttons: list, header_text: str = None):
    header = {"type": "text", "text": header_text} if header_text else None
    interactive = {
        "type": "button",
        "body": {"text": body},
        "footer": {"text": footer},
        "action": {"buttons": buttons},
    }
    if header:
        interactive["header"] = header
    _post({
        "messaging_product": "whatsapp",
        "to": nomor,
        "type": "interactive",
        "interactive": interactive,
    })


def kirim_gambar_tombol(nomor: str, image_url: str, body: str, footer: str, buttons: list):
    _post({
        "messaging_product": "whatsapp",
        "to": nomor,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {"type": "image", "image": {"link": image_url}},
            "body": {"text": body},
            "footer": {"text": footer},
            "action": {"buttons": buttons},
        },
    })


def kirim_list(nomor: str, header: str, body: str, footer: str, button_label: str, sections: list):
    _post({
        "messaging_product": "whatsapp",
        "to": nomor,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header},
            "body": {"text": body},
            "footer": {"text": footer},
            "action": {
                "button": button_label,
                "sections": sections,
            },
        },
    })
