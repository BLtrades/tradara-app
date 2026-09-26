from datetime import date
import pandas as pd
import streamlit as st
from supabase import create_client

@st.cache_resource
def base_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def cloud_ready():
    return "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets

def client():
    c=base_client()
    access=st.session_state.get("access_token")
    refresh=st.session_state.get("refresh_token")
    if access and refresh:
        try:c.auth.set_session(access,refresh)
        except Exception:pass
    return c

def user():
    return st.session_state.get("tradara_user")

def sign_in(email,password):
    r=base_client().auth.sign_in_with_password({"email":email,"password":password})
    if r.user and r.session:
        st.session_state.tradara_user={"id":str(r.user.id),"email":r.user.email}
        st.session_state.access_token=r.session.access_token
        st.session_state.refresh_token=r.session.refresh_token
        return True
    return False

def sign_up(email,password):
    r=base_client().auth.sign_up({"email":email,"password":password})
    if r.user and r.session:
        st.session_state.tradara_user={"id":str(r.user.id),"email":r.user.email}
        st.session_state.access_token=r.session.access_token
        st.session_state.refresh_token=r.session.refresh_token
        return "signed_in"
    return "confirm"

def sign_out():
    try:client().auth.sign_out()
    except Exception:pass
    for k in ["tradara_user","access_token","refresh_token"]:st.session_state.pop(k,None)

def get_profile():
    u=user()
    if not u:return None
    r=client().table("profiles").select("*").eq("user_id",u["id"]).limit(1).execute()
    return r.data[0] if r.data else None

def save_profile(name,location,description,trades,types,maxdist,minval,maxval,targetmonth,revenue):
    u=user()
    payload={"user_id":u["id"],"company_name":name,"base_location":location,"company_description":description,"preferred_trades":trades,"preferred_project_types":types,"max_distance_km":maxdist,"min_job_value":minval,"max_job_value":maxval,"target_month":str(targetmonth),"revenue_target":revenue,"updated_at":pd.Timestamp.utcnow().isoformat()}
    client().table("profiles").upsert(payload,on_conflict="user_id").execute()

def pipeline_df():
    u=user()
    if not u:return pd.DataFrame(columns=["development","trade","status","notes","est_value","first_saved","last_updated"])
    r=client().table("pipeline").select("*").eq("user_id",u["id"]).order("last_updated",desc=True).execute()
    return pd.DataFrame(r.data)

def save_lead(dev,trade,status="Saved",notes="",value=0):
    u=user(); today=str(date.today())
    payload={"user_id":u["id"],"development":dev,"trade":trade,"status":status,"notes":notes,"est_value":float(value or 0),"last_updated":today}
    client().table("pipeline").upsert(payload,on_conflict="user_id,development,trade").execute()
