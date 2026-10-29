"""Smart Campus — Student Complaint and Issue Management System."""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import (init_db, create_complaint, get_complaint, get_all_complaints,
                      update_status, CATEGORIES, PRIORITIES, STATUSES, add_sample_data)
from auth import require_admin_login
from analytics import make_category_chart, make_status_chart

st.set_page_config(page_title="Smart Campus", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")
init_db()

st.markdown("""
<style>
.block-container {padding-top: 1.8rem; padding-bottom: 2.5rem;}
[data-testid="stMetric"] {background: var(--secondary-background-color); padding: 15px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🎓 Smart Campus")
    st.caption("Student Complaint & Issue Management")
    page = st.radio("Navigation", ["Home", "Submit Complaint", "Track Complaint", "Admin Dashboard"], label_visibility="collapsed")
    st.divider()
    st.caption("University mini-project · Python · Streamlit · SQLite")


def show_metrics(df):
    total = len(df)
    pending = int((df["status"] == "Pending").sum()) if total else 0
    progress = int((df["status"] == "In Progress").sum()) if total else 0
    resolved = int((df["status"] == "Resolved").sum()) if total else 0
    cols = st.columns(4)
    for col, label, value in zip(cols, ["Total complaints", "Pending", "In progress", "Resolved"], [total, pending, progress, resolved]):
        col.metric(label, value)


if page == "Home":
    st.title("Smart Campus")
    st.subheader("A simpler way to report and resolve campus issues")
    st.write("Report problems such as Wi-Fi failures, broken classroom equipment, water supply issues and cleanliness concerns. Track progress using your complaint ID.")
    a, b, c = st.columns(3)
    with a:
        st.markdown("### 📝 Report")
        st.write("Submit a clear description, location and priority.")
    with b:
        st.markdown("### 🔎 Track")
        st.write("Use your unique ID to check the latest status.")
    with c:
        st.markdown("### 🛠️ Resolve")
        st.write("Authorised administrators review and update reports.")
    st.divider()
    df = get_all_complaints()
    st.markdown("#### Campus issue overview")
    show_metrics(df)
    st.info("Start by selecting **Submit Complaint** in the sidebar. Keep your complaint ID to track your report later.")

elif page == "Submit Complaint":
    st.title("Submit a complaint")
    st.write("Please provide enough detail for the campus team to locate and understand the issue.")
    with st.form("complaint_form", clear_on_submit=True):
        title = st.text_input("Complaint title *", max_chars=120, placeholder="e.g. Wi-Fi not working in library")
        description = st.text_area("Description *", max_chars=3000, height=130, placeholder="Explain what happened and any details that may help.")
        c1, c2 = st.columns(2)
        with c1:
            category = st.selectbox("Category *", CATEGORIES)
            location = st.text_input("Campus location *", max_chars=160, placeholder="e.g. Block A, Room 204")
        with c2:
            priority = st.selectbox("Priority *", PRIORITIES, index=1)
            st.caption("Urgent should be reserved for issues requiring immediate attention.")
        consent = st.checkbox("I confirm that the information provided is accurate.")
        submitted = st.form_submit_button("Submit complaint", type="primary", use_container_width=True)
    if submitted:
        if not title.strip() or not description.strip() or not location.strip():
            st.error("Please complete all required fields marked with *.")
        elif not consent:
            st.error("Please confirm that the information is accurate.")
        else:
            try:
                cid = create_complaint(title, description, category, location, priority)
                st.success("Complaint submitted successfully!")
                st.markdown("### Your complaint ID")
                st.code(cid, language=None)
                st.warning("Save this ID. You will need it to track your complaint.")
            except (ValueError, RuntimeError) as exc:
                st.error(str(exc))
            except Exception:
                st.error("Something went wrong while saving your complaint. Please try again.")

elif page == "Track Complaint":
    st.title("Track your complaint")
    st.write("Enter the unique complaint ID shown after submission.")
    with st.form("track_form"):
        cid = st.text_input("Complaint ID", placeholder="SC-YYYYMMDD-XXXXXXXX")
        search = st.form_submit_button("Find complaint", type="primary")
    if search:
        if not cid.strip():
            st.error("Enter a complaint ID first.")
        else:
            complaint = get_complaint(cid)
            if not complaint:
                st.error("No complaint found with that ID. Check the ID and try again.")
            else:
                st.success("Complaint found")
                st.subheader(complaint["title"])
                st.write(complaint["description"])
                x1, x2, x3 = st.columns(3)
                x1.metric("Status", complaint["status"])
                x2.metric("Priority", complaint["priority"])
                x3.metric("Category", complaint["category"])
                st.write("**Location:**", complaint["location"])
                st.write("**Complaint ID:**", complaint["complaint_id"])
                st.write("**Submitted:**", complaint["created_at"])
                st.write("**Last updated:**", complaint["updated_at"])

elif page == "Admin Dashboard":
    st.title("Administrator dashboard")
    if not require_admin_login():
        st.stop()
    top1, top2 = st.columns([4, 1])
    with top2:
        if st.button("Log out", use_container_width=True):
            st.session_state["admin_authenticated"] = False
            st.rerun()
    df = get_all_complaints()
    show_metrics(df)
    st.divider()
    st.subheader("Search and filter complaints")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        id_query = st.text_input("Complaint ID contains")
    with f2:
        category_filter = st.selectbox("Category", ["All"] + CATEGORIES)
    with f3:
        location_query = st.text_input("Location contains")
    with f4:
        status_filter = st.selectbox("Status", ["All"] + STATUSES)
    filtered = df.copy()
    if id_query.strip():
        filtered = filtered[filtered["complaint_id"].str.contains(id_query.strip(), case=False, na=False)]
    if category_filter != "All":
        filtered = filtered[filtered["category"] == category_filter]
    if location_query.strip():
        filtered = filtered[filtered["location"].str.contains(location_query.strip(), case=False, na=False)]
    if status_filter != "All":
        filtered = filtered[filtered["status"] == status_filter]
    st.caption(f"Showing {len(filtered)} of {len(df)} complaints")
    display_cols = ["complaint_id", "title", "category", "location", "priority", "status", "created_at"]
    if filtered.empty:
        st.info("No complaints match these filters.")
    else:
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)
    st.divider()
    st.subheader("Update complaint status")
    if not df.empty:
        options = df["complaint_id"].tolist()
        with st.form("update_status_form"):
            selected_id = st.selectbox("Select complaint", options, format_func=lambda x: f"{x} — {df.loc[df['complaint_id'] == x, 'title'].iloc[0]}")
            current_status = df.loc[df["complaint_id"] == selected_id, "status"].iloc[0]
            new_status = st.selectbox("New status", STATUSES, index=STATUSES.index(current_status))
            update = st.form_submit_button("Save status", type="primary")
        if update:
            if update_status(selected_id, new_status):
                st.success(f"{selected_id} updated to {new_status}.")
                st.rerun()
            else:
                st.error("Could not update the complaint. Please refresh and try again.")
    else:
        st.info("There are no complaints to update yet.")
    st.divider()
    st.subheader("Analytics")
    chart1, chart2 = st.columns(2)
    with chart1:
        st.pyplot(make_category_chart(df), use_container_width=True)
        plt.close("all")
    with chart2:
        st.pyplot(make_status_chart(df), use_container_width=True)
        plt.close("all")
    with st.expander("Download complaint data"):
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv_data, file_name="smart_campus_complaints.csv", mime="text/csv")
