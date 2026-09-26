import sqlite3, re, requests
from datetime import date
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tradara | Construction Opportunity Intelligence", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")
DB="/tmp/tradara.db"

st.markdown("""
<style>
:root{--ink:#0b1020;--blue:#5b6cff;--cyan:#22d3ee;--muted:#667085;--line:#e6eaf0}
.stApp{background:radial-gradient(circle at 90% 0%,rgba(91,108,255,.08),transparent 28%),#fbfcfe;color:var(--ink)}
.block-container{max-width:1440px;padding:1.4rem 2.2rem 5rem}
[data-testid="stSidebar"]{background:#0c1222;border-right:1px solid rgba(255,255,255,.06)}
[data-testid="stSidebar"] *{color:#eef2ff}[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.1)}
[data-testid="stSidebar"] .stButton>button{background:linear-gradient(135deg,#6675ff,#4f5de8);border:0;color:white;box-shadow:0 10px 24px rgba(79,93,232,.28)}
h1,h2,h3{letter-spacing:-.035em;color:var(--ink)}
.tp-brand{display:flex;align-items:center;gap:.85rem;margin:0 0 1.2rem}.tp-mark{width:46px;height:46px;border-radius:14px;background:linear-gradient(135deg,#6d7cff,#4857dc);color:white;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:22px;box-shadow:0 10px 28px rgba(79,93,232,.25)}
.tp-name{font-size:25px;font-weight:850;letter-spacing:-.05em;line-height:1.05}.tp-sub{color:#7c879c;font-size:12px;margin-top:4px;text-transform:uppercase;letter-spacing:.11em;font-weight:700}
.tp-hero{position:relative;overflow:hidden;padding:42px 44px;border:1px solid rgba(91,108,255,.14);border-radius:24px;background:linear-gradient(135deg,#10182b 0%,#162344 55%,#25336c 100%);margin:0 0 26px;box-shadow:0 20px 55px rgba(16,24,40,.14)}
.tp-hero:after{content:"";position:absolute;width:360px;height:360px;border-radius:50%;right:-120px;top:-190px;background:radial-gradient(circle,rgba(34,211,238,.30),rgba(91,108,255,.08) 45%,transparent 70%)}
.tp-hero h2{position:relative;z-index:1;margin:0 0 10px;color:white;font-size:38px;line-height:1.08;max-width:780px}.tp-hero p{position:relative;z-index:1;margin:0;color:#c9d2e7;font-size:16px;max-width:780px;line-height:1.6}.tp-pill{position:relative;z-index:1;display:inline-flex;padding:7px 11px;border-radius:999px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.13);color:#bdefff;font-size:11px;font-weight:800;letter-spacing:.08em;margin-bottom:14px}
[data-baseweb="tab-list"]{gap:8px;background:#fff;border:1px solid var(--line);padding:7px;border-radius:16px;box-shadow:0 8px 24px rgba(16,24,40,.04)}button[data-baseweb="tab"]{border-radius:10px;padding:10px 15px!important}button[data-baseweb="tab"][aria-selected="true"]{background:#eef1ff}
div[data-testid="stMetric"]{border:1px solid var(--line);border-radius:18px;padding:18px 20px;background:rgba(255,255,255,.92);box-shadow:0 8px 26px rgba(16,24,40,.045)}div[data-testid="stMetricValue"]{font-weight:850;letter-spacing:-.04em}
div[data-testid="stExpander"]{border:1px solid var(--line);border-radius:16px;background:white;box-shadow:0 7px 22px rgba(16,24,40,.035)}
.stButton>button,.stLinkButton>a{border-radius:11px;font-weight:750;min-height:42px;transition:.18s ease}.stButton>button:hover,.stLinkButton>a:hover{transform:translateY(-1px)}.stButton>button[kind="primary"]{background:linear-gradient(135deg,#6574ff,#4d5bd9);border:0;box-shadow:0 8px 22px rgba(79,93,232,.22)}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:15px;overflow:hidden;box-shadow:0 8px 24px rgba(16,24,40,.035)}.stTextInput input,.stTextArea textarea,.stNumberInput input{border-radius:10px!important}.stAlert{border-radius:14px}hr{border-color:var(--line)}
@media(max-width:800px){.block-container{padding:1rem 1rem 4rem}.tp-hero{padding:30px 24px}.tp-hero h2{font-size:30px}}
</style>
""", unsafe_allow_html=True)

LAYER="https://lsa4.geohub.sa.gov.au/server/rest/services/LSA/LocationSAViewerV34/MapServer/259/query"
TRADE_INTEL={
"Earthworks":{"keys":["land division","subdivision","excavation","earthworks","site works"],"start":0,"end":3,"phase":"Site preparation"},
"Concreter":{"keys":["dwelling","residential","townhouse","units","apartment","building","footing","slab"],"start":1,"end":5,"phase":"Foundations / structure"},
"Bricklayer":{"keys":["dwelling","residential","townhouse","units","apartment","building"],"start":3,"end":8,"phase":"Structure / envelope"},
"Carpenter":{"keys":["dwelling","residential","townhouse","units","apartment","building"],"start":2,"end":8,"phase":"Framing / fit-out"},
"Roofer":{"keys":["dwelling","residential","townhouse","units","apartment","building"],"start":4,"end":9,"phase":"Building envelope"},
"Plumber":{"keys":["dwelling","residential","townhouse","units","apartment","building","commercial"],"start":3,"end":10,"phase":"Rough-in / fit-off"},
"Electrician":{"keys":["dwelling","residential","townhouse","units","apartment","building","commercial"],"start":3,"end":11,"phase":"Rough-in / fit-off"},
"HVAC":{"keys":["apartment","commercial","shop","office","building","units"],"start":4,"end":11,"phase":"Services / fit-off"},
"Plasterer":{"keys":["dwelling","residential","townhouse","units","apartment","building"],"start":6,"end":11,"phase":"Internal fit-out"},
"Tiler":{"keys":["dwelling","residential","townhouse","units","apartment","building"],"start":7,"end":12,"phase":"Internal finishes"},
"Painter":{"keys":["dwelling","residential","townhouse","units","apartment","building"],"start":8,"end":13,"phase":"Finishes"},
"Landscaper":{"keys":["dwelling","residential","townhouse","units","apartment","land division","subdivision"],"start":9,"end":15,"phase":"External completion"},
"Fencer":{"keys":["dwelling","residential","townhouse","units","land division","subdivision"],"start":8,"end":15,"phase":"External completion"}}

def conn():
    c=sqlite3.connect(DB,check_same_thread=False)
    c.execute("""CREATE TABLE IF NOT EXISTS pipeline(development TEXT, trade TEXT, status TEXT, notes TEXT, est_value REAL, first_saved TEXT, last_updated TEXT, PRIMARY KEY(development,trade))""")
    c.execute("""CREATE TABLE IF NOT EXISTS profile(id INTEGER PRIMARY KEY CHECK(id=1), company_name TEXT, base_location TEXT, company_description TEXT, preferred_trades TEXT, preferred_project_types TEXT, max_distance_km REAL, min_job_value REAL, max_job_value REAL, target_month TEXT, revenue_target REAL)""")
    c.commit(); return c
C=conn()

def get_profile():
    try:
        x=pd.read_sql_query("SELECT * FROM profile WHERE id=1",C); return None if x.empty else x.iloc[0].to_dict()
    except Exception:return None

def save_profile(name,location,description,trades,types,maxdist,minval,maxval,targetmonth,revenue):
    C.execute("DELETE FROM profile WHERE id=1")
    C.execute("""INSERT INTO profile(id,company_name,base_location,company_description,preferred_trades,preferred_project_types,max_distance_km,min_job_value,max_job_value,target_month,revenue_target) VALUES(1,?,?,?,?,?,?,?,?,?,?)""",(name,location,description,",".join(trades),",".join(types),maxdist,minval,maxval,str(targetmonth),revenue)); C.commit()

def profile_keywords(profile):
    text=((profile or {}).get("company_description") or "").lower(); vocab=["residential","commercial","apartment","apartments","townhouse","townhouses","dwelling","dwellings","subdivision","land division","units","renovation","new build","solar","industrial","office","shop","multi-storey","luxury"]; return [v for v in vocab if v in text]

def preference_boost(row,profile):
    if not profile:return 0,"No company profile yet"
    boost=0; why=[]; preferred=[x for x in (profile.get("preferred_project_types") or "").split(",") if x]; desc=(row.get("Description") or "").lower()
    if any(p.lower() in desc for p in preferred):boost+=8; why.append("preferred project type")
    if any(k in desc for k in profile_keywords(profile)):boost+=7; why.append("matches company description")
    if row.get("Trade") in [x for x in (profile.get("preferred_trades") or "").split(",") if x]:boost+=8; why.append("core company trade")
    if row.get("Action","").startswith("CONTACT NOW"):boost+=5; why.append("timing suits active prospecting")
    return min(boost,25),(", ".join(why) if why else "general fit")

def fetch_sa(limit):
    p={"where":"1=1","outFields":"appid,decision,description,developmentnumber,applicationtype,lodgementdate,applicationstatus,consenttype,decisiondate,completeddate,applicationurl,urlonly","returnGeometry":"true","outSR":"4326","f":"geojson","resultRecordCount":limit,"orderByFields":"decisiondate DESC"}
    r=requests.get(LAYER,params=p,timeout=30,headers={"User-Agent":"Tradara/1.0"}); r.raise_for_status(); payload=r.json()
    if "features" not in payload:raise RuntimeError("The SA development service returned an unexpected response.")
    return payload

def dt(ms):
    try:return pd.to_datetime(ms,unit="ms") if ms else pd.NaT
    except:return pd.NaT

def months_since(x):return None if pd.isna(x) else max(0,(pd.Timestamp.now().tz_localize(None)-x).days/30.44)
def scale(desc):
    d=(desc or "").lower()
    if "land division" in d or "subdivision" in d:return "Multi-lot / land",8
    nums=[int(x) for x in re.findall(r"\b(\d{1,3})\b",d)]; n=max(nums) if nums else 1; return ("Large",12) if n>=10 else ("Medium",7) if n>=3 else ("Small / unknown",0)
def timing(age,i):
    if age is None:return "VERIFY TIMING",0
    s,e=i["start"],i["end"]
    if age<s-2:return f"EARLY — watch (~{max(1,round(s-age))} mo)",4
    if age<s:return "CONTACT NOW — pre-position",20
    if age<=e:return "CONTACT NOW — trade window",30
    if age<=e+3:return "LATE WINDOW — verify",8
    return "LIKELY PASSED — verify",-15

def score(p,trade):
    d=(p.get("description") or "").lower(); i=TRADE_INTEL[trade]; hits=sum(k in d for k in i["keys"])
    if not hits:return None
    x=min(40,20+hits*7); dec=(p.get("decision") or "").lower()
    if any(k in dec for k in ["approved","granted","consent"]):x+=20
    age=months_since(dt(p.get("decisiondate"))); action,b=timing(age,i); x+=b; sc,sb=scale(d); x+=sb
    return max(0,min(100,x)),action,i["phase"],age,sc

def rows(data,trades):
    out=[]
    for f in data.get("features",[]):
        p=f["properties"]
        for t in trades:
            z=score(p,t)
            if z:
                s,a,ph,age,sc=z; out.append({"Score":s,"Action":a,"Trade":t,"Phase":ph,"Development":p.get("developmentnumber",""),"Description":p.get("description",""),"Scale":sc,"Decision":p.get("decision",""),"Decision date":dt(p.get("decisiondate")),"Months":round(age,1) if age is not None else None,"PlanSA":p.get("applicationurl") or p.get("urlonly") or ""})
    return pd.DataFrame(out)
def pipeline_df():return pd.read_sql_query("SELECT * FROM pipeline ORDER BY last_updated DESC",C)
def save_lead(dev,trade,status="Saved",notes="",value=0):
    today=str(date.today()); C.execute("""INSERT INTO pipeline VALUES(?,?,?,?,?,?,?) ON CONFLICT(development,trade) DO UPDATE SET status=excluded.status,notes=excluded.notes,est_value=excluded.est_value,last_updated=excluded.last_updated""",(dev,trade,status,notes,value,today,today)); C.commit()
def outcome_stats():
    p=pipeline_df(); result={}
    if p.empty:return result
    for t,g in p.groupby("trade"):
        won=(g.status=="Won").sum(); decided=g.status.isin(["Won","Lost"]).sum(); result[t]=(won/decided if decided else None,won,decided)
    return result

st.markdown("""<div class="tp-brand"><div class="tp-mark">T</div><div><div class="tp-name">Tradara</div><div class="tp-sub">Construction Opportunity Intelligence</div></div></div><div class="tp-hero"><span class="tp-pill">SOUTH AUSTRALIA · LIVE OPPORTUNITY RADAR</span><h2>Turn development activity into your next best opportunity.</h2><p>A modern intelligence workspace for contractors — ranked opportunities, trade timing, pipeline visibility and capacity planning in one place.</p></div>""",unsafe_allow_html=True)

tabs=st.tabs(["🏢 Company Profile","🎯 Tradara Radar","📌 My Pipeline","📅 Capacity Planner","📈 Learning"])
with tabs[0]:
    st.subheader("Company profile"); st.caption("Personalise Tradara around the work your business actually wants."); prof=get_profile() or {}
    company=st.text_input("Company name",value=prof.get("company_name") or ""); location=st.text_input("Where are you based?",value=prof.get("base_location") or "",placeholder="e.g. Salisbury, SA")
    description=st.text_area("Describe your company",value=prof.get("company_description") or "",placeholder="e.g. We are a 4-person electrical contractor specialising in new residential builds and townhouse developments.")
    current_trades=[x for x in (prof.get("preferred_trades") or "").split(",") if x]; preferred_trades=st.multiselect("What trades/services do you provide?",list(TRADE_INTEL),default=[x for x in current_trades if x in TRADE_INTEL])
    types=["dwelling","townhouse","apartments","units","subdivision","land division","commercial","office","shop","renovation"]; current_types=[x for x in (prof.get("preferred_project_types") or "").split(",") if x]; preferred_types=st.multiselect("Preferred project types",types,default=[x for x in current_types if x in types])
    c1,c2,c3=st.columns(3); maxdist=c1.number_input("Maximum travel distance (km)",10.0,500.0,float(prof.get("max_distance_km") or 50),5.0); minval=c2.number_input("Preferred minimum job value ($)",0.0,10000000.0,float(prof.get("min_job_value") or 5000),1000.0); maxval=c3.number_input("Preferred maximum job value ($)",0.0,100000000.0,float(prof.get("max_job_value") or 250000),5000.0)
    targetmonth=st.date_input("When do you next need work?",value=date.today()); revenue=st.number_input("Revenue you want to fill ($)",0.0,100000000.0,float(prof.get("revenue_target") or 50000),5000.0)
    if st.button("Save company profile",type="primary"):save_profile(company,location,description,preferred_trades,preferred_types,maxdist,minval,maxval,targetmonth,revenue); st.success("Company profile saved. Tradara Radar will now rank work around these preferences.")
    st.info("Exact kilometre filtering will become active once project-address geocoding is added.")
with tabs[1]:
    with st.sidebar:
        st.markdown("### Tradara"); st.caption("Opportunity Radar"); st.divider(); trades=st.multiselect("My trades",list(TRADE_INTEL),default=["Electrician"]); minscore=st.slider("Minimum score",0,100,55,5); limit=st.slider("Applications scanned",250,2000,1500,250); refresh=st.button("Refresh radar",type="primary",use_container_width=True)
    if refresh:
        try:
            with st.spinner("Reading SA development data..."):st.session_state.raw=fetch_sa(limit)
        except Exception as e:st.error(f"Could not load the SA development feed: {e}")
    if "raw" not in st.session_state:st.info("Click **Refresh radar** in the sidebar to load current South Australian development opportunities."); df=pd.DataFrame()
    else:df=rows(st.session_state.raw,trades) if trades else pd.DataFrame()
    if not df.empty:df=df[df.Score>=minscore].sort_values(["Score","Decision date"],ascending=[False,False])
    if df.empty:st.warning("No matches.")
    else:
        stats=outcome_stats()
        def personal(r):
            q=stats.get(r.Trade)
            if not q or q[0] is None or q[2]<3:return r.Score
            return min(100,round(r.Score+(q[0]-.25)*12))
        profile=get_profile(); df["Personal score"]=df.apply(personal,axis=1); fits=df.apply(lambda r:preference_boost(r,profile),axis=1); df["Company fit boost"]=[x[0] for x in fits]; df["Why it fits you"]=[x[1] for x in fits]; df["Tradara Score"]=(df["Personal score"]+df["Company fit boost"]).clip(upper=100); df=df.sort_values(["Tradara Score","Personal score","Score"],ascending=False)
        if profile:st.success(f"Recommendations personalised for {profile.get('company_name') or 'your company'} in {profile.get('base_location') or 'your area'}.")
        for idx,r in df.head(10).iterrows():
            with st.container(border=True):
                c1,c2,c3=st.columns([5,1,1])
                with c1:st.markdown(f"### {int(r['Tradara Score'])}/100 · {r.Trade} · {r.Action}"); st.write(r.Description); st.caption(f"{r.Phase} · {r.Scale} · Decision {r['Decision date'].date() if not pd.isna(r['Decision date']) else 'unknown'}"); st.markdown(f"**Why this suits your company:** {r['Why it fits you']}")
                with c2:
                    if r.PlanSA:st.link_button("Verify",r.PlanSA,use_container_width=True)
                with c3:
                    if st.button("Save",key=f"s{idx}",use_container_width=True):save_lead(r.Development,r.Trade); st.toast("Saved to pipeline")
        st.download_button("Export radar",df.to_csv(index=False).encode(),"tradara_radar.csv","text/csv")
with tabs[2]:
    p=pipeline_df(); st.subheader("Sales pipeline"); st.caption("Track opportunities from first look through to won work.")
    if p.empty:st.info("Save leads from Tradara Radar first.")
    else:
        for _,r in p.iterrows():
            with st.expander(f"{r['status']} · {r['trade']} · {r['development']}"):
                opts=["Saved","Contacted","Quoted","Won","Lost","Not relevant"]; status=st.selectbox("Stage",opts,index=opts.index(r["status"]) if r["status"] in opts else 0,key=f"st{r['development']}{r['trade']}"); val=st.number_input("Estimated job value ($)",min_value=0.0,value=float(r["est_value"] or 0),step=1000.0,key=f"v{r['development']}{r['trade']}"); notes=st.text_area("Notes",value=r["notes"] or "",key=f"n{r['development']}{r['trade']}")
                if st.button("Update",key=f"u{r['development']}{r['trade']}"):save_lead(r["development"],r["trade"],status,notes,val); st.success("Updated")
        p=pipeline_df(); quoted=p[p.status=="Quoted"]["est_value"].sum(); won=p[p.status=="Won"]["est_value"].sum(); c1,c2,c3=st.columns(3); c1.metric("Quoted pipeline",f"${quoted:,.0f}"); c2.metric("Won value",f"${won:,.0f}"); c3.metric("Active leads",int(p.status.isin(["Saved","Contacted","Quoted"]).sum()))
with tabs[3]:
    st.subheader("Capacity planner"); st.caption("See how much future work you still need to fill."); cp=get_profile() or {}; month=st.date_input("Target work month",value=date.today()); target=st.number_input("Revenue you want to fill ($)",min_value=0.0,value=float(cp.get("revenue_target") or 50000),step=5000.0); p=pipeline_df(); committed=p[p.status=="Won"]["est_value"].sum() if not p.empty else 0; quoted=p[p.status=="Quoted"]["est_value"].sum() if not p.empty else 0; gap=max(0,target-committed); c1,c2,c3=st.columns(3); c1.metric("Target",f"${target:,.0f}"); c2.metric("Won / committed",f"${committed:,.0f}"); c3.metric("Unfilled capacity",f"${gap:,.0f}")
    if gap:st.warning(f"You still need roughly ${gap:,.0f} of work. Prioritise CONTACT NOW leads and move them into the pipeline.")
    if quoted:st.write(f"You also have **${quoted:,.0f} quoted**. If all converted, remaining gap would be **${max(0,gap-quoted):,.0f}**.")
with tabs[4]:
    st.subheader("Performance intelligence"); st.caption("Tradara starts adapting as your won/lost history grows."); p=pipeline_df()
    if p.empty:st.info("No outcomes yet.")
    else:
        decided=p[p.status.isin(["Won","Lost"])]
        if decided.empty:st.info("Mark leads Won or Lost to start generating conversion data.")
        else:
            summary=decided.groupby("trade").agg(Decisions=("status","size"),Wins=("status",lambda x:(x=="Won").sum()),Won_value=("est_value",lambda x:x[decided.loc[x.index,"status"]=="Won"].sum())).reset_index(); summary["Win rate"]=summary["Wins"]/summary["Decisions"]; st.dataframe(summary,use_container_width=True,hide_index=True,column_config={"Win rate":st.column_config.ProgressColumn(min_value=0,max_value=1,format="%.0f%%")})
st.divider(); st.caption("Tradara provides prospecting signals, not proof that a contractor is unappointed. Verify project timing and procurement before outreach.")