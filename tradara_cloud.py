import pandas as pd
from datetime import date
from supabase import create_client


class TradaraCloud:
    """Authenticated Supabase data layer for Tradara 1.0."""

    def __init__(self, url, key):
        self.client = create_client(url, key)

    # ---------- Authentication ----------
    def restore(self, access_token, refresh_token):
        return self.client.auth.set_session(access_token, refresh_token)

    def sign_up(self, email, password):
        return self.client.auth.sign_up({"email": email.strip().lower(), "password": password})

    def sign_in(self, email, password):
        return self.client.auth.sign_in_with_password({"email": email.strip().lower(), "password": password})

    def sign_out(self):
        try:
            self.client.auth.sign_out()
        except Exception:
            pass

    def user(self):
        try:
            response = self.client.auth.get_user()
            return response.user
        except Exception:
            return None

    def reset_password(self, email, redirect_url=None):
        options = {"redirect_to": redirect_url} if redirect_url else None
        return self.client.auth.reset_password_email(email.strip().lower(), options=options)

    def update_password(self, new_password):
        if len(new_password) < 8:
            raise ValueError("Password must contain at least 8 characters.")
        return self.client.auth.update_user({"password": new_password})

    def update_email(self, new_email):
        return self.client.auth.update_user({"email": new_email.strip().lower()})

    def session_tokens(self):
        session = self.client.auth.get_session()
        if not session:
            return None
        return {"access_token": session.access_token, "refresh_token": session.refresh_token}

    # ---------- Company profile ----------
    def get_profile(self, user_id):
        result = self.client.table("profiles").select("*").eq("user_id", user_id).maybe_single().execute()
        return result.data or None

    def save_profile(self, user_id, name, location, description, trades, types, maxdist, minval, maxval, targetmonth, revenue):
        payload = {
            "user_id": user_id,
            "company_name": name,
            "base_location": location,
            "company_description": description,
            "preferred_trades": trades,
            "preferred_project_types": types,
            "max_distance_km": float(maxdist),
            "min_job_value": float(minval),
            "max_job_value": float(maxval),
            "target_month": str(targetmonth),
            "revenue_target": float(revenue),
        }
        return self.client.table("profiles").upsert(payload, on_conflict="user_id").execute()

    # ---------- Pipeline ----------
    def pipeline_df(self, user_id):
        result = self.client.table("pipeline").select("*").eq("user_id", user_id).order("last_updated", desc=True).execute()
        return pd.DataFrame(result.data or [], columns=["id", "user_id", "development", "trade", "status", "notes", "est_value", "first_saved", "last_updated"])

    def save_lead(self, user_id, development, trade, status="Saved", notes="", value=0):
        payload = {
            "user_id": user_id,
            "development": development,
            "trade": trade,
            "status": status,
            "notes": notes or "",
            "est_value": float(value or 0),
            "last_updated": str(date.today()),
        }
        return self.client.table("pipeline").upsert(payload, on_conflict="user_id,development,trade").execute()

    def delete_lead(self, user_id, development, trade):
        return self.client.table("pipeline").delete().eq("user_id", user_id).eq("development", development).eq("trade", trade).execute()

    # ---------- Privacy / account lifecycle ----------
    def delete_customer_data(self, user_id):
        """Delete app-owned data for the authenticated user.

        Auth-user deletion itself must be performed by a protected server-side
        function using privileged credentials. A service-role key must never be
        exposed to the Streamlit client.
        """
        self.client.table("pipeline").delete().eq("user_id", user_id).execute()
        self.client.table("profiles").delete().eq("user_id", user_id).execute()
        return True
