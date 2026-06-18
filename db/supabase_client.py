import os
from datetime import datetime, timezone
from supabase import create_client, Client

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL dan SUPABASE_KEY belum diisi di .env")
        _client = create_client(url, key)
    return _client


def upsert_user(wa_number: str, name: str) -> dict:
    sb = get_client()
    now = datetime.now(timezone.utc).isoformat()
    result = (
        sb.table("users")
        .upsert(
            {"wa_number": wa_number, "name": name, "last_seen_at": now},
            on_conflict="wa_number",
        )
        .execute()
    )
    return result.data[0] if result.data else {}


def get_user(wa_number: str) -> dict:
    sb = get_client()
    result = sb.table("users").select("*").eq("wa_number", wa_number).execute()
    return result.data[0] if result.data else {}


def save_enrollment(user_id: str, path_id: str):
    sb = get_client()
    # nonaktifkan enrollment lama
    sb.table("enrollments").update({"is_active": False}).eq("user_id", user_id).execute()
    # insert enrollment baru
    sb.table("enrollments").insert({
        "user_id": user_id,
        "path_id": path_id,
        "is_active": True,
    }).execute()
    # update active_path di tabel users
    sb.table("users").update({"active_path": path_id}).eq("id", user_id).execute()


def get_state(wa_number: str) -> dict:
    sb = get_client()
    result = (
        sb.table("conversation_state")
        .select("*")
        .eq("wa_number", wa_number)
        .execute()
    )
    return result.data[0] if result.data else {}


def set_state(wa_number: str, state: str, context_data: dict = None):
    sb = get_client()
    sb.table("conversation_state").upsert(
        {
            "wa_number": wa_number,
            "current_state": state,
            "context_data": context_data or {},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        on_conflict="wa_number",
    ).execute()


def save_challenge_response(user_id: str, path_id: str, day: int, status: str):
    sb = get_client()
    now = datetime.now(timezone.utc).isoformat()
    existing = (
        sb.table("daily_challenges")
        .select("id")
        .eq("user_id", user_id)
        .eq("path_id", path_id)
        .eq("challenge_day", day)
        .execute()
    )
    if existing.data:
        sb.table("daily_challenges").update({
            "status": status,
            "responded_at": now,
        }).eq("id", existing.data[0]["id"]).execute()
    else:
        sb.table("daily_challenges").insert({
            "user_id": user_id,
            "path_id": path_id,
            "challenge_day": day,
            "status": status,
            "responded_at": now,
        }).execute()


def get_streak(user_id: str) -> int:
    sb = get_client()
    result = (
        sb.table("daily_challenges")
        .select("challenge_day, status, responded_at")
        .eq("user_id", user_id)
        .eq("status", "done")
        .order("responded_at", desc=True)
        .execute()
    )
    if not result.data:
        return 0

    streak = 0
    prev_date = None
    for row in result.data:
        if not row.get("responded_at"):
            continue
        date = row["responded_at"][:10]
        if prev_date is None:
            streak = 1
            prev_date = date
        elif (datetime.fromisoformat(prev_date) - datetime.fromisoformat(date)).days == 1:
            streak += 1
            prev_date = date
        else:
            break
    return streak


def get_challenge_day(user_id: str, path_id: str) -> int:
    sb = get_client()
    result = (
        sb.table("daily_challenges")
        .select("challenge_day")
        .eq("user_id", user_id)
        .eq("path_id", path_id)
        .order("challenge_day", desc=True)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]["challenge_day"] + 1
    return 1


def get_done_this_week(user_id: str) -> int:
    sb = get_client()
    result = (
        sb.table("daily_challenges")
        .select("id")
        .eq("user_id", user_id)
        .eq("status", "done")
        .execute()
    )
    return len(result.data)
