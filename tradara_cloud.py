import pandas as pd
from datetime import date
from supabase import create_client

class TradaraCloud:
    def __init__(self, url, key):
        self.client = create_client(url, key)

    def restore(self, access_token, refresh_token):
        return self.client.auth.set_session(access_token, refresh_token)

    def sign_up(self, email, password):
        return self.client.auth.sign_up({"email": email, "password": password})

    def sign_in(self, email, password):
        return self.client.auth.sign_in_with_password({"email": email, "password": password})

    def sign_out(self):
        try: self.client.auth.sign_out()
        except Exception: pass

    def user(self):
        try:
            response = self.client.auth.get_user()
            return response.user
        except Exception:
            return None

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

    def pipeline_df(self, user_id):
        result = self.client.table("pipeline").select("*").eq("user_id", user_id).order("last_updated", desc=True).execute()
        return pd.DataFrame(result.data or [], columns=["id","user_id","development","trade","status","notes","est_value","first_saved","last_updated"])

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
