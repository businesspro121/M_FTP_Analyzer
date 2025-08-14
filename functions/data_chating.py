from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from ftp_rules import load_rules, detect_policy_violations
import pandas as pd
import os
import json

# Initialize Oracle OCI LLM
llm = ChatOCIGenAI(
    model_id="cohere.command",  # Replace with your actual model ID
    service_endpoint="https://your-oci-endpoint",  # Replace with your OCI endpoint
    compartment_id="your-compartment-id"  # Replace with your compartment ID
)

# Load policy rules (textual guidance for LLM)
def load_policies():
    policy_path = os.path.join("functions", "ftp_policies.txt")
    if os.path.exists(policy_path):
        with open(policy_path, "r") as f:
            return f.read()
    else:
        return "No policy rules provided."

# Prompt template for LLM
template = """
You are an expert in Fund Transfer Pricing analysis.

Follow these policy rules:
{policies}

Given the following question and the list of detected FTP violations, provide a detailed explanation and suggest resolutions.

Question: {question}
Violations:
{data}
"""

prompt = PromptTemplate(
    input_variables=["question", "data", "policies"],
    template=template
)

chain = LLMChain(llm=llm, prompt=prompt)

# Main function to run FTP analysis
def ask_llm(question, df):
    policies = load_policies()
    rules = load_rules()
    violations_df = detect_policy_violations(df, rules)

    if violations_df.empty:
        return "✅ No violations detected based on current FTP rules."

    violations_text = violations_df.to_string(index=False)

    response = chain.run({
        "question": question,
        "data": violations_text,
        "policies": policies
    })

    return response
