import pandas as pd
import re
import json
import streamlit as st
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# === LLM initialisation ===
llm = ChatOCIGenAI(
    model_id="cohere.command-r-plus-08-2024",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="ocid1.compartment.oc1..aaaaaaaaxj6dyzjb6zggtwoaavl6apkzzgd7tv3lykpl6bmmf6iffegu5woa",
    model_kwargs={"temperature": 0.0, "max_tokens": 800}
)

# === Load authoritative FTP policies (JSON-driven scope) ===
FTP_SCOPE_AVAILABLE = True
try:
    with open("ftp_policies.json") as f:
        _ftp_policies = json.load(f)
    FTP_POLICY_DESCRIPTIONS = {p["description"] for p in _ftp_policies if "description" in p}
except Exception:
    FTP_SCOPE_AVAILABLE = False
    FTP_POLICY_DESCRIPTIONS = set()

# === Prompt ===
template = """
You are a financial data analyst.

Global total violations: {total_count_all}

Global per-policy counts:
{policy_counts_all}

{scoped_section}

Truncation status:
{truncation_note}

Rules:
- Treat each row in the violations list as a violation/anomaly.
- If total_count_all > 0, you must NOT say there are no anomalies.
- If a scoped section is provided and scoped_total > 0, focus on those. If scoped_total == 0, state that explicitly.
- Do not infer or invent policies, counts, or anomalies beyond the provided data.

Violations Data (respect any truncation noted):
{violations}

Question:
{question}

Answer based ONLY on the supplied data and rules above. Be concise and specific.
"""
prompt = PromptTemplate(
    input_variables=[
        "violations",
        "question",
        "total_count_all",
        "policy_counts_all",
        "scoped_section",
        "truncation_note",
    ],
    template=template
)
chain = LLMChain(llm=llm, prompt=prompt)

# --- Patterns ---
COUNT_TOTAL_PAT       = re.compile(r"\b(how\s+many|number\s+of)\b.*\bviolation", re.IGNORECASE)
COUNT_PER_POLICY_PAT  = re.compile(r"(each|per\s+policy|by\s+policy)", re.IGNORECASE)
TABLE_HINT_PAT        = re.compile(r"(?:show|display|provide|give|list|present).*table|table(?:\s+(?:view|format))?", re.IGNORECASE)
LIST_ROWS_PAT         = re.compile(r"\b(which|what)\b.*\b(entries?|rows?|records?)\b", re.IGNORECASE)
ANOMALY_PAT           = re.compile(r"\b(anomal(?:y|ies)|violation(?:s)?|issue(?:s)?|non[-\s]?compliance|breach(?:es)?)\b", re.IGNORECASE)
FTP_HINT_PAT          = re.compile(r"\bftp\b", re.IGNORECASE)

# --- CSS helpers ---
def inject_white_text_css():
    st.markdown("""
        <style>
        html, body, [class*="stMarkdown"], .stMarkdown p, .stText { color: white !important; }
        .stDataFrame tbody, .stDataFrame td, .stDataFrame th { color: white !important; }
        </style>
    """, unsafe_allow_html=True)

def white_subheader(text: str):
    st.markdown(f"<h3 style='color: white; margin-bottom: 0;'>{text}</h3>", unsafe_allow_html=True)

def query_llm(violations_df, question, max_violations=None, as_streamlit=False):
    """
    Deterministic for counts, anomalies, and scoped (FTP) queries using JSON-driven scope.
    LLM for narrative, with injected global and scoped counts.
    """
    if violations_df is None or violations_df.empty:
        return "No violations found."

    q_lower = question.lower()

    # Auto-enable table mode for table or list-rows hints
    if TABLE_HINT_PAT.search(q_lower) or LIST_ROWS_PAT.search(q_lower):
        as_streamlit = True
    if as_streamlit:
        inject_white_text_css()

    # --- Global counts ---
    total_count_all = len(violations_df)
    per_policy_all = (
        violations_df['description'].value_counts()
        .rename_axis('Policy').reset_index(name='Count')
        .sort_values(by="Count", ascending=False)
    )
    policy_counts_all_str = per_policy_all.to_string(index=False)

    # --- Optional FTP scope ---
    scoped_df = violations_df
    scope_applied = False
    scope_note = ""
    if FTP_HINT_PAT.search(q_lower):
        if FTP_SCOPE_AVAILABLE and FTP_POLICY_DESCRIPTIONS:
            scope_applied = True
            scoped_df = violations_df[violations_df['description'].isin(FTP_POLICY_DESCRIPTIONS)]
            # Short-circuit if scope doesn't reduce the set
            if scoped_df.shape[0] == violations_df.shape[0]:
                scope_applied = False
        else:
            scope_note = "FTP scope file not found or empty — using global dataset."

    scoped_total = len(scoped_df)
    per_policy_scoped_str = (
        scoped_df['description'].value_counts()
        .rename_axis('Policy').reset_index(name='Count')
        .to_string(index=False)
        if scope_applied and not scoped_df.empty else "—"
    )

    # --- Full table branch for "which entries/rows" ---
    if LIST_ROWS_PAT.search(q_lower):
        df_to_show = scoped_df if scope_applied else violations_df
        if as_streamlit:
            scope_label = " (FTP scope)" if scope_applied else ""
            white_subheader(f"Violating entries{scope_label}: {len(df_to_show)}")
            if scope_note:
                st.caption(scope_note)
            st.dataframe(df_to_show, use_container_width=True)
            return ""
        return f"Violating entries:\n{df_to_show.to_string(index=False)}"

    # --- Instant factual answers ---
    if COUNT_TOTAL_PAT.search(q_lower) and not COUNT_PER_POLICY_PAT.search(q_lower):
        if as_streamlit:
            white_subheader(f"Total policy violations: {total_count_all}")
            if scope_note:
                st.caption(scope_note)
            return ""
        return f"Total policy violations: {total_count_all}"

    if COUNT_PER_POLICY_PAT.search(q_lower):
        if as_streamlit:
            white_subheader(f"Total policy violations: {total_count_all}")
            if scope_note:
                st.caption(scope_note)
            st.dataframe(per_policy_all, use_container_width=True)
        else:
            return f"Violations per policy:\n{policy_counts_all_str}"
        return ""

    # --- Anomaly summary ---
    if ANOMALY_PAT.search(q_lower) or scope_applied:
        if scope_applied:
            if scoped_total > 0:
                if as_streamlit:
                    white_subheader(f"FTP anomalies: {scoped_total} (of {total_count_all} total)")
                    st.dataframe(scoped_df['description'].value_counts().reset_index(name='Count'), use_container_width=True)
                    return ""
                return f"FTP anomalies: {scoped_total} (of {total_count_all} total)\nBy policy:\n{per_policy_scoped_str}"
            else:
                msg = f"No FTP anomalies. Global violations present: {total_count_all}."
                if as_streamlit:
                    white_subheader(msg)
                    return ""
                return msg
        else:
            if total_count_all > 0:
                if as_streamlit:
                    white_subheader(f"Anomalies/violations detected: {total_count_all}")
                    st.dataframe(per_policy_all, use_container_width=True)
                    return ""
                return f"Anomalies/violations detected: {total_count_all}\nBy policy:\n{policy_counts_all_str}"
            else:
                if as_streamlit:
                    white_subheader("No anomalies/violations detected.")
                    return ""
                return "No anomalies/violations detected."

    # --- LLM narrative ---
    df_for_prompt = scoped_df if scope_applied else violations_df
    truncated = False
    if max_violations is not None and max_violations < len(df_for_prompt):
        df_for_prompt = df_for_prompt.head(max_violations)
        truncated = True

    violations_str = df_for_prompt.to_string(index=False)
    scoped_section = (
        f"Scoped to FTP policies from ftp_policies.json:\nscoped_total: {scoped_total}\nscoped per-policy counts:\n{per_policy_scoped_str}"
        if scope_applied else f"No scoped filter applied.{(' ' + scope_note) if scope_note else ''}"
    )
    truncation_note = (
        f"YES — showing first {len(df_for_prompt)} of {scoped_total if scope_applied else total_count_all} rows (max_violations={max_violations})."
        if truncated else "NO — all rows included."
    )

    return chain.run({
        "violations": violations_str,
        "question": question,
        "total_count_all": total_count_all,
        "policy_counts_all": policy_counts_all_str,
        "scoped_section": scoped_section,
        "truncation_note": truncation_note,
    })
