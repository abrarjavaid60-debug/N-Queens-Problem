"""Simple admin authentication for a classroom/demo project.
Set SMART_CAMPUS_ADMIN_PASSWORD in your environment before deployment.
"""
import hmac
import os
import streamlit as st

DEMO_PASSWORD = "admin123!"


def require_admin_login():
    if st.session_state.get("admin_authenticated", False):
        return True
    st.subheader("Administrator login")
    st.caption("Only authorised campus staff should access complaint management.")
    with st.form("admin_login_form"):
        password = st.text_input("Admin password", type="password")
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
    if submitted:
        expected = os.environ.get("SMART_CAMPUS_ADMIN_PASSWORD", DEMO_PASSWORD)
        if hmac.compare_digest(password.encode("utf-8"), expected.encode("utf-8")):
            st.session_state["admin_authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    if "SMART_CAMPUS_ADMIN_PASSWORD" not in os.environ:
        st.warning("Demo password is active: admin123! Set SMART_CAMPUS_ADMIN_PASSWORD before sharing or deploying this app.")
    return False
