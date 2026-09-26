import re, requests
from datetime import date
import pandas as pd
import streamlit as st
from tradara_cloud import TradaraCloud

st.set_page_config(page_title="Tradara | Construction Opportunity Intelligence",page_icon="⚡",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
:root{--ink:#0b1020;--muted:#667085;--line:#e5e9f2}.stApp{background:radial-gradient(circle at 90% 0%,rgba(91,108,255,.09),transparent 28%),#fbfcfe;color:var(--ink)}.block-container{max-width:1380px;padding:1.25rem 2rem 5rem}h1,h2,h3,p,label{font-weight:650}h1,h2,h3{letter-spacing:-.035em}.brand{display:flex;align-items:center;gap:12px;margin-bottom:20px}.mark{width:46px;height:46px;border-radius:14px;background:linear-gradient(135deg,#7180ff,#4755d8);color:#fff;display:grid;place-items:center;font-size:22px;font-weight:900;box-shadow:0 10px 28px #4f5de83d}.name{font-size:26px;font-weight:900;letter-spacing:-.05em}.sub{font-size:11px;color:#758198;font-weight:800;letter-spacing:.11em}.hero{padding:38px 42px;border-radius:24px;background:linear-gradient(135deg,#0c1427,#17264a 58%,#283776);color:white;margin-bottom:24px;box-shadow:0 20px 55px #10182820}.hero h1{color:white;font-size:38px;margin:8px 0}.hero p{color:#d2d9e8;max-width:760px;line-height:1.6}.pill{display:inline-block;padding:7px 11px;border-radius:99px;background:#ffffff12;border:1px solid #ffffff18;color:#bdefff;font-size:11px;font-weight:850;letter-spacing:.08em}.auth{max-width:520px;margin:6vh auto;background:white;border:1px solid var(--line);border-radius:22px;padding:32px;box-shadow:0 24px 70px #10182814}.auth h1{font-size:32px;margin-bottom:6px}.auth p{color:#667085}.stButton>button,.stLinkButton>a{border-radius:11px;font-weight:800;min-height:44px}.stButton>button[kind="primary"]{background:linear-gradient(135deg,#6574ff,#4d5bd9);border:0}div[data-testid="stMetric"]{border:1px solid var(--line);border-radius:17px;padding:17px;background:white;box-shadow:0 8px 25px #1018280a}div[data-testid="stExpander"]{border:1px solid var(--line);border-radius:15px;background:white}[data-baseweb="tab-list"]{gap:7px;background:white;border:1px solid var(--line);padding:7px;border-radius:15px}button[data-baseweb="tab"]{font-weight:800}.stTextInput input,.stTextArea textarea,.stNumberInput input{border-radius:10px!important}@media(max-width:760px){.block-container{padding:1rem .85rem 5rem}.hero{padding:27px 22px}.hero h1{font-size:29px}.auth{margin:2vh auto;padding:23px}.stTabs [data-baseweb="tab-list"]{overflow-x:auto}.stTabs [data-baseweb="tab"]{white-space:nowrap}}
</style>""",unsafe_allow_html=True)

try:
    # Keep the auth client within this Streamlit session. A shared client can expose
    # one visitor's credentials to another visitor.
    if "cloud" not in st.session_state:
        st.session_state.cloud=TradaraCloud(st.secrets["SUPABASE_URL"],st.secrets["SUPABASE_KEY"])
    cloud=st.session_state.cloud
except Exception:
    st.error("Tradara Cloud is not configured. Add SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets."); st.stop()

if "session" not in st.session_state: st.session_state.session=None

# Supabase's recovery email template can link back with a token_hash. Verify it
# server-side before allowing a password change, then remove it from the URL.
if st.query_params.get("type")=="recovery" and st.query_params.get("token_hash"):
    try:
        recovery=cloud.verify_recovery(st.query_params["token_hash"])
        st.session_state.session=recovery.session
        st.session_state.recovery_mode=True
        st.query_params.clear()
        st.rerun()
    except Exception:
        st.query_params.clear()
        st.error("This recovery link is invalid or expired. Request another reset email.")

def auth_screen():
    st.markdown('<div class="auth"><div class="brand"><div class="mark">T</div><div><div class="name">Tradara</div><div class="sub">CONSTRUCTION OPPORTUNITY INTELLIGENCE</div></div></div><h1>Work is out there.<br>See it earlier.</h1><p>Sign in to sync your company profile, opportunity radar and pipeline across phone and desktop.</p></div>',unsafe_allow_html=True)
    mode=st.radio("Account",["Sign in","Create account","Reset password"],horizontal=True,label_visibility="collapsed")
    email=st.text_input("Email",placeholder="you@company.com")
    password=st.text_input("Password",type="password",placeholder="Minimum 6 characters") if mode!="Reset password" else ""
    if st.button(mode,type="primary",use_container_width=True):
        if not email or (mode!="Reset password" and len(password)<6): st.error("Enter an email and a password of at least 6 characters."); return
        try:
            if mode=="Reset password":
                cloud.reset_password(email)
                st.success("If that address has an account, a recovery email has been sent. Follow its instructions.")
            elif mode=="Create account":
                res=cloud.sign_up(email,password)
                if res.session: st.session_state.session=res.session; st.rerun()
                else: st.success("Account created. Check your email to confirm it, then sign in.")
            else:
                res=cloud.sign_in(email,password); st.session_state.session=res.session; st.rerun()
        except Exception: st.error(f"Could not {mode.lower()}. Check your details and try again.")

user=cloud.user() if st.session_state.session else None
if not user: auth_screen(); st.stop()
UID=str(user.id)

TRADE_INTEL={"Earthworks":(["land division","subdivision","earthworks"],0,3,"Site preparation"),"Concreter":(["dwelling","townhouse","units","apartment","building"],1,5,"Foundations / structure"),"Bricklayer":(["dwelling","townhouse","units","apartment","building"],3,8,"Structure / envelope"),"Carpenter":(["dwelling","townhouse","units","apartment","building"],2,8,"Framing / fit-out"),"Roofer":(["dwelling","townhouse","units","apartment","building"],4,9,"Building envelope"),"Plumber":(["dwelling","townhouse","units","apartment","building","commercial"],3,10,"Rough-in / fit-off"),"Electrician":(["dwelling","townhouse","units","apartment","building","commercial"],3,11,"Rough-in / fit-off"),"HVAC":(["apartment","commercial","shop","office","building","units"],4,11,"Services / fit-off"),"Plasterer":(["dwelling","townhouse","units","apartment","building"],6,11,"Internal fit-out"),"Tiler":(["dwelling","townhouse","units","apartment","building"],7,12,"Internal finishes"),"Painter":(["dwelling","townhouse","units","apartment","building"],8,13,"Finishes"),"Landscaper":(["dwelling","townhouse","units","apartment","land division","subdivision"],9,15,"External completion"),"Fencer":(["dwelling","townhouse","units","land division","subdivision"],8,15,"External completion")}
LAYER="https://lsa4.geohub.sa.gov.au/server/rest/services/LSA/LocationSAViewerV34/MapServer/259/query"
def fetch_sa(limit):
    p={"where":"1=1","outFields":"decision,description,developmentnumber,decisiondate,applicationurl,urlonly","returnGeometry":"false","f":"json","resultRecordCount":limit,"orderByFields":"decisiondate DESC"}; r=requests.get(LAYER,params=p,timeout=30,headers={"User-Agent":"Tradara/2.0"}); r.raise_for_status(); return r.json()
def todt(ms):
    try:return pd.to_datetime(ms,unit="ms") if ms else pd.NaT
    except:return pd.NaT
def opportunity_rows(data,trades):
    out=[]
    for f in data.get("features",[]):
        p=f.get("attributes",f.get("properties",{})); desc=(p.get("description") or "").lower(); d=todt(p.get("decisiondate")); age=None if pd.isna(d) else max(0,(pd.Timestamp.now()-d).days/30.44)
        for t in trades:
            keys,start,end,phase=TRADE_INTEL[t]; hits=sum(k in desc for k in keys)
            if not hits: continue
            score=min(40,20+hits*7); decision=(p.get("decision") or "").lower()
            if any(x in decision for x in ["approved","granted","consent"]): score+=20
            if age is None: action="VERIFY TIMING"
            elif age<start: action="CONTACT NOW — pre-position"; score+=20
            elif age<=end: action="CONTACT NOW — trade window"; score+=30
            elif age<=end+3: action="LATE WINDOW — verify"; score+=8
            else: action="LIKELY PASSED — verify"; score-=15
            out.append({"Score":max(0,min(100,score)),"Action":action,"Trade":t,"Phase":phase,"Development":p.get("developmentnumber") or "Unknown","Description":p.get("description") or "No description","Decision date":d,"PlanSA":p.get("applicationurl") or p.get("urlonly") or ""})
    return pd.DataFrame(out)
def get_profile():
    try:return cloud.get_profile(UID)
    except Exception:
        st.error("Your company profile could not load. Please try again shortly.")
        st.stop()
def pipeline_df():
    try:return cloud.pipeline_df(UID)
    except Exception:
        st.error("Your pipeline could not load. Please try again shortly.")
        st.stop()
def save_lead(dev,trade,status="Saved",notes="",value=0):return cloud.save_lead(UID,dev,trade,status,notes,value)

def pref_list(profile,key):
    v=(profile or {}).get(key) or []
    return v if isinstance(v,list) else [x for x in str(v).split(",") if x]
def fit_boost(row,profile):
    if not profile:return 0,"Complete your company profile to personalise this score"
    boost=0; why=[]; desc=str(row["Description"]).lower()
    if any(x.lower() in desc for x in pref_list(profile,"preferred_project_types")):boost+=8;why.append("preferred project type")
    if row["Trade"] in pref_list(profile,"preferred_trades"):boost+=8;why.append("core company trade")
    if str(row["Action"]).startswith("CONTACT NOW"):boost+=5;why.append("good timing")
    return boost,", ".join(why) or "general company fit"

st.markdown('<div class="brand"><div class="mark">T</div><div><div class="name">Tradara</div><div class="sub">CONSTRUCTION OPPORTUNITY INTELLIGENCE</div></div></div>',unsafe_allow_html=True)
with st.sidebar:
    st.markdown("### Your Tradara"); st.caption(user.email); st.divider()
    if st.button("Sign out",use_container_width=True): cloud.sign_out();st.session_state.session=None;st.session_state.pop("cloud",None);st.rerun()
st.markdown('<div class="hero"><span class="pill">CLOUD SYNC ACTIVE · SOUTH AUSTRALIA</span><h1>Turn development activity into your next best opportunity.</h1><p>Your profile, saved opportunities and pipeline now follow your Tradara account across desktop and mobile.</p></div>',unsafe_allow_html=True)

tabs=st.tabs(["🏢 Profile","🎯 Radar","📌 Pipeline","📅 Capacity","📈 Learning","⚙️ Account"])
with tabs[0]:
    prof=get_profile() or {}; st.subheader("Company profile"); st.caption("Tradara uses this to rank work around your business.")
    company=st.text_input("Company name",value=prof.get("company_name") or ""); location=st.text_input("Where are you based?",value=prof.get("base_location") or "",placeholder="e.g. Adelaide, SA"); description=st.text_area("Describe your company",value=prof.get("company_description") or "",placeholder="What work do you specialise in and what jobs do you want more of?")
    current=pref_list(prof,"preferred_trades"); trades=st.multiselect("Trades/services",list(TRADE_INTEL),default=[x for x in current if x in TRADE_INTEL]); types_all=["dwelling","townhouse","apartments","units","subdivision","land division","commercial","office","shop","renovation"]; current_types=pref_list(prof,"preferred_project_types"); types=st.multiselect("Preferred project types",types_all,default=[x for x in current_types if x in types_all])
    a,b,c=st.columns(3); dist=a.number_input("Travel distance (km)",10.0,500.0,float(prof.get("max_distance_km") or 50),5.0); minv=b.number_input("Minimum job value ($)",0.0,10000000.0,float(prof.get("min_job_value") or 5000),1000.0); maxv=c.number_input("Maximum job value ($)",0.0,100000000.0,float(prof.get("max_job_value") or 250000),5000.0); target=st.number_input("Revenue to fill ($)",0.0,100000000.0,float(prof.get("revenue_target") or 50000),5000.0)
    if st.button("Save profile to cloud",type="primary"):
        try:cloud.save_profile(UID,company,location,description,trades,types,dist,minv,maxv,date.today(),target);st.success("Saved. This profile is now synced to your account.")
        except Exception:st.error("Could not save your profile. Please try again.")
with tabs[1]:
    prof=get_profile() or {}; defaults=pref_list(prof,"preferred_trades") or ["Electrician"]; c1,c2,c3=st.columns([2,1,1]); chosen=c1.multiselect("Trades",list(TRADE_INTEL),default=[x for x in defaults if x in TRADE_INTEL]); minscore=c2.slider("Minimum score",0,100,55,5); limit=c3.select_slider("Scan depth",[250,500,1000,1500,2000],value=1000)
    if st.button("Refresh opportunity radar",type="primary"):
        try:
            with st.spinner("Scanning development activity..."):st.session_state.raw=fetch_sa(limit)
        except Exception:st.error("Radar could not load. Please try again shortly.")
    if "raw" not in st.session_state:st.info("Tap **Refresh opportunity radar** to scan current development activity.")
    else:
        df=opportunity_rows(st.session_state.raw,chosen) if chosen else pd.DataFrame()
        if not df.empty:
            fits=df.apply(lambda r:fit_boost(r,prof),axis=1);df["Tradara Score"]=(df.Score+[x[0] for x in fits]).clip(upper=100);df["Why it fits"]=[x[1] for x in fits];df=df[df["Tradara Score"]>=minscore].sort_values("Tradara Score",ascending=False)
        if df.empty:st.warning("No matching opportunities at this score. Try lowering the minimum score.")
        else:
            for idx,r in df.head(15).iterrows():
                with st.container(border=True):
                    st.markdown(f"### {int(r['Tradara Score'])}/100 · {r['Trade']}");st.markdown(f"**{r['Action']}** · {r['Phase']}");st.write(r["Description"]);st.caption(f"Why it fits: {r['Why it fits']}");x,y=st.columns(2)
                    if r["PlanSA"]:x.link_button("Verify project",r["PlanSA"],use_container_width=True)
                    if y.button("Save to pipeline",key=f"save{idx}",use_container_width=True):
                        try:save_lead(r["Development"],r["Trade"]);st.toast("Saved — synced to your Tradara account")
                        except Exception:st.error("Could not save this opportunity. Please try again.")
with tabs[2]:
    p=pipeline_df();st.subheader("My pipeline")
    if p.empty:st.info("Save opportunities from Radar and they will appear here on every device.")
    else:
        for _,r in p.iterrows():
            key=f"{r['development']}{r['trade']}"
            with st.expander(f"{r['status']} · {r['trade']} · {r['development']}"):
                opts=["Saved","Contacted","Quoted","Won","Lost","Not relevant"];status=st.selectbox("Stage",opts,index=opts.index(r["status"]) if r["status"] in opts else 0,key="s"+key);value=st.number_input("Estimated value ($)",0.0,value=float(r.get("est_value") or 0),step=1000.0,key="v"+key);notes=st.text_area("Notes",value=r.get("notes") or "",key="n"+key)
                if st.button("Update",key="u"+key):
                    try:save_lead(r["development"],r["trade"],status,notes,value);st.success("Updated in cloud")
                    except Exception:st.error("Could not update this opportunity. Please try again.")
        p=pipeline_df();a,b,c=st.columns(3);a.metric("Quoted",f"${p[p.status=='Quoted'].est_value.sum():,.0f}");b.metric("Won",f"${p[p.status=='Won'].est_value.sum():,.0f}");c.metric("Active",int(p.status.isin(["Saved","Contacted","Quoted"]).sum()))
with tabs[3]:
    prof=get_profile() or {};p=pipeline_df();target=float(prof.get("revenue_target") or 50000);won=p[p.status=="Won"].est_value.sum() if not p.empty else 0;quoted=p[p.status=="Quoted"].est_value.sum() if not p.empty else 0;gap=max(0,target-won);st.subheader("Capacity planner");a,b,c=st.columns(3);a.metric("Target",f"${target:,.0f}");b.metric("Won",f"${won:,.0f}");c.metric("Unfilled",f"${gap:,.0f}");st.write(f"Quoted pipeline: **${quoted:,.0f}**")
with tabs[4]:
    p=pipeline_df();st.subheader("Performance intelligence")
    if p.empty or p[p.status.isin(["Won","Lost"])].empty:st.info("Mark opportunities Won or Lost and Tradara will begin learning from your outcomes.")
    else:
        d=p[p.status.isin(["Won","Lost"])];summary=d.groupby("trade").agg(Decisions=("status","size"),Wins=("status",lambda x:(x=="Won").sum())).reset_index();summary["Win rate"]=summary.Wins/summary.Decisions;st.dataframe(summary,use_container_width=True,hide_index=True)
with tabs[5]:
    st.subheader("Account settings")
    if st.session_state.pop("recovery_mode",False):
        st.info("Recovery link verified. Enter your new password below, then sign in again on your other devices.")
    st.write(f"Signed in as **{user.email}**")
    st.caption("Your company profile and pipeline are stored with your account.")
    with st.form("change_password"):
        new_password=st.text_input("New password",type="password")
        confirm_password=st.text_input("Confirm new password",type="password")
        if st.form_submit_button("Change password"):
            if len(new_password)<6 or new_password!=confirm_password: st.error("Enter matching passwords of at least 6 characters.")
            else:
                try: cloud.update_password(new_password);st.success("Password updated.")
                except Exception: st.error("Password could not be updated. Please try again.")
    st.divider()
    st.markdown("### Delete account")
    st.write("This permanently removes your Tradara account, company profile and saved pipeline.")
    confirmation=st.text_input("Type DELETE to confirm",key="delete_confirmation")
    if st.button("Permanently delete my account",disabled=confirmation!="DELETE"):
        try:
            cloud.delete_account()
            cloud.sign_out();st.session_state.session=None;st.session_state.pop("cloud",None)
            st.success("Your account has been deleted.");st.rerun()
        except Exception: st.error("Account deletion failed. Your account remains active. Please try again.")
st.divider();st.caption("Tradara provides opportunity signals, not proof that a contractor is unappointed. Verify project timing and procurement before outreach.")
