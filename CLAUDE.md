# CLAUDE.md — Studio Foto WhatsApp Bot

## Project Summary
WhatsApp chatbot untuk studio foto. Menerima pesan via Meta Webhook, menampilkan menu interaktif, mengelola booking, dan menjawab pertanyaan fotografi menggunakan Google Gemini AI.

**Tech stack:** Flask + Waitress · Supabase (PostgreSQL) · Google Gemini API · WhatsApp Cloud API v18.0

---

## Architecture
```
WhatsApp User
     │
     ▼
POST /webhook  (app.py)
     │
     ├─ tipe == "text"       → ai_router.route_message()
     │                              ├─ AI_LLM       → llm_client.tanya_llm()
     │                              ├─ ENTER_AI_MODE → set_state FREE_TEXT
     │                              └─ REDIRECT      → kirim_menu_utama()
     │
     └─ tipe == "interactive" → _handle_interactive()  (app.py)
                                       ├─ btn_layanan    → services.py
                                       ├─ booking_*      → booking.py
                                       ├─ btn_ai         → set_state FREE_TEXT
                                       └─ btn_cs         → admin notify
                                       
Semua outgoing messages → handlers/sender.py → WhatsApp Cloud API
Semua state/data        → db/supabase_client.py → Supabase
```

---

## Key Files

| File | Fungsi |
|------|--------|
| `app.py` | Entry point Flask, webhook receiver, dispatcher utama |
| `handlers/sender.py` | Kirim pesan/tombol/list ke WhatsApp Cloud API |
| `handlers/menu.py` | Tampilkan menu utama |
| `handlers/services.py` | Katalog layanan dan detail paket |
| `handlers/booking.py` | State machine booking lengkap |
| `handlers/ai_router.py` | Routing pesan ke LLM atau rule-based, build system prompt |
| `handlers/llm_client.py` | Wrapper Google Gemini API |
| `handlers/admin.py` | Notifikasi ke nomor admin |
| `config/content.py` | Master data: layanan, paket, time slot, label status |
| `db/supabase_client.py` | Semua operasi DB: user, state, booking, time slot |
| `db/schema.sql` | Definisi schema database |

---

## Booking State Machine
```
IDLE
  │ booking_{service_id}
  ▼
PILIH_PAKET  (pilih paket Basic/Standard/Premium via list)
  │ paket_{service_id}_{paket_id}
  ▼
TUNGGU_TANGGAL  (user ketik tanggal format DD/MM/YYYY)
  │ teks tanggal valid
  ▼
PILIH_JAM  (pilih time slot via list)
  │ jam_{slot_id}
  ▼
KONFIRMASI  (tampilkan ringkasan, btn_konfirmasi atau btn_batal_booking)
  │ btn_konfirmasi
  ▼
IDLE  (booking tersimpan di DB)
```

**AI/Free Text mode:**
- `IDLE` → ketik "tanya ai"/"chat"/"ai" → state `FREE_TEXT`
- `FREE_TEXT` → semua teks masuk ke Gemini, respons dikirim balik
- `FREE_TEXT` → ketik "menu"/"selesai"/"keluar" → kembali ke `IDLE`

---

## Button/List ID Conventions
- `btn_*` — tombol menu utama
- `svc_{service_id}` — pilih layanan dari list
- `booking_{service_id}` — mulai booking layanan
- `paket_{service_id}_{paket_id}` — pilih paket (di-split dengan `rsplit("_", 1)`)
- `jam_{slot_id}` — pilih time slot

---

## Environment Variables (`.env`)
```
TOKEN=           # WhatsApp Cloud API access token
PHONE_ID=        # WhatsApp Business Phone Number ID
VERIFY_TOKEN=    # Webhook verification token
ADMIN_NUMBER=    # Nomor WA admin (format: 628xx)
SUPABASE_URL=    # Supabase project URL
SUPABASE_KEY=    # Supabase anon/service key
GEMINI_API_KEY=  # Google Gemini API key
PORT=5000        # (opsional, default 5000)
```

---

## Dev Commands

```bash
# Run lokal
python app.py

# Tunnel ke internet untuk webhook (dev)
./ngrok.exe http 5000

# Install dependencies
pip install -r requirements.txt

# Deploy ke Render
# Push ke main branch → auto deploy (Procfile: web: python app.py)
```

**Debug endpoints:**
- `GET /test-send` — kirim pesan test ke ADMIN_NUMBER
- `GET /debug-token` — cek validitas TOKEN & PHONE_ID ke Meta API

---

## Code Conventions
- **Bahasa variabel/fungsi:** Indonesia (e.g., `kirim_teks`, `nomor`, `pilihan`)
- **Bahasa konten user-facing:** Indonesia
- **Setiap handler** adalah fungsi standalone di file masing-masing, dipanggil dari `app.py`
- **State** disimpan di Supabase sebagai `{current_state, ...data}` per nomor pengguna
- **WhatsApp API version:** v18.0
