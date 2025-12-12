import os
from pathlib import Path

import streamlit as st
import pandas as pd

from agents import (
    underage_risk_agent,
    content_risk_agent,
    interaction_risk_agent,
    policy_violation_agent,
    report_generator_agent,
)

# THEME & HEADER CSS 
THEME_CSS = """
<style>

/* -------------------------------------------------- */
/* GLOBAL LAYOUT                                      */
/* -------------------------------------------------- */

body, .main {
    background-color: #F5F8FA !important;
    color: #0F1419 !important;
    font-family: "Inter", "Segoe UI", Roboto, sans-serif;
}

/* Reduce extra whitespace near the top */
.block-container {
    padding-top: 20px !important;
    padding-left: 40px !important;
    padding-right: 40px !important;
}

/* -------------------------------------------------- */
/* SIDEBAR                                            */
/* -------------------------------------------------- */

[data-testid="stSidebar"] {
    background-color: #E3F6FF !important;   /* light social blue */
    border-right: 1px solid #D0E7FF;
    padding-top: 20px !important;
}

[data-testid="stSidebar"] .stSelectbox>div>div {
    background: #FFFFFF;
    border-radius: 10px;
}

/* Sidebar cards */
[data-testid="stSidebar"] .block-container div {
    border-radius: 12px !important;
}

/* -------------------------------------------------- */
/* HEADER CARD                                        */
/* -------------------------------------------------- */

.header-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 22px 30px;
    margin: 0 0 26px 0;
    border: 1px solid #D0E7FF;
    box-shadow: 0 6px 18px rgba(13,37,63,0.06);
}

.header-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #0F1419;
    margin-bottom: 6px;
}

.header-subtitle {
    color: #475569;
    font-size: 1.05rem;
}

/* -------------------------------------------------- */
/* CONTENT CARDS (User Profile, Sections, Blocks)     */
/* -------------------------------------------------- */

/* Style only major content cards, not layout wrappers */
div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div {
    border: 1px solid #D0E7FF !important;
    border-radius: 14px !important;
    background: #FFFFFF !important;
    padding: 16px !important;
    margin-bottom: 20px !important;
}

/* Section titles */
h2, h3 {
    color: #0F1419;
    font-weight: 700 !important;
}

/* -------------------------------------------------- */
/* TABLES                                             */
/* -------------------------------------------------- */

.stDataFrame table {
    border-collapse: separate !important;
    border-spacing: 0 6px !important;
}

.stDataFrame thead th {
    background: #F0F7FF !important;
    color: #0F1419 !important;
    font-weight: 700 !important;
    border-bottom: 1px solid #D0E7FF !important;
}

.stDataFrame tbody tr td {
    background: #FFFFFF !important;
    border: 1px solid #D0E7FF !important;
}

/* Zebra light-blue stripes (optional—looks modern) */
.stDataFrame tbody tr:nth-child(even) td {
    background: #EAF4FF !important;
}

/* -------------------------------------------------- */
/* BUTTONS                                            */
/* -------------------------------------------------- */

.stButton>button, .stDownloadButton>button {
    background-color: #1DA1F2 !important;
    color: white !important;
    border: none !important;
    padding: 10px 16px !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(29,161,242,0.16);
    transition: 0.2s ease;
}

.stButton>button:hover, .stDownloadButton>button:hover {
    background-color: #0C8BD9 !important;
    box-shadow: 0 6px 14px rgba(29,161,242,0.25);
}

/* -------------------------------------------------- */
/* EXPANDERS (Policy section)                         */
/* -------------------------------------------------- */

details {
    border: 1px solid #D0E7FF !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
    padding: 8px !important;
}

.streamlit-expanderHeader {
    font-weight: 700;
    color: #0F1419;
}

/* -------------------------------------------------- */
/* CHARTS                                             */
/* -------------------------------------------------- */

.stBarChart, .stPlotlyChart, .stAltairChart {
    background: #FFFFFF !important;
    border: 1px solid #D0E7FF !important;
    border-radius: 14px !important;
    padding: 14px !important;
}

/* -------------------------------------------------- */
/* RESPONSIVE ADJUSTMENTS                             */
/* -------------------------------------------------- */

@media (max-width: 1000px) {
    .header-title { font-size: 1.8rem !important; }
}

</style>
"""



 
 
# Project branding / constants
PROJECT_NAME = "SafeScroll"
PROJECT_SLUG = "safescroll"
PROJECT_TAGLINE = "Making your social feed safer — one scroll at a time."

POLICY_PATH = Path("policies") / "safety_policies.txt"


def load_data():
    data_dir = Path("data")
    users = pd.read_csv(data_dir / "users.csv")
    posts = pd.read_csv(data_dir / "posts.csv")
    interactions = pd.read_csv(data_dir / "interactions.csv")
    return users, posts, interactions


def load_policies() -> str:
    if POLICY_PATH.exists():
        return POLICY_PATH.read_text(encoding="utf-8")
    return "No policies found."


def main():
    # Inject CSS theme
    st.markdown(THEME_CSS, unsafe_allow_html=True)

    st.set_page_config(
        page_title=PROJECT_NAME,
        page_icon="🛡️",
        layout="wide",
    )

    # Polished header block  
    st.markdown(
        f"""
        <div class="header-card">
            <div class="header-title">🛡️ {PROJECT_NAME} — AI-Powered Social Media Safety Auditor</div>
            <div class="header-subtitle">{PROJECT_TAGLINE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        """
This tool simulates an **internal Trust & Safety system** for a social platform.

It uses multi-agent GenAI to:
- Analyze user posts and DMs
- Detect underage risk, bullying, self-harm, grooming patterns, and substance abuse
- Map findings to company safety policies
- Generate a human-readable **Safety Report** with a final recommended action

All data here is synthetic and for research/demo purposes only.
"""
    )

    users, posts, interactions = load_data()
    policies_text = load_policies()

    st.sidebar.header("User Selection")
    selected_user_id = st.sidebar.selectbox(
        "Choose a user to audit", options=users["user_id"].tolist()
    )

    st.sidebar.markdown("---")
    st.sidebar.write("Users table preview:")
    st.sidebar.dataframe(users.head(), height=200)

    user_row = users[users["user_id"] == selected_user_id].iloc[0].to_dict()
    user_posts_df = posts[posts["user_id"] == selected_user_id]
    user_interactions_df = interactions[
        (interactions["from_user"] == selected_user_id)
        | (interactions["to_user"] == selected_user_id)
    ]

    st.markdown("## 👤 User Profile")
    col_profile, col_posts = st.columns([1, 2])

    with col_profile:
        st.write("**User ID:**", user_row["user_id"])
        st.write("**Declared age:**", int(user_row["age"]))
        st.write("**Account type:**", user_row["account_type"])
         

    with col_posts:
        st.write("**Recent Posts (sample):**")
        st.dataframe(
            user_posts_df[["post_id", "text", "timestamp"]].head(10),
            height=250,
        )

    st.markdown("## 📩 Interactions (DMs)")
    if not user_interactions_df.empty:
        st.dataframe(user_interactions_df, height=200)
    else:
        st.write("_No interactions found for this user in the sample data._")

    st.markdown("---")
    st.markdown("## 🚨 Run Safety Audit")

    # Demo mode: if no OPENAI_API_KEY is set, we show mocked results for screenshots
    DEMO_MODE = not bool(os.getenv("OPENAI_API_KEY"))

    if DEMO_MODE:
        st.info("Running in DEMO MODE — no OpenAI key detected. Showing mock results only.")

    if st.button("Run Multi-Agent Safety Audit"):
        # If in demo mode, use canned results (no external calls)
        if DEMO_MODE:
            # Mock outputs for UI/screenshot purposes
            underage_res = {
                "is_minor_suspected": True,
                "underage_misrepresentation_risk": 72,
                "reason": "User posts indicate teenage language patterns and age-related topics."
            }

            content_res = {
                "per_post": [
                    {
                        "post_id": user_posts_df.iloc[0]["post_id"] if not user_posts_df.empty else "p1",
                        "text": user_posts_df.iloc[0]["text"] if not user_posts_df.empty else "",
                        "bullying_risk": "none",
                        "self_harm_risk": "low",
                        "sexual_exploitation_risk": "none",
                        "substance_abuse_risk": "low",
                        "notes": "Some references to substance use and low-level self-harm language."
                    }
                ],
                "overall": {
                    "bullying_risk": "low",
                    "self_harm_risk": "low",
                    "sexual_exploitation_risk": "none",
                    "substance_abuse_risk": "low",
                    "summary": "Low-to-moderate concerns primarily around substance references and self-harm wording."
                }
            }

            interaction_res = {
                "grooming_risk": "medium",
                "evidence": [
                    {
                        "interaction_id": user_interactions_df.iloc[0]["interaction_id"] if not user_interactions_df.empty else "i1",
                        "text_snippet": user_interactions_df.iloc[0]["text"] if not user_interactions_df.empty else "Don't tell anyone we talk here.",
                        "comment": "Secrecy and older-user behavior detected."
                    }
                ],
                "summary": "Some age-imbalanced conversations and secrecy cues were observed."
            }

            policy_res = {
                "violated_sections": ["Underage Safety", "Substance Use Policy"],
                "overall_severity": "medium",
                "recommended_action": "monitor",
                "explanation": "Behavior matches medium-risk guidelines; recommend monitoring and a warning if escalates."
            }

            report_res = {
                "risk_title": f"{PROJECT_NAME} Automated Safety Report",
                "overall_risk_score": 62,
                "risk_summary": "Moderate concerns detected. Monitoring recommended.",
                "markdown_report": (
                    "### Summary\n"
                    "Moderate concerns detected in posts and DMs. Evidence suggests age-imbalanced interactions and "
                    "mentions of substance use. Recommended action: monitor and warn if behavior escalates.\n\n"
                    "### Evidence\n- Secrecy in DMs: 'Don't tell anyone we talk here.'\n- Post: 'Trying pills for the first time haha.'\n\n"
                    "### Recommendation\n- Monitor the account for escalation\n- Send a precautionary warning message\n- Escalate to human safety team if further evidence appears."
                )
            }

        else:
            # Real flow: ensure key is present and not placeholder
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key or "YOUR_OPENAI_API_KEY_HERE" in api_key:
                st.error(
                    "OPENAI_API_KEY environment variable is not set or still a placeholder. Please configure it to run real audits."
                )
                return

            with st.spinner("Agents are analyzing this user..."):
                posts_payload = user_posts_df[["post_id", "text"]].to_dict(orient="records")

                users_age_map = dict(zip(users["user_id"], users["age"]))
                inter_payload = []
                for _, row in user_interactions_df.iterrows():
                    r = row.to_dict()
                    r["from_age"] = int(users_age_map.get(r["from_user"], -1))
                    r["to_age"] = int(users_age_map.get(r["to_user"], -1))
                    inter_payload.append(r)

                underage_res = underage_risk_agent(user_row, posts_payload)
                content_res = content_risk_agent(posts_payload)
                interaction_res = interaction_risk_agent(user_row, inter_payload)

                aggregated_findings = {
                    "underage": underage_res,
                    "content": content_res,
                    "interactions": interaction_res,
                }

                policy_res = policy_violation_agent(policies_text, aggregated_findings)
                report_res = report_generator_agent(
                    user_row, underage_res, content_res, interaction_res, policy_res
                )

        st.success("Safety audit completed.")

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("### 🧠 Underage Risk")
            st.json(underage_res)

            st.markdown("### 🎭 Content Risk (aggregated)")
            if "overall" in content_res:
                st.json(content_res["overall"])
            else:
                st.json(content_res)

            st.markdown("### 🤝 Interaction / Grooming Risk")
            st.json(interaction_res)

        with col_right:
            # Risk chart
            st.markdown("### 📊 Risk Overview (Content)")
            risk_map = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
            if "overall" in content_res:
                overall = content_res["overall"]
                bullying = risk_map.get(overall.get("bullying_risk", "none"), 0)
                selfharm = risk_map.get(overall.get("self_harm_risk", "none"), 0)
                sexual = risk_map.get(overall.get("sexual_exploitation_risk", "none"), 0)
                substance = risk_map.get(
                    overall.get("substance_abuse_risk", "none"), 0
                )

                risk_df = pd.DataFrame(
                    {
                        "Risk type": [
                            "Bullying",
                            "Self-harm",
                            "Sexual exploitation",
                            "Substance abuse",
                        ],
                        "Severity (0–4)": [bullying, selfharm, sexual, substance],
                    }
                ).set_index("Risk type")

                st.bar_chart(risk_df)
            else:
                st.write("No aggregated content risk data available.")

            st.markdown("### 📜 Policy Evaluation")
            st.json(policy_res)

            st.markdown("### 🔝 Final Safety Report")
            if report_res:
                st.write(
                    "**Title:**",
                    report_res.get("risk_title", f"{PROJECT_NAME} Safety Report"),
                )
                st.write(
                    "**Overall Risk Score:**",
                    report_res.get("overall_risk_score", "N/A"),
                )
                st.write("**Summary:**", report_res.get("risk_summary", ""))
                st.markdown("---")
                st.markdown(report_res.get("markdown_report", ""))
            else:
                st.write("No report generated.")

            # Simple text download for the report
            if report_res:
                report_text = (
                    f"# {report_res.get('risk_title', f'{PROJECT_NAME} Safety Report')}\n\n"
                )
                report_text += report_res.get("markdown_report", "")
                st.download_button(
                    "⬇ Download Report as .txt",
                    data=report_text,
                    file_name=f"{PROJECT_SLUG}_safety_report_{selected_user_id}.txt",
                    mime="text/plain",
                )

    st.markdown("---")
    st.markdown("### 📘 Safety Policies Used")
    with st.expander("View policies"):
        st.text(load_policies())


if __name__ == "__main__":
    main()
