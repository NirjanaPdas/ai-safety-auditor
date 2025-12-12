<!-- ===================== -->
<!-- SafeScroll App Banner -->
<!-- ===================== -->

<p align="center">
  <img src="assets/safescroll_overview.png" width="100%" />
</p>

<p align="center">
  <img src="assets/safescroll_moderation.png" width="100%" />
</p>

---


# 🛡️ AI Safety & Risk Auditor for Social Platforms

This project is a small simulation of an **internal Trust & Safety tool** for a social media platform.

It uses a **multi-agent LLM pipeline** on top of synthetic company data (users, posts, DMs) to:

- Analyse user posts and private messages
- Detect underage risk / misrepresentation
- Detect bullying and harassment
- Detect self-harm / mental health risk
- Detect grooming / sexual exploitation patterns
- Detect substance abuse promotion
- Map the findings to simplified **safety policies**
- Generate a **user-level safety report** with an overall risk score and recommended action

All data in this project is **synthetic** and for **research/demo purposes only**.

---

## ✨ Features

- Multi-agent GenAI workflow:
  - Underage Risk Agent
  - Content Safety Agent (bullying, self-harm, grooming, substance)
  - Interaction/Grooming Agent
  - Policy Violation Agent
  - Safety Report Generator
- Streamlit dashboard to:
  - Select a user
  - Inspect posts + DMs
  - Run a complete safety audit
  - View structured JSON outputs
  - Visualise risk levels with a bar chart
  - Download the final report as a `.txt` file

---

## 🗂 Folder structure

```text
 safe-scroll/
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── safescroll_overview.png
│   └── safescroll_moderation.png
├── data/
│   ├── interactions.csv
│   ├── posts.csv
│   └── users.csv
├── policies/
│   └── safety_policies.txt
├── README.md
├── agents.py
├── app.py
├── generate_synthetic_data.py
└── requirements.txt
```
