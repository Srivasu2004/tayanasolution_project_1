import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="CodeGuardian", page_icon="🛡️", layout="wide")
st.title("🛡️ CodeGuardian")
st.caption("Autonomous AI-powered Python code review, refactoring and validation")

with st.sidebar:
    st.header("Settings")
    use_ai = st.toggle("Enable AI review", value=True)
    st.caption("AI features require GROQ_API_KEY in the backend .env file.")
    st.write("Backend:", API_URL)
    if st.button("Check backend"):
        try:
            r = requests.get(f"{API_URL}/health", timeout=5)
            st.success(r.json())
        except requests.RequestException as exc:
            st.error(str(exc))

tab_paste, tab_upload = st.tabs(["Paste code", "Upload Python file"])
code = ""

with tab_paste:
    code = st.text_area(
        "Python source code",
        height=360,
        placeholder="def add(a, b):\n    return a + b\n",
    )
    review_clicked = st.button("🔍 Review code", type="primary", key="paste_review")

with tab_upload:
    uploaded = st.file_uploader("Choose a .py file", type=["py"])
    upload_clicked = st.button("📄 Review uploaded file", type="primary")
    if uploaded:
        try:
            code = uploaded.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            st.error("Please upload a UTF-8 encoded Python file.")
            code = ""

def show_review(result):
    syntax = result.get("syntax", {})
    if syntax.get("ok"):
        st.success("Syntax check passed")
    else:
        st.error(f"Syntax error: {syntax.get('message')} (line {syntax.get('line')})")

    findings = result.get("static_findings", [])
    st.subheader("Rule-based findings")
    if findings:
        st.dataframe(findings, use_container_width=True)
    else:
        st.info("No built-in rule findings.")

    st.subheader("Optional static-analysis tools")
    tools = result.get("tool_results", {})
    c1, c2 = st.columns(2)
    c1.markdown("**Ruff**")
    c1.code(str(tools.get("ruff", "Not run")), language="json")
    c2.markdown("**Bandit**")
    c2.code(str(tools.get("bandit", "Not run")), language="json")

    st.subheader("AI review")
    ai = result.get("ai_review")
    if ai:
        st.markdown(ai)
    elif not result.get("ai_available"):
        st.warning("AI is not configured. Add GROQ_API_KEY to backend/.env and restart the backend.")
    else:
        st.info("AI review was skipped or unavailable.")

if review_clicked and code.strip():
    try:
        with st.spinner("Analyzing your code..."):
            response = requests.post(
                f"{API_URL}/review",
                json={"code": code, "use_ai": use_ai},
                timeout=120,
            )
        response.raise_for_status()
        show_review(response.json())
        st.session_state["last_code"] = code
    except requests.RequestException as exc:
        st.error(f"Review request failed: {exc}")
elif review_clicked:
    st.warning("Paste Python code first.")

if upload_clicked:
    if not uploaded:
        st.warning("Choose a .py file first.")
    else:
        try:
            with st.spinner("Uploading and reviewing..."):
                response = requests.post(
                    f"{API_URL}/upload-review",
                    files={"file": (uploaded.name, uploaded.getvalue(), "text/x-python")},
                    params={"use_ai": use_ai},
                    timeout=120,
                )
            response.raise_for_status()
            st.success(f"Reviewed: {response.json().get('filename')}")
            show_review(response.json()["review"])
            st.session_state["last_code"] = code
        except requests.RequestException as exc:
            st.error(f"Upload review failed: {exc}")

source_for_refactor = st.session_state.get("last_code", "")
if source_for_refactor:
    st.divider()
    st.subheader("♻️ Refactor and validate")
    if st.button("Generate refactored code", type="primary"):
        try:
            with st.spinner("Generating and validating refactored code..."):
                response = requests.post(
                    f"{API_URL}/refactor",
                    json={"code": source_for_refactor, "use_ai": use_ai},
                    timeout=180,
                )
            response.raise_for_status()
            data = response.json()
            left, right = st.columns(2)
            with left:
                st.markdown("**Original code**")
                st.code(data["original_code"], language="python")
            with right:
                st.markdown("**Refactored code**")
                st.code(data["refactored_code"], language="python")
                st.download_button(
                    "Download refactored .py",
                    data=data["refactored_code"],
                    file_name="refactored_code.py",
                    mime="text/x-python",
                )
            if data["validation"]["syntax_valid"]:
                st.success("Refactored source passed syntax validation.")
            else:
                st.error("Refactored source failed syntax validation.")
            st.caption(data["validation"]["note"])
        except requests.RequestException as exc:
            st.error(f"Refactoring failed: {exc}")

st.divider()
st.caption("Safety: CodeGuardian does not execute uploaded or pasted code. Static checks and syntax validation are not a substitute for isolated tests and human review.")
