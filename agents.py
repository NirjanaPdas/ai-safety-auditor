import os
import json
from typing import Dict, List

from openai import OpenAI

# Project branding
PROJECT_NAME = "SafeScroll"
PROJECT_SLUG = "safescroll"

# OpenAI client (expects OPENAI_API_KEY env variable)
# Keep the placeholder; user must set the env var in production.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE"))

# Default model used for agents (change if you'd like)
LLM_MODEL = "gpt-4o-mini"


def _run_json_agent(system_prompt: str, user_content: str, max_tokens: int = 400) -> Dict:
    """
    Helper to call an LLM agent and parse JSON response.

    Returns an empty dict on parse failure.
    """
    try:
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
        )
    except Exception as e:
        # Return a sensible error structure so callers can handle missing output
        return {"error": f"LLM request failed: {e}"}

    # Extract content in a defensive way
    try:
        content = resp.choices[0].message.content
    except Exception:
        # Unexpected response shape
        return {"error": "unexpected LLM response format"}

    # Try to parse JSON strictly, fall back to heuristic extraction
    try:
        return json.loads(content)
    except Exception:
        # attempt to recover JSON substring
        try:
            idx = content.rfind("{")
            if idx != -1:
                return json.loads(content[idx:])
        except Exception:
            # best-effort: return raw content for debugging
            return {"error": "failed to parse JSON", "raw": content}


def underage_risk_agent(user_profile: Dict, posts: List[Dict]) -> Dict:
    """
    Agent: Estimate underage risk based on declared age and content style.

    Input:
      - user_profile: {"user_id": "...", "age": int, ...}
      - posts: list of {"post_id": "...", "text": "...", ...}

    Output JSON structure:
    {
      "is_minor_suspected": true,
      "underage_misrepresentation_risk": 0,
      "reason": ""
    }
    """
    system_prompt = f"""
You are an Underage Risk Detection Agent for {PROJECT_NAME}.

You receive:
- A user profile (age, account_type, created_at)
- A sample of their posts

Task:
1. Estimate if the user appears UNDER 18 or ADULT based on content style and declared age.
2. Output a risk score for "underage_misrepresentation" from 0 to 100.
3. Provide reasoning.

Output strict JSON:

{{
  "is_minor_suspected": true,
  "underage_misrepresentation_risk": 0,
  "reason": ""
}}
"""
    user_str = json.dumps(user_profile, ensure_ascii=False)
    posts_str = json.dumps(posts, ensure_ascii=False)
    user_content = f"USER_PROFILE:\n{user_str}\n\nSAMPLE_POSTS:\n{posts_str}"
    return _run_json_agent(system_prompt, user_content)


def content_risk_agent(posts: List[Dict]) -> Dict:
    """
    Agent: Analyze content for bullying, self-harm, sexual exploitation, substance abuse.

    Input:
      - posts: list of {"post_id": "...", "text": "...", ...}

    Output JSON structure:
    {
      "per_post": [
        {
          "post_id": "",
          "text": "",
          "bullying_risk": "none",
          "self_harm_risk": "none",
          "sexual_exploitation_risk": "none",
          "substance_abuse_risk": "none",
          "notes": ""
        }
      ],
      "overall": {
        "bullying_risk": "none",
        "self_harm_risk": "none",
        "sexual_exploitation_risk": "none",
        "substance_abuse_risk": "none",
        "summary": ""
      }
    }
    """
    system_prompt = f"""
You are a Content Safety Agent working for {PROJECT_NAME}.

You receive a list of posts from one user. For each post, you should detect:
- bullying
- self_harm
- sexual_exploitation_or_grooming
- substance_abuse

Then aggregate into overall risk levels.

Overall risk levels should be "none", "low", "medium", or "high".

Output this strict JSON:

{{
  "per_post": [
    {{
      "post_id": "",
      "text": "",
      "bullying_risk": "none",
      "self_harm_risk": "none",
      "sexual_exploitation_risk": "none",
      "substance_abuse_risk": "none",
      "notes": ""
    }}
  ],
  "overall": {{
    "bullying_risk": "none",
    "self_harm_risk": "none",
    "sexual_exploitation_risk": "none",
    "substance_abuse_risk": "none",
    "summary": ""
  }}
}}
"""
    posts_str = json.dumps(posts, ensure_ascii=False)
    return _run_json_agent(system_prompt, posts_str, max_tokens=1000)


def interaction_risk_agent(user_profile: Dict, interactions: List[Dict]) -> Dict:
    """
    Agent: Analyze direct messages / interactions for grooming-like patterns and power imbalance.

    Input:
      - user_profile: profile for the audited user
      - interactions: list of {"interaction_id","from_user","to_user","text","from_age","to_age",...}

    Output JSON structure:
    {
      "grooming_risk": "none",
      "evidence": [
        {
          "interaction_id": "",
          "text_snippet": "",
          "comment": ""
        }
      ],
      "summary": ""
    }
    """
    system_prompt = f"""
You are an Interaction Risk Agent for {PROJECT_NAME}.

You receive:
- A user profile
- A list of direct message interactions between this user and others.
  Each interaction includes from_user, to_user, text, and age information (in metadata).

Task:
1. Detect if there are signs of grooming or sexual exploitation risk.
2. Consider age differences (older messaging younger).
3. Output a "grooming_risk" level: "none", "low", "medium", "high", "critical".
4. Provide key evidence snippets.

Output strict JSON:

{{
  "grooming_risk": "none",
  "evidence": [
    {{
      "interaction_id": "",
      "text_snippet": "",
      "comment": ""
    }}
  ],
  "summary": ""
}}
"""
    payload = {"user_profile": user_profile, "interactions": interactions}
    return _run_json_agent(system_prompt, json.dumps(payload, ensure_ascii=False), max_tokens=800)


def policy_violation_agent(policy_text: str, aggregated_findings: Dict) -> Dict:
    """
    Agent: Map earlier findings to company policy violations.

    Input:
      - policy_text: raw company safety policies (string)
      - aggregated_findings: dict combining outputs from other agents

    Output JSON structure:
    {
      "violated_sections": [],
      "overall_severity": "low",
      "recommended_action": "",
      "explanation": ""
    }
    """
    system_prompt = f"""
You are a Policy Violation Agent for {PROJECT_NAME}.

You receive:
- Company safety policies text.
- Aggregated findings from other safety agents about a single user.

Task:
1. Map the findings to specific policy sections that are likely violated.
2. Determine overall severity: "low", "medium", "high", "critical".
3. Recommend an action:
   - "monitor"
   - "warn"
   - "restrict_features"
   - "escalate_to_safety_team"
   - "temporary_suspension"
4. Provide a short explanation.

Output strict JSON:

{{
  "violated_sections": [],
  "overall_severity": "low",
  "recommended_action": "",
  "explanation": ""
}}
"""
    payload = {"policies": policy_text, "findings": aggregated_findings}
    return _run_json_agent(system_prompt, json.dumps(payload, ensure_ascii=False), max_tokens=600)


def report_generator_agent(
    user_profile: Dict,
    underage: Dict,
    content: Dict,
    interactions: Dict,
    policy_result: Dict,
) -> Dict:
    """
    Agent: Generate a human-readable safety report (markdown-style).

    Input:
      - structured JSON from the other agents
    Output JSON structure:
    {
      "risk_title": "",
      "overall_risk_score": 0,
      "risk_summary": "",
      "markdown_report": ""
    }
    """
    system_prompt = f"""
You are a Safety Report Generator Agent for {PROJECT_NAME}.

You receive structured JSON from several safety agents for ONE user:
- underage risk
- content risk
- interaction/grooming risk
- policy violation summary

Task:
1. Produce a clear, human-readable report (markdown-style).
2. Include:
   - short user summary
   - key risks
   - evidence examples
   - final recommended action

Output strict JSON:

{{
  "risk_title": "",
  "overall_risk_score": 0,
  "risk_summary": "",
  "markdown_report": ""
}}
"""
    payload = {
        "user_profile": user_profile,
        "underage": underage,
        "content": content,
        "interactions": interactions,
        "policy_result": policy_result,
    }
    return _run_json_agent(system_prompt, json.dumps(payload, ensure_ascii=False), max_tokens=900)
