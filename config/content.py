ROADMAP_PATHS = {
    "path_backend_golang": {
        "title": "Backend Engineer — Golang",
        "emoji": "🐹",
        "stack": [
            "Go (Golang), Gin / Fiber framework",
            "PostgreSQL + GORM / sqlx",
            "Docker & Docker Compose",
            "REST API + gRPC",
            "Redis (caching), JWT Auth",
            "GitHub Actions (CI/CD dasar)",
        ],
        "salary": [
            "Junior Backend (0–1 thn): Rp 6–10 juta/bulan",
            "Mid-level (1–3 thn): Rp 12–22 juta/bulan",
            "Senior / Tech Lead: Rp 25–50 juta/bulan",
            "Remote internasional: $2.000–$5.000 USD/bulan",
        ],
        "duration": "~16 minggu (belajar 1–2 jam/hari)",
        "total_modules": 24,
        "total_challenges": 16,
    },
    "path_frontend_react": {
        "title": "Frontend Engineer — React",
        "emoji": "⚛️",
        "stack": [
            "React 19, TypeScript",
            "Next.js 15 (App Router)",
            "Tailwind CSS, Shadcn/UI",
            "Zustand / React Query",
            "Jest + React Testing Library",
            "Vercel / Netlify deploy",
        ],
        "salary": [
            "Junior Frontend (0–1 thn): Rp 5–9 juta/bulan",
            "Mid-level (1–3 thn): Rp 10–20 juta/bulan",
            "Senior Frontend: Rp 22–45 juta/bulan",
            "Remote internasional: $1.500–$4.500 USD/bulan",
        ],
        "duration": "~14 minggu (belajar 1–2 jam/hari)",
        "total_modules": 20,
        "total_challenges": 14,
    },
    "path_cloud_engineer": {
        "title": "Cloud Engineer",
        "emoji": "☁️",
        "stack": [
            "AWS (EC2, S3, RDS, Lambda) / GCP",
            "Terraform (Infrastructure as Code)",
            "Docker & Kubernetes (EKS/GKE)",
            "GitHub Actions / GitLab CI",
            "Prometheus + Grafana (Monitoring)",
            "Linux & Bash scripting",
        ],
        "salary": [
            "Junior Cloud (0–1 thn): Rp 8–13 juta/bulan",
            "Mid-level (1–3 thn): Rp 15–28 juta/bulan",
            "Senior Cloud Architect: Rp 30–60 juta/bulan",
            "Remote internasional: $3.000–$8.000 USD/bulan",
        ],
        "duration": "~18 minggu (belajar 1–2 jam/hari)",
        "total_modules": 28,
        "total_challenges": 18,
    },
    "path_fullstack": {
        "title": "Fullstack Engineer — Go + React",
        "emoji": "🔥",
        "stack": [
            "Go (Gin) untuk backend API",
            "React + TypeScript untuk frontend",
            "PostgreSQL + Redis",
            "Docker Compose (multi-service)",
            "JWT Auth end-to-end",
            "Deploy ke VPS / Railway",
        ],
        "salary": [
            "Junior Fullstack (0–1 thn): Rp 7–12 juta/bulan",
            "Mid-level (1–3 thn): Rp 15–25 juta/bulan",
            "Senior Fullstack: Rp 28–55 juta/bulan",
            "Remote internasional: $2.500–$6.000 USD/bulan",
        ],
        "duration": "~22 minggu (belajar 1–2 jam/hari)",
        "total_modules": 36,
        "total_challenges": 22,
    },
    "path_devops": {
        "title": "DevOps Engineer",
        "emoji": "🛠️",
        "stack": [
            "Linux & Shell scripting",
            "Docker & Kubernetes",
            "GitHub Actions, Jenkins",
            "Ansible (Configuration Management)",
            "Prometheus, Grafana, ELK Stack",
            "Nginx, HAProxy (Load Balancer)",
        ],
        "salary": [
            "Junior DevOps (0–1 thn): Rp 7–12 juta/bulan",
            "Mid-level (1–3 thn): Rp 15–30 juta/bulan",
            "Senior DevOps / SRE: Rp 30–65 juta/bulan",
            "Remote internasional: $3.000–$9.000 USD/bulan",
        ],
        "duration": "~20 minggu (belajar 1–2 jam/hari)",
        "total_modules": 32,
        "total_challenges": 20,
    },
    "path_mobile_flutter": {
        "title": "Mobile Engineer — Flutter",
        "emoji": "📱",
        "stack": [
            "Dart & Flutter (cross-platform)",
            "Firebase (Auth, Firestore, Storage)",
            "Riverpod / BLoC (state management)",
            "REST API integration",
            "Push Notification (FCM)",
            "Play Store & App Store deploy",
        ],
        "salary": [
            "Junior Mobile (0–1 thn): Rp 6–10 juta/bulan",
            "Mid-level (1–3 thn): Rp 12–22 juta/bulan",
            "Senior Mobile Engineer: Rp 24–48 juta/bulan",
            "Remote internasional: $2.000–$5.500 USD/bulan",
        ],
        "duration": "~16 minggu (belajar 1–2 jam/hari)",
        "total_modules": 22,
        "total_challenges": 16,
    },
}

DAILY_CHALLENGES = {
    "path_backend_golang": [
        {
            "day": 1,
            "topic": "Syntax Dasar & Control Flow",
            "case": (
                "Buat program Go yang menerima array angka dan mengembalikan "
                "dua angka dengan selisih terkecil.\n\n"
                "*🧩 Constraint:*\n"
                "• Input: `[]int{4, 1, 8, 3, 9}`\n"
                "• Output: angka dan selisihnya\n"
                "• Time complexity harus O(n log n)"
            ),
        },
        {
            "day": 7,
            "topic": "REST API & Database Optimization",
            "case": (
                "Buat endpoint `GET /leaderboard` yang mengembalikan *top 10 user* "
                "berdasarkan skor tertinggi dari tabel `users`.\n\n"
                "*🧩 Constraint:*\n"
                "• Tabel `users` berisi 1 juta+ baris\n"
                "• Response harus < 100ms\n"
                "• Tidak boleh menggunakan `SELECT *`\n\n"
                "*💡 Yang harus kamu pikirkan:*\n"
                "1. Index apa yang perlu dibuat di PostgreSQL?\n"
                "2. Apakah perlu Redis caching? Berapa TTL-nya?\n"
                "3. Tulis query SQL atau pseudocode-nya"
            ),
        },
    ],
    "path_frontend_react": [
        {
            "day": 1,
            "topic": "React Hooks & State",
            "case": (
                "Buat komponen `useDebounce` custom hook yang men-delay update "
                "nilai input selama 500ms.\n\n"
                "*🧩 Constraint:*\n"
                "• Gunakan TypeScript\n"
                "• Hook harus bersih dari memory leak (cleanup `useEffect`)\n"
                "• Implementasikan untuk search bar sederhana"
            ),
        },
    ],
}
