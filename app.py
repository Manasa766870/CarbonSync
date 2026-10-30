import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from backend.database import init_db
from backend.auth import register_user, authenticate_user
from backend.services import get_user, update_profile, save_message, get_messages, get_dashboard_stats
from backend.agent_client import ask_agent
from backend.i18n import T

st.set_page_config(page_title="Carbon Sync", page_icon="🌱", layout="wide")
init_db()

LANGUAGES = {"English": "en", "తెలుగు": "te", "हिन्दी": "hi"}

def tr(key):
    lang = st.session_state.get("language", "en")
    return T.get(lang, T["en"]).get(key, T["en"].get(key, key))

def logout():
    for key in ["user_id", "user_name", "page", "chat_session_id"]:
        st.session_state.pop(key, None)
    st.rerun()

if "language" not in st.session_state:
    st.session_state.language = "en"
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Top bar
left, right = st.columns([4, 1])
with left:
    st.markdown("<h1 style='margin-bottom:0;color:#16845b'>🌱 Carbon Sync</h1><p style='color:gray;margin-top:0'>Small actions. A greener campus.</p>", unsafe_allow_html=True)
with right:
    selected = st.selectbox("Language / భాష / भाषा", list(LANGUAGES.keys()),
        index=list(LANGUAGES.values()).index(st.session_state.language))
    st.session_state.language = LANGUAGES[selected]

if "user_id" not in st.session_state:
    tab1, tab2 = st.tabs([tr("home"), tr("login_signup")])
    with tab1:
        st.markdown("## " + tr("hero_title"))
        st.write(tr("hero_subtitle"))
        c1, c2, c3 = st.columns(3)
        c1.metric(tr("feature_track"), "📊")
        c2.metric(tr("feature_chat"), "🤖")
        c3.metric(tr("feature_campus"), "🏫")
        st.info(tr("landing_note"))
        st.markdown("### " + tr("how_it_works"))
        st.write("1. " + tr("step1"))
        st.write("2. " + tr("step2"))
        st.write("3. " + tr("step3"))
    with tab2:
        mode = st.radio(tr("account"), [tr("signup"), tr("login")], horizontal=True)
        if mode == tr("signup"):
            with st.form("signup_form"):
                name = st.text_input(tr("full_name"))
                email = st.text_input(tr("email"))
                password = st.text_input(tr("password"), type="password")
                hostel = st.text_input(tr("hostel"))
                department = st.text_input(tr("department"))
                submitted = st.form_submit_button(tr("create_account"), use_container_width=True)
            if submitted:
                ok, msg, uid = register_user(name, email, password, hostel, department)
                if ok:
                    st.session_state.user_id = uid
                    st.session_state.user_name = name
                    st.success(tr("signup_success"))
                    st.rerun()
                else:
                    st.error(msg)
        else:
            with st.form("login_form"):
                email = st.text_input(tr("email"))
                password = st.text_input(tr("password"), type="password")
                submitted = st.form_submit_button(tr("login"), use_container_width=True)
            if submitted:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.user_id = user["id"]
                    st.session_state.user_name = user["name"]
                    st.success(tr("welcome_back"))
                    st.rerun()
                else:
                    st.error(tr("invalid_login"))
    st.stop()

user = get_user(st.session_state.user_id)
if not user:
    logout()

with st.sidebar:
    st.success(f"{tr('hello')}, {user['name']}")
    page = st.radio(tr("navigation"), [tr("dashboard"), tr("chatbot"), tr("profile")],
                    key="nav_radio")
    st.divider()
    st.caption(f"{tr('hostel')}: {user['hostel'] or '—'}")
    st.caption(f"{tr('department')}: {user['department'] or '—'}")
    if st.button(tr("logout"), use_container_width=True):
        logout()

if page == tr("dashboard"):
    st.title(tr("dashboard"))
    stats = get_dashboard_stats(user["id"])
    a, b, c = st.columns(3)
    a.metric(tr("logged_activities"), stats["activity_count"])
    b.metric(tr("calculated_footprint"), f'{stats["total_kg"]:.3f} kg')
    c.metric(tr("chat_messages"), stats["message_count"])
    st.info(tr("dashboard_note"))
    st.subheader(tr("recent_activity"))
    if stats["activities"]:
        st.dataframe(stats["activities"], use_container_width=True, hide_index=True)
    else:
        st.write(tr("no_activities"))

elif page == tr("chatbot"):
    st.title("🤖 " + tr("chatbot"))
    st.write(tr("chat_intro"))
    if "chat_session_id" not in st.session_state:
        import uuid
        st.session_state.chat_session_id = str(uuid.uuid4())
    history = get_messages(user["id"], st.session_state.chat_session_id)
    for item in history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
    prompt = st.chat_input(tr("chat_placeholder"))
    if prompt:
        save_message(user["id"], st.session_state.chat_session_id, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner(tr("thinking")):
                reply = ask_agent(
                    message=prompt,
                    user_id=user["id"],
                    language=st.session_state.language,
                    session_id=st.session_state.chat_session_id
                )
                st.markdown(reply)
        save_message(user["id"], st.session_state.chat_session_id, "assistant", reply)

elif page == tr("profile"):
    st.title("👤 " + tr("profile"))
    with st.form("profile_form"):
        name = st.text_input(tr("full_name"), value=user["name"])
        email = st.text_input(tr("email"), value=user["email"], disabled=True)
        hostel = st.text_input(tr("hostel"), value=user["hostel"] or "")
        department = st.text_input(tr("department"), value=user["department"] or "")
        save = st.form_submit_button(tr("save_profile"))
    if save:
        update_profile(user["id"], name, hostel, department)
        st.session_state.user_name = name
        st.success(tr("profile_saved"))
        st.rerun()
    st.caption(tr("profile_privacy"))
