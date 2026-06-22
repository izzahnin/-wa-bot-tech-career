# Studio Foto WhatsApp Bot

WhatsApp chatbot untuk manajemen studio foto — booking layanan, cek jadwal, dan konsultasi fotografi via AI.

## Fitur

- **Menu interaktif** — tombol dan list untuk navigasi tanpa ketik manual
- **Katalog layanan** — 5 layanan foto dengan 3 tier paket (Basic / Standard / Premium)
- **Booking online** — alur lengkap: pilih layanan → paket → tanggal → jam → konfirmasi
- **Cek booking** — lihat status dan riwayat booking per nomor WA
- **AI Assistant** — tanya jawab seputar fotografi menggunakan Google Gemini
- **Notifikasi admin** — alert otomatis ke nomor admin saat ada booking atau permintaan CS

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Web server | Flask + Waitress |
| Database | Supabase (PostgreSQL) |
| AI | Google Gemini 2.0 Flash |
| Messaging | WhatsApp Cloud API v18.0 |
| Deployment | Render |

## Struktur Project

```
bot-testing/
├── app.py                  # Entry point, webhook receiver & message dispatcher
├── config/
│   └── content.py          # Master data: layanan, paket, time slot
├── db/
│   ├── supabase_client.py  # Semua operasi database
│   └── schema.sql          # Skema tabel Supabase
└── handlers/
    ├── sender.py           # Kirim pesan/tombol/list ke WhatsApp API
    ├── menu.py             # Menu utama
    ├── services.py         # Katalog dan detail layanan
    ├── booking.py          # State machine alur booking
    ├── ai_router.py        # Routing pesan ke LLM atau rule-based
    ├── llm_client.py       # Wrapper Google Gemini API
    └── admin.py            # Notifikasi admin
```

## Alur Booking

```
Pilih Layanan → Pilih Paket → Input Tanggal (DD/MM/YYYY) → Pilih Jam → Konfirmasi
```

State machine: `IDLE` → `PILIH_PAKET` → `TUNGGU_TANGGAL` → `PILIH_JAM` → `KONFIRMASI` → `IDLE`

## Setup Lokal

### 1. Clone & install dependencies

```bash
git clone <repo-url>
cd bot-testing
pip install -r requirements.txt
```

### 2. Buat file `.env`

```env
TOKEN=           # WhatsApp Cloud API access token
PHONE_ID=        # WhatsApp Business Phone Number ID
VERIFY_TOKEN=    # Token untuk verifikasi webhook
ADMIN_NUMBER=    # Nomor WA admin (format: 628xx tanpa +)
SUPABASE_URL=    # URL project Supabase
SUPABASE_KEY=    # Supabase anon/service key
GEMINI_API_KEY=  # Google Gemini API key (format: AIzaSy...)
RENDER_SECRET=   # Secret untuk proteksi endpoint debug
```

### 3. Setup database Supabase

Jalankan `db/schema.sql` di Supabase SQL editor.

### 4. Jalankan server

```bash
python app.py
```

Server berjalan di `http://localhost:5000`.

### 5. Tunnel untuk webhook (development)

```bash
./ngrok.exe http 5000
```

Daftarkan URL ngrok ke Meta Webhook: `https://<ngrok-url>/webhook`

## Environment Variables

| Variable | Keterangan |
|----------|------------|
| `TOKEN` | Access token dari Meta Developer Console |
| `PHONE_ID` | Phone Number ID dari WhatsApp Business |
| `VERIFY_TOKEN` | String bebas untuk verifikasi webhook Meta |
| `ADMIN_NUMBER` | Nomor WA admin tanpa `+` (contoh: `6281234567890`) |
| `SUPABASE_URL` | URL project dari Supabase dashboard |
| `SUPABASE_KEY` | API key dari Supabase dashboard |
| `GEMINI_API_KEY` | API key dari [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `RENDER_SECRET` | Secret untuk akses endpoint `/test-send` |

## Deployment (Render)

1. Push ke GitHub
2. Buat **Web Service** baru di Render → connect repo ini
3. Isi semua environment variables di Render dashboard
4. Render otomatis deploy via `Procfile`: `web: python app.py`

## Debug Endpoints

| Endpoint | Fungsi |
|----------|--------|
| `GET /test-send?secret=<RENDER_SECRET>` | Kirim pesan test ke ADMIN_NUMBER |
| `GET /debug-token` | Cek validitas TOKEN & PHONE_ID ke Meta API |