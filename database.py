from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

_client: Client | None = None


def get_db() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("Supabase credentials not configured.")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def get_authed_db(token: str) -> Client:
    """Return a Supabase client authenticated with the user's JWT."""
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client.auth.set_session(token, token)
    return client
