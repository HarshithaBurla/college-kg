
import requests
import streamlit as st

# ==========================================================
# COLLEGE INFORMATION KNOWLEDGE GRAPH
# Frontend: Streamlit | Backend: FastAPI | Database: Neo4j
# ==========================================================

APP_TITLE = "College Information Knowledge Graph"
API_URL = "http://127.0.0.1:8000"
ASK_URL = f"{API_URL}/ask"
HEALTH_URL = f"{API_URL}/health"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------- SESSION STATE ---------------------

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

if "messages" not in st.session_state:
    st.session_state.messages = []


def navigate(page_name):
    st.session_state.page = page_name


def select_question(question):
    st.session_state.question_input = question
    st.session_state.page = "Ask a Question"


# --------------------------- CSS --------------------------

st.markdown(
    """
    <style>
    :root {
        --navy: #14263d;
        --navy-light: #203e60;
        --teal: #0f9d91;
        --teal-light: #e5f7f4;
        --background: #f4f7fb;
        --border: #e1e7ef;
        --text: #263548;
        --muted: #718096;
    }

    .stApp {
        background: var(--background);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1320px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.4rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }

    .brand-icon {
        width: 45px;
        height: 45px;
        border-radius: 12px;
        background: var(--navy);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 23px;
    }

    .brand-name {
        color: var(--navy);
        font-size: 16px;
        font-weight: 750;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 11px;
        margin-top: 4px;
    }

    .menu-label {
        color: #8290a2;
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 1.3px;
        margin: 25px 0 10px 5px;
    }

    /* Page headings */

    .eyebrow {
        color: var(--teal);
        text-transform: uppercase;
        font-weight: 750;
        font-size: 11px;
        letter-spacing: 1.8px;
        margin-bottom: 7px;
    }

    .page-heading {
        color: var(--navy);
        font-size: 30px;
        line-height: 1.3;
        font-weight: 780;
        margin-bottom: 8px;
    }

    .page-description {
        color: var(--muted);
        font-size: 14px;
        line-height: 1.7;
        margin-bottom: 22px;
    }

    h1, h2, h3, h4 {
        color: var(--navy) !important;
    }

    /* Dashboard banner */

    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(
            120deg, #14263d 0%, #1d4260 65%, #126e72 100%
        );
        border-radius: 17px;
        padding: 32px;
        margin-bottom: 25px;
    }

    .hero-label {
        color: #72e3d3;
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 1.7px;
        margin-bottom: 12px;
    }

    .hero-title {
        color: #ffffff;
        font-size: 29px;
        font-weight: 760;
        line-height: 1.3;
        margin-bottom: 12px;
    }

    .hero-description {
        color: #dce8f2;
        font-size: 14px;
        line-height: 1.8;
        max-width: 690px;
        margin-bottom: 18px;
    }

    .hero-tag {
        display: inline-block;
        color: #e8fffa;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 20px;
        padding: 7px 12px;
        font-size: 11px;
        margin: 0 5px 5px 0;
    }

    /* Metrics */

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 3px 12px rgba(25,45,70,0.025);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: 12px !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--navy) !important;
        font-size: 28px !important;
        font-weight: 750 !important;
    }

    /* Section headings */

    .section-title {
        color: var(--navy);
        font-size: 20px;
        font-weight: 750;
        margin: 25px 0 5px 0;
    }

    .section-description {
        color: var(--muted);
        font-size: 13px;
        margin-bottom: 15px;
    }

    /* Information cards */

    .quick-card {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 13px;
        padding: 18px;
        min-height: 125px;
        margin-bottom: 10px;
    }

    .quick-icon {
        font-size: 22px;
        margin-bottom: 10px;
    }

    .quick-title {
        color: var(--navy);
        font-size: 15px;
        font-weight: 750;
        margin-bottom: 6px;
    }

    .quick-description {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.65;
    }

    .process-card {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 17px;
        min-height: 112px;
    }

    .process-number {
        display: inline-flex;
        width: 29px;
        height: 29px;
        border-radius: 9px;
        background: var(--teal-light);
        color: #087b70;
        font-size: 13px;
        font-weight: 750;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px;
    }

    .process-title {
        color: var(--navy);
        font-size: 14px;
        font-weight: 750;
        margin-bottom: 5px;
    }

    .process-description {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.6;
    }

    /* Search panel */

    .workspace {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 21px;
        margin-bottom: 18px;
    }

    .workspace-heading {
        color: var(--navy);
        font-size: 17px;
        font-weight: 750;
        margin-bottom: 7px;
    }

    .workspace-description {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.7;
    }

    /* Buttons */

    .stButton > button {
        border-radius: 9px;
        min-height: 42px;
        font-weight: 600;
        border: 1px solid #dce4ee;
        background: #ffffff;
        color: var(--navy) !important;
    }

    .stButton > button p {
        color: var(--navy) !important;
    }

    .stButton > button:hover {
        border-color: var(--teal);
        background: #f0fbf9;
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button {
        background: var(--navy);
        color: #ffffff !important;
        border: 1px solid var(--navy);
        border-radius: 9px;
        min-height: 44px;
        font-weight: 650;
    }

    .stButton > button[kind="primary"] p,
    .stFormSubmitButton > button p {
        color: #ffffff !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button:hover {
        background: var(--navy-light);
        border-color: var(--navy-light);
    }

    /* Input fields */

    input, textarea {
        color: #263548 !important;
        background: #ffffff !important;
        -webkit-text-fill-color: #263548 !important;
    }

    input::placeholder, textarea::placeholder {
        color: #8290a2 !important;
        -webkit-text-fill-color: #8290a2 !important;
        opacity: 1 !important;
    }

    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div {
        background: #ffffff !important;
        border-color: #d6deea !important;
        border-radius: 9px !important;
    }

    /* Conversation and results */

    [data-testid="stChatMessage"] {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    [data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 10px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 9px;
        overflow: hidden;
    }

    .app-footer {
        margin-top: 32px;
        padding-top: 14px;
        border-top: 1px solid var(--border);
        color: #8591a1;
        font-size: 11px;
        display: flex;
        justify-content: space-between;
        gap: 10px;
        flex-wrap: wrap;
    }

    @media (max-width: 700px) {
        .hero {
            padding: 23px;
        }

        .hero-title {
            font-size: 24px;
        }

        .page-heading {
            font-size: 25px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------- BACKEND FUNCTIONS -----------------

def check_backend():
    for url in (HEALTH_URL, API_URL):
        try:
            response = requests.get(url, timeout=2)
            if response.ok:
                return True
        except requests.RequestException:
            continue

    return False


def ask_backend(question):
    response = requests.post(
        ASK_URL,
        json={"question": question},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def get_answer(data):
    answer = data.get("answer")

    if isinstance(answer, str) and answer.strip():
        return answer

    answers = data.get("answers", [])

    if isinstance(answers, str) and answers.strip():
        return answers

    if isinstance(answers, list) and answers:
        return "\n".join(str(item) for item in answers)

    rows = data.get("rows", [])

    if rows:
        return f"Retrieved {len(rows)} matching records."

    return data.get("message", "No answer was returned.")


def display_result(data):
    st.markdown("#### Answer")

    answer = data.get("answer")
    answers = data.get("answers", [])
    rows = data.get("rows", [])

    # List-based response from the existing API
    if isinstance(answers, list) and answers:
        for item in answers:
            st.markdown(f"- {item}")

    # Structured database rows
    elif isinstance(rows, list) and rows:
        if all(isinstance(row, dict) for row in rows):
            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )
        else:
            for item in rows:
                st.markdown(f"- {item}")

    # Text response from a language model or API
    elif isinstance(answer, str) and answer.strip():
        lines = [
            line.strip()
            for line in answer.splitlines()
            if line.strip()
        ]

        # Convert numbered or line-separated lists into bullets.
        if len(lines) > 1:
            for line in lines:
                cleaned = line.lstrip("•*- ").strip()
                st.markdown(f"- {cleaned}")
        else:
            st.markdown(answer)

    else:
        st.info("No results were returned.")

    if data.get("count") is not None:
        st.caption(f"Records found: {data['count']}")

    cypher = data.get("cypher")

    if isinstance(cypher, str) and cypher.strip():
        with st.expander("View generated Cypher query"):
            st.code(cypher, language="cypher")


def submit_question(question):
    question = question.strip()

    if not question:
        st.warning("Please enter a question first.")
        return

    with st.spinner("Searching the knowledge graph..."):
        try:
            data = ask_backend(question)

            st.session_state.messages.append({
                "role": "user",
                "content": question,
            })

            st.session_state.messages.append({
                "role": "assistant",
                "content": get_answer(data),
                "data": data,
            })

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to FastAPI. Start the backend "
                "on port 8000 and try again."
            )

        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")

        except requests.exceptions.HTTPError as exc:
            st.error(f"Backend error: {exc}")

            if exc.response is not None:
                st.code(exc.response.text[:1000])

        except (ValueError, requests.exceptions.RequestException) as exc:
            st.error(f"Could not complete the request: {exc}")


def page_header(label, title, description):
    st.markdown(
        f"""
        <div class="eyebrow">{label}</div>
        <div class="page-heading">{title}</div>
        <div class="page-description">{description}</div>
        """,
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        """
        <div class="app-footer">
            <span>College Information Knowledge Graph</span>
            <span>Academic Information System</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def quick_card(icon, title, description):
    st.markdown(
        f"""
        <div class="quick-card">
            <div class="quick-icon">{icon}</div>
            <div class="quick-title">{title}</div>
            <div class="quick-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------- SIDEBAR ----------------------

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">🎓</div>
            <div>
                <div class="brand-name">College KG</div>
                <div class="brand-subtitle">Academic Information System</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="menu-label">WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    st.button(
        "⌂   Dashboard",
        key="nav_home",
        use_container_width=True,
        on_click=navigate,
        args=("Home",),
    )

    st.button(
        "⌕   Ask a Question",
        key="nav_question",
        use_container_width=True,
        on_click=navigate,
        args=("Ask a Question",),
    )

    st.button(
        "▤   About Project",
        key="nav_about",
        use_container_width=True,
        on_click=navigate,
        args=("About",),
    )

    st.divider()

    st.markdown(
        '<div class="menu-label">SYSTEM STATUS</div>',
        unsafe_allow_html=True,
    )

    if check_backend():
        st.success("API service connected")
    else:
        st.warning("API service unavailable")

    st.caption("Backend: FastAPI")
    st.caption("Graph database: Neo4j")


# --------------------------- DASHBOARD --------------------

page = st.session_state.page

if page == "Home":
    page_header(
        "COLLEGE KNOWLEDGE SYSTEM",
        "Dashboard",
        "Explore academic information and relationships in one place.",
    )

    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">KNOWLEDGE GRAPH EXPLORER</div>
            <div class="hero-title">
                Discover information.<br>
                Understand connections.
            </div>
            <div class="hero-description">
                Explore courses, departments, faculty, students and
                academic programs through a connected college knowledge
                graph. Ask questions in plain English and inspect the
                information retrieved from the database.
            </div>
            <span class="hero-tag">Neo4j Graph Database</span>
            <span class="hero-tag">Natural Language Questions</span>
            <span class="hero-tag">Academic Data</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Knowledge Graph Overview</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Previously recorded project statistics</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Graph Nodes", "87")

    with col2:
        st.metric("Relationships", "115")

    with col3:
        st.metric("Courses", "66")

    st.markdown(
        '<div class="section-title">Explore Information</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Choose an area to start exploring.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        quick_card(
            "📚",
            "Courses and Subjects",
            "Find syllabus courses and academic subjects.",
        )

        st.button(
            "Explore Courses  →",
            key="home_courses",
            use_container_width=True,
            on_click=select_question,
            args=("List all courses available in the knowledge graph",),
        )

        quick_card(
            "🏢",
            "Departments",
            "Explore departments represented in the graph.",
        )

        st.button(
            "Explore Departments  →",
            key="home_departments",
            use_container_width=True,
            on_click=select_question,
            args=("List all departments",),
        )

    with right:
        quick_card(
            "👩‍🏫",
            "Faculty",
            "Find faculty members and related academic information.",
        )

        st.button(
            "Explore Faculty  →",
            key="home_faculty",
            use_container_width=True,
            on_click=select_question,
            args=("List all faculty members",),
        )

        quick_card(
            "🎓",
            "Academic Programs",
            "Explore programs and their course relationships.",
        )

        st.button(
            "Explore Programs  →",
            key="home_programs",
            use_container_width=True,
            on_click=select_question,
            args=("List all academic programs",),
        )

    st.markdown(
        '<div class="section-title">How the System Works</div>',
        unsafe_allow_html=True,
    )

    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown(
            """
            <div class="process-card">
                <div class="process-number">01</div>
                <div class="process-title">Ask</div>
                <div class="process-description">
                    Enter a question about college information.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            """
            <div class="process-card">
                <div class="process-number">02</div>
                <div class="process-title">Retrieve</div>
                <div class="process-description">
                    The backend retrieves matching graph records.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p3:
        st.markdown(
            """
            <div class="process-card">
                <div class="process-number">03</div>
                <div class="process-title">Explore</div>
                <div class="process-description">
                    Review the answer and available database results.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    footer()


# ------------------------ ASK A QUESTION ------------------

elif page == "Ask a Question":
    page_header(
        "KNOWLEDGE GRAPH SEARCH",
        "Ask a Question",
        "Ask about college information using everyday language.",
    )

    st.markdown(
        """
        <div class="workspace">
            <div class="workspace-heading">
                Search the college knowledge graph
            </div>
            <div class="workspace-description">
                Ask about courses, departments, faculty, students,
                programs or research areas. Results depend on the
                information stored in the database.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Example question")

    st.button(
        "📚  List all courses available in the knowledge graph",
        key="example_courses",
        use_container_width=True,
        on_click=select_question,
        args=("List all courses available in the knowledge graph",),
    )

    st.caption(
        "This is only an example. You can type any question in the box below."
    )

    with st.form("question_form", clear_on_submit=False):
        question = st.text_input(
            "Your question",
            key="question_input",
            placeholder="Type your own question here...",
        )

        submitted = st.form_submit_button(
            "Search Knowledge Graph  →",
            use_container_width=True,
        )

    if submitted:
        submit_question(question)

    st.markdown(
        '<div class="section-title">Results and Conversation</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        st.info(
            "Your search results will appear here after you submit a question."
        )
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    data = message.get("data")

                    if isinstance(data, dict):
                        display_result(data)
                    else:
                        st.markdown(message["content"])

        if st.button("Clear conversation", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

    footer()


# ----------------------------- ABOUT ----------------------

elif page == "About":
    page_header(
        "PROJECT INFORMATION",
        "About the Project",
        "An academic information system built around connected data.",
    )

    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">PROJECT OVERVIEW</div>
            <div class="hero-title">
                College Information Knowledge Graph
            </div>
            <div class="hero-description">
                The project represents college information as entities
                and relationships in a graph database. The web interface
                sends questions to the backend, which retrieves relevant
                information from the graph.
            </div>
            <span class="hero-tag">Knowledge Representation</span>
            <span class="hero-tag">Graph Queries</span>
            <span class="hero-tag">Information Retrieval</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Technology Stack")

    st.table(
        [
            {
                "Technology": "Python",
                "Purpose": "Application logic and data processing",
            },
            {
                "Technology": "Streamlit",
                "Purpose": "Web interface",
            },
            {
                "Technology": "FastAPI",
                "Purpose": "Backend API",
            },
            {
                "Technology": "Neo4j",
                "Purpose": "Graph storage and relationships",
            },
            {
                "Technology": "Gemini",
                "Purpose": "Optional natural-language processing",
            },
        ]
    )

    st.markdown("### Information Categories")

    left, right = st.columns(2)

    with left:
        st.markdown(
            """
            - Academic courses and subjects
            - Departments
            - Faculty members
            """
        )

    with right:
        st.markdown(
            """
            - Students
            - Academic programs
            - Research areas
            """
        )

    st.info(
        "Dashboard totals are previously recorded values, not live "
        "database counts."
    )

    footer()
