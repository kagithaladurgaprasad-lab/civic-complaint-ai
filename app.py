
import os
import requests
import pandas as pd
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

API_URL = "https://civic-complaint-ai-xm2y.onrender.com"

st.set_page_config(
    page_title="Civic Complaint AI",
    page_icon="🏙️",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def logout():
    st.session_state.token = None
    st.session_state.logged_in = False
    st.rerun()


def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def handle_auth_error(status_code):
    if status_code == 401:
        st.error("🔐 Session expired. Please login again.")
        logout()
        return True

    return False


def show_duplicate_result(duplicate):
    st.subheader("🔍 Duplicate Detection")

    decision = duplicate.get("decision", "UNKNOWN")

    if decision == "DUPLICATE":
        st.error("🔴 DUPLICATE")

    elif decision == "POSSIBLY_RELATED":
        st.warning("🟡 POSSIBLY RELATED")

    else:
        st.success("🟢 NEW COMPLAINT")

    best_match = duplicate.get("best_match")

    if best_match:

        st.write("### Best Matching Historical Complaint")

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                f"**Complaint ID:** "
                f"{best_match.get('complaint_id', 'Unknown')}"
            )

            st.write(
                f"**Title:** "
                f"{best_match.get('title', 'Unknown')}"
            )

            st.write(
                f"**Category:** "
                f"{best_match.get('category', 'Unknown')}"
            )

        with col2:
            st.write(
                f"**Text Similarity:** "
                f"{best_match.get('text_score', 'Unknown')}"
            )

            st.write(
                f"**Location Distance:** "
                f"{best_match.get('distance_meters', 'Unknown')} meters"
            )

            st.write(
                f"**Final Score:** "
                f"{best_match.get('final_score', 'Unknown')}"
            )


def show_sla(sla):
    st.subheader("📜 Official Municipal SLA")

    if not sla:
        st.info(
            "No relevant official municipal SLA was found."
        )
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write(
            f"**Service:** {sla.get('service', 'Unknown')}"
        )

        st.write(
            f"**SLA:** {sla.get('sla_days', 'Unknown')} days"
        )

    with col2:
        st.write(
            f"**Department:** "
            f"{sla.get('department', 'Unknown')}"
        )

        st.write(
            f"**Source:** {sla.get('source', 'Unknown')}"
        )

    if sla.get("source_id"):
        st.caption(
            f"Source ID: {sla.get('source_id')}"
        )


def show_image(image_path, caption="Complaint Image"):
    if not image_path:
        st.info("No complaint image available.")
        return

    if os.path.exists(image_path):
        st.image(
            image_path,
            caption=caption,
            width=450
        )
    else:
        st.warning(
            "Complaint image file could not be found."
        )


def show_visual_evidence(duplicate):
    visual_evidence = duplicate.get(
        "visual_evidence",
        []
    )

    if not visual_evidence:
        return

    st.subheader("🖼️ Visual Evidence")

    for i, evidence in enumerate(
        visual_evidence,
        start=1
    ):

        with st.expander(
            f"Visual Match {i}"
        ):

            st.write(
                f"**Image ID:** "
                f"{evidence.get('image_id', 'Unknown')}"
            )

            st.write(
                f"**Image Similarity:** "
                f"{evidence.get('image_similarity', 'Unknown')}"
            )

            st.write(
                f"**Category:** "
                f"{evidence.get('category', 'Unknown')}"
            )

            st.write(
                f"**Source:** "
                f"{evidence.get('source', 'Unknown')}"
            )


def show_complaint_summary(complaint):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🏷️ Category",
            complaint.get(
                "category",
                "Unknown"
            )
        )

    with col2:
        st.metric(
            "🏢 Department",
            complaint.get(
                "department",
                "Unknown"
            )
        )

    with col3:
        st.metric(
            "🚨 Urgency",
            complaint.get(
                "urgency",
                "Unknown"
            )
        )


def show_status(status):
    if status == "Duplicate":
        st.warning(f"🔴 Status: {status}")

    elif status == "Resolved":
        st.success(f"🟢 Status: {status}")

    elif status == "In Progress":
        st.info(f"🔵 Status: {status}")

    else:
        st.write(f"**Status:** {status}")


# ============================================================
# LOGIN / REGISTER PAGE
# ============================================================

if not st.session_state.logged_in:

    st.title("🏙️ Civic Complaint AI")

    st.caption(
        "AI-powered municipal complaint classification, "
        "duplicate detection and official SLA retrieval"
    )

    login_tab, register_tab = st.tabs(
        ["🔐 Login", "📝 Register"]
    )

    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.subheader("Login")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            type="primary"
        ):

            if not email or not password:

                st.error(
                    "Please enter email and password."
                )

            else:

                try:

                    response = requests.post(
                        f"{API_URL}/login",
                        data={
                            "username": email.strip(),
                            "password": password
                        },
                        timeout=30
                    )

                    if response.status_code == 200:

                        result = response.json()

                        st.session_state.token = (
                            result["access_token"]
                        )

                        st.session_state.logged_in = True

                        st.success(
                            "Login successful!"
                        )

                        st.rerun()

                    else:

                        try:
                            message = response.json().get(
                                "detail",
                                "Login failed"
                            )
                        except Exception:
                            message = response.text

                        st.error(
                            f"❌ {message}"
                        )

                except requests.exceptions.ConnectionError as e:

                    st.error(
                        "❌ Cannot connect to FastAPI."
                    )

                    st.code(
                        str(e),
                        language="text"
                    )

                    st.info(
                        f"FastAPI URL being used: {API_URL}"
                    )

                except requests.exceptions.Timeout as e:

                    st.error(
                        "⏳ FastAPI request timed out."
                    )

                    st.code(
                        str(e),
                        language="text"
                    )

                except Exception as e:

                    st.error(
                        f"❌ Error: {str(e)}"
                    )

    # ========================================================
    # REGISTER
    # ========================================================

    with register_tab:

        st.subheader("Create Account")

        name = st.text_input(
            "Name",
            key="register_name"
        )

        email = st.text_input(
            "Email",
            key="register_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        if st.button("Register"):

            if not name or not email or not password:

                st.error(
                    "Please fill all fields."
                )

            else:

                try:

                    response = requests.post(
                        f"{API_URL}/register",
                        json={
                            "name": name,
                            "email": email,
                            "password": password
                        },
                        timeout=30
                    )

                    if response.status_code in [200, 201]:

                        st.success(
                            "✅ Registration successful. "
                            "Now login."
                        )

                    else:

                        try:
                            message = response.json().get(
                                "detail",
                                "Registration failed"
                            )
                        except Exception:
                            message = response.text

                        st.error(
                            f"❌ {message}"
                        )

                except requests.exceptions.ConnectionError as e:

                    st.error(
                        "❌ Cannot connect to FastAPI."
                    )

                    st.code(
                        str(e),
                        language="text"
                    )

                    st.info(
                        f"FastAPI URL being used: {API_URL}"
                    )

                except requests.exceptions.Timeout as e:

                    st.error(
                        "⏳ FastAPI request timed out."
                    )

                    st.code(
                        str(e),
                        language="text"
                    )

                except Exception as e:

                    st.error(
                        f"❌ Error: {str(e)}"
                    )

    st.stop()


# ============================================================
# LOGGED-IN APPLICATION
# ============================================================

st.title("🏙️ Civic Complaint AI")

st.caption(
    "AI-powered municipal complaint classification, "
    "duplicate detection and official SLA retrieval"
)


# ============================================================
# TOP BAR
# ============================================================

col1, col2 = st.columns([5, 1])

with col1:
    st.success("✅ Logged in")

with col2:
    if st.button("Logout"):
        logout()


headers = get_headers()

st.divider()


# ============================================================
# TABS
# ============================================================

submit_tab, history_tab, admin_tab = st.tabs(
    [
        "📝 Submit Complaint",
        "📋 My Complaints",
        "🏢 Admin Dashboard"
    ]
)


# ============================================================
# SUBMIT COMPLAINT
# ============================================================

with submit_tab:

    st.header("📝 Submit Civic Complaint")

    title = st.text_input(
        "Complaint Title",
        placeholder="Example: Deep pothole near railway station"
    )

    description = st.text_area(
        "Complaint Description",
        placeholder="Describe the problem in detail...",
        height=150
    )

    col1, col2 = st.columns(2)

    with col1:
        latitude = st.number_input(
            "Latitude",
            format="%.6f"
        )

    with col2:
        longitude = st.number_input(
            "Longitude",
            format="%.6f"
        )

    image = st.file_uploader(
        "📷 Upload Complaint Image",
        type=["jpg", "jpeg", "png"]
    )

    if image:

        st.image(
            image,
            caption="Uploaded Complaint Image",
            width=400
        )

    if st.button(
        "🚀 Submit Complaint",
        type="primary"
    ):

        if not title.strip():

            st.error(
                "Please enter complaint title."
            )

        elif not description.strip():

            st.error(
                "Please enter complaint description."
            )

        elif image is None:

            st.error(
                "Please upload complaint image."
            )

        else:

            files = {
                "image": (
                    image.name,
                    image.getvalue(),
                    image.type
                )
            }

            data = {
                "title": title,
                "description": description,
                "latitude": latitude,
                "longitude": longitude
            }

            try:

                with st.spinner(
                    "🔄 AI is analyzing the complaint..."
                ):

                    response = requests.post(
                        f"{API_URL}/complaints",
                        data=data,
                        files=files,
                        headers=headers,
                        timeout=180
                    )

                if handle_auth_error(
                    response.status_code
                ):
                    st.stop()

                if response.status_code == 200:

                    result = response.json()

                    complaint = result.get(
                        "complaint",
                        {}
                    )

                    duplicate = result.get(
                        "duplicate",
                        {}
                    )

                    sla = result.get(
                        "municipal_sla"
                    )

                    ai_analysis = result.get(
                        "ai_analysis",
                        ""
                    )

                    st.success(
                        "✅ Complaint submitted successfully!"
                    )

                    st.divider()

                    st.header(
                        "📋 Complaint Analysis"
                    )

                    show_complaint_summary(
                        complaint
                    )

                    st.subheader(
                        "📌 Complaint Status"
                    )

                    show_status(
                        complaint.get(
                            "status",
                            "Unknown"
                        )
                    )

                    show_duplicate_result(
                        duplicate
                    )

                    show_sla(
                        sla
                    )

                    st.subheader(
                        "🤖 AI Analysis"
                    )

                    if ai_analysis:
                        st.markdown(
                            ai_analysis
                        )
                    else:
                        st.info(
                            "AI analysis not available."
                        )

                    show_visual_evidence(
                        duplicate
                    )

                    st.subheader(
                        "📍 Complaint Location"
                    )

                    st.write(
                        f"**Latitude:** "
                        f"{complaint.get('latitude', latitude)}"
                    )

                    st.write(
                        f"**Longitude:** "
                        f"{complaint.get('longitude', longitude)}"
                    )

                else:

                    st.error(
                        f"❌ API Error: "
                        f"{response.status_code}"
                    )

                    try:
                        st.json(
                            response.json()
                        )
                    except Exception:
                        st.code(
                            response.text
                        )

            except requests.exceptions.ConnectionError as e:

                st.error(
                    "❌ Cannot connect to FastAPI."
                )

                st.code(
                    str(e),
                    language="text"
                )

            except requests.exceptions.Timeout as e:

                st.error(
                    "⏳ Request timed out."
                )

                st.code(
                    str(e),
                    language="text"
                )

            except Exception as e:

                st.error(
                    f"❌ Error: {str(e)}"
                )


# ============================================================
# MY COMPLAINTS
# ============================================================

with history_tab:

    st.header("📋 My Complaints")

    if st.button(
        "🔄 Refresh My Complaints"
    ):

        st.rerun()

    try:

        response = requests.get(
            f"{API_URL}/my-complaints",
            headers=headers,
            timeout=30
        )

        if handle_auth_error(
            response.status_code
        ):
            st.stop()

        if response.status_code == 200:

            complaints = response.json()

            if not complaints:

                st.info(
                    "You have not submitted any complaints yet."
                )

            else:

                st.success(
                    f"Total Complaints: {len(complaints)}"
                )

                for complaint in complaints:

                    complaint_id = complaint.get(
                        "id"
                    )

                    title = complaint.get(
                        "title",
                        "Untitled"
                    )

                    with st.expander(
                        f"#{complaint_id} — {title}"
                    ):

                        show_complaint_summary(
                            complaint
                        )

                        show_status(
                            complaint.get(
                                "status",
                                "Unknown"
                            )
                        )

                        st.write(
                            f"**Description:** "
                            f"{complaint.get('description', '')}"
                        )

                        st.write(
                            f"**Latitude:** "
                            f"{complaint.get('latitude', 'Unknown')}"
                        )

                        st.write(
                            f"**Longitude:** "
                            f"{complaint.get('longitude', 'Unknown')}"
                        )

                        st.subheader(
                            "🖼️ Complaint Image"
                        )

                        show_image(
                            complaint.get(
                                "image_path"
                            )
                        )

        else:

            st.error(
                f"❌ Error: {response.status_code}"
            )

            try:
                st.json(
                    response.json()
                )
            except Exception:
                st.code(
                    response.text
                )

    except requests.exceptions.ConnectionError as e:

        st.error(
            "❌ Cannot connect to FastAPI."
        )

        st.code(
            str(e),
            language="text"
        )

    except requests.exceptions.Timeout as e:

        st.error(
            "⏳ Request timed out."
        )

        st.code(
            str(e),
            language="text"
        )

    except Exception as e:

        st.error(
            f"❌ Error: {str(e)}"
        )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

with admin_tab:

    st.header("🏢 Admin Dashboard")

    if st.button(
        "🔄 Refresh Admin Dashboard"
    ):

        st.rerun()

    try:

        response = requests.get(
            f"{API_URL}/admin/complaints",
            headers=headers,
            timeout=30
        )

        if response.status_code == 401:

            st.error(
                "🔐 Session expired. Please login again."
            )

            logout()

        elif response.status_code == 403:

            st.warning(
                "🚫 Admin access required."
            )

            st.info(
                "Login with an account whose role is 'admin'."
            )

        elif response.status_code != 200:

            st.error(
                f"❌ Admin API Error: "
                f"{response.status_code}"
            )

            try:
                st.json(
                    response.json()
                )
            except Exception:
                st.code(
                    response.text
                )

        else:

            complaints = response.json()

            if not complaints:

                st.info(
                    "No complaints available."
                )

            else:

                df = pd.DataFrame(
                    complaints
                )

                # ====================================================
                # METRICS
                # ====================================================

                total = len(df)

                high = len(
                    df[df["urgency"] == "High"]
                )

                duplicates = len(
                    df[df["status"] == "Duplicate"]
                )

                resolved = len(
                    df[df["status"] == "Resolved"]
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "📊 Total",
                        total
                    )

                with col2:
                    st.metric(
                        "🔴 High Urgency",
                        high
                    )

                with col3:
                    st.metric(
                        "♻️ Duplicates",
                        duplicates
                    )

                with col4:
                    st.metric(
                        "🟢 Resolved",
                        resolved
                    )

                st.divider()

                # ====================================================
                # CHARTS
                # ====================================================

                st.subheader(
                    "📊 Complaints by Category"
                )

                st.bar_chart(
                    df["category"].value_counts()
                )

                st.subheader(
                    "🏢 Complaints by Department"
                )

                st.bar_chart(
                    df["department"].value_counts()
                )

                st.divider()

                # ====================================================
                # FILTERS
                # ====================================================

                st.subheader(
                    "🔎 Filters"
                )

                col1, col2, col3, col4 = st.columns(4)

                categories = sorted(
                    df["category"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                departments = sorted(
                    df["department"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                statuses = sorted(
                    df["status"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                urgencies = sorted(
                    df["urgency"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                with col1:
                    selected_category = st.selectbox(
                        "Category",
                        ["All"] + categories
                    )

                with col2:
                    selected_department = st.selectbox(
                        "Department",
                        ["All"] + departments
                    )

                with col3:
                    selected_status = st.selectbox(
                        "Status",
                        ["All"] + statuses
                    )

                with col4:
                    selected_urgency = st.selectbox(
                        "Urgency",
                        ["All"] + urgencies
                    )

                filtered = df.copy()

                if selected_category != "All":

                    filtered = filtered[
                        filtered["category"]
                        == selected_category
                    ]

                if selected_department != "All":

                    filtered = filtered[
                        filtered["department"]
                        == selected_department
                    ]

                if selected_status != "All":

                    filtered = filtered[
                        filtered["status"]
                        == selected_status
                    ]

                if selected_urgency != "All":

                    filtered = filtered[
                        filtered["urgency"]
                        == selected_urgency
                    ]

                st.write(
                    f"Showing **{len(filtered)}** complaints"
                )

                # ====================================================
                # TABLE
                # ====================================================

                columns = [
                    "id",
                    "title",
                    "category",
                    "department",
                    "urgency",
                    "status",
                    "user_id"
                ]

                columns = [
                    col
                    for col in columns
                    if col in filtered.columns
                ]

                st.dataframe(
                    filtered[columns],
                    use_container_width=True,
                    hide_index=True
                )

                st.divider()

                # ====================================================
                # COMPLAINT REVIEW
                # ====================================================

                st.subheader(
                    "📋 Complaint Review"
                )

                for complaint in complaints:

                    complaint_id = complaint.get(
                        "id"
                    )

                    # Apply same filters
                    if (
                        selected_category != "All"
                        and complaint.get("category")
                        != selected_category
                    ):
                        continue

                    if (
                        selected_department != "All"
                        and complaint.get("department")
                        != selected_department
                    ):
                        continue

                    if (
                        selected_status != "All"
                        and complaint.get("status")
                        != selected_status
                    ):
                        continue

                    if (
                        selected_urgency != "All"
                        and complaint.get("urgency")
                        != selected_urgency
                    ):
                        continue

                    with st.expander(
                        f"#{complaint_id} — "
                        f"{complaint.get('title', 'Untitled')}"
                    ):

                        show_complaint_summary(
                            complaint
                        )

                        show_status(
                            complaint.get(
                                "status",
                                "Unknown"
                            )
                        )

                        st.write(
                            f"**Description:** "
                            f"{complaint.get('description', '')}"
                        )

                        st.write(
                            f"**User ID:** "
                            f"{complaint.get('user_id', 'Unknown')}"
                        )

                        st.subheader(
                            "📍 Location"
                        )

                        st.write(
                            f"Latitude: "
                            f"{complaint.get('latitude', 'Unknown')}"
                        )

                        st.write(
                            f"Longitude: "
                            f"{complaint.get('longitude', 'Unknown')}"
                        )

                        st.subheader(
                            "🖼️ Complaint Image"
                        )

                        show_image(
                            complaint.get(
                                "image_path"
                            )
                        )

                        # ================================================
                        # FULL DETAILS
                        # ================================================

                        if st.button(
                            "🔎 View Full AI/RAG Details",
                            key=f"details_{complaint_id}"
                        ):

                            try:

                                with st.spinner(
                                    "Loading AI/RAG analysis..."
                                ):

                                    detail_response = requests.get(
                                        f"{API_URL}/admin/complaints/"
                                        f"{complaint_id}/details",
                                        headers=headers,
                                        timeout=180
                                    )

                                if detail_response.status_code == 200:

                                    detail = (
                                        detail_response.json()
                                    )

                                    detail_complaint = (
                                        detail.get(
                                            "complaint",
                                            {}
                                        )
                                    )

                                    detail_duplicate = (
                                        detail.get(
                                            "duplicate",
                                            {}
                                        )
                                    )

                                    detail_sla = (
                                        detail.get(
                                            "municipal_sla"
                                        )
                                    )

                                    detail_ai = (
                                        detail.get(
                                            "ai_analysis",
                                            ""
                                        )
                                    )

                                    st.subheader(
                                        "🤖 AI Analysis"
                                    )

                                    if detail_ai:
                                        st.markdown(
                                            detail_ai
                                        )
                                    else:
                                        st.info(
                                            "AI analysis unavailable."
                                        )

                                    show_duplicate_result(
                                        detail_duplicate
                                    )

                                    show_sla(
                                        detail_sla
                                    )

                                    show_visual_evidence(
                                        detail_duplicate
                                    )

                                elif detail_response.status_code == 401:

                                    logout()

                                elif detail_response.status_code == 403:

                                    st.error(
                                        "🚫 Admin access required."
                                    )

                                else:

                                    st.error(
                                        f"❌ Error: "
                                        f"{detail_response.status_code}"
                                    )

                                    try:
                                        st.json(
                                            detail_response.json()
                                        )
                                    except Exception:
                                        st.code(
                                            detail_response.text
                                        )

                            except requests.exceptions.Timeout as e:

                                st.error(
                                    "⏳ AI/RAG request timed out."
                                )

                                st.code(
                                    str(e),
                                    language="text"
                                )

                            except requests.exceptions.ConnectionError as e:

                                st.error(
                                    "❌ Cannot connect to FastAPI."
                                )

                                st.code(
                                    str(e),
                                    language="text"
                                )

                            except Exception as e:

                                st.error(
                                    f"❌ Error: {str(e)}"
                                )

                        # ================================================
                        # UPDATE STATUS
                        # ================================================

                        st.subheader(
                            "🔄 Update Status"
                        )

                        allowed_statuses = [
                            "Submitted",
                            "Duplicate",
                            "In Progress",
                            "Resolved",
                            "Rejected"
                        ]

                        current_status = complaint.get(
                            "status",
                            "Submitted"
                        )

                        selected_status_value = st.selectbox(
                            "New Status",
                            allowed_statuses,
                            index=(
                                allowed_statuses.index(
                                    current_status
                                )
                                if current_status
                                in allowed_statuses
                                else 0
                            ),
                            key=f"new_status_{complaint_id}"
                        )

                        if st.button(
                            "💾 Update Status",
                            key=f"update_{complaint_id}"
                        ):

                            try:

                                update_response = requests.put(
                                    f"{API_URL}/admin/complaints/"
                                    f"{complaint_id}/status",
                                    params={
                                        "status":
                                        selected_status_value
                                    },
                                    headers=headers,
                                    timeout=30
                                )

                                if update_response.status_code == 200:

                                    st.success(
                                        "✅ Status updated successfully."
                                    )

                                    st.rerun()

                                elif update_response.status_code == 401:

                                    logout()

                                elif update_response.status_code == 403:

                                    st.error(
                                        "🚫 Admin access required."
                                    )

                                else:

                                    st.error(
                                        f"❌ Update failed: "
                                        f"{update_response.status_code}"
                                    )

                                    try:
                                        st.json(
                                            update_response.json()
                                        )
                                    except Exception:
                                        st.code(
                                            update_response.text
                                        )

                            except requests.exceptions.ConnectionError as e:

                                st.error(
                                    "❌ Cannot connect to FastAPI."
                                )

                                st.code(
                                    str(e),
                                    language="text"
                                )

                            except requests.exceptions.Timeout as e:

                                st.error(
                                    "⏳ Request timed out."
                                )

                                st.code(
                                    str(e),
                                    language="text"
                                )

                            except Exception as e:

                                st.error(
                                    f"❌ Error: {str(e)}"
                                )

    except requests.exceptions.ConnectionError as e:

        st.error(
            "❌ Cannot connect to FastAPI."
        )

        st.code(
            str(e),
            language="text"
        )

        st.info(
            f"FastAPI URL being used: {API_URL}"
        )

    except requests.exceptions.Timeout as e:

        st.error(
            "⏳ Request timed out."
        )

        st.code(
            str(e),
            language="text"
        )

    except Exception as e:

        st.error(
            f"❌ Error: {str(e)}"
        )

