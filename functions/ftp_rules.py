import pandas as pd
import json
import os
import json as pyjson  # for stringifying row_context

# === CONFIG ===
ROW_CONTEXT_FIELDS = None  # None = include all columns; or list of column names

def load_rules(path: str = os.path.join("functions", "ftp_policies.json")):
    """Loads rules from a JSON file."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _make_row_context(row: pd.Series):
    """Return either full or filtered row dict, with all values JSON‑serializable."""
    if ROW_CONTEXT_FIELDS is None:
        data = row.to_dict()
    else:
        data = {field: row.get(field, None) for field in ROW_CONTEXT_FIELDS}
    # Convert Timestamps and other non‑serializable objects to strings
    for k, v in data.items():
        if isinstance(v, (pd.Timestamp, )):
            data[k] = v.isoformat()
        else:
            try:
                pyjson.dumps(v)  # test serializability
            except TypeError:
                data[k] = str(v)
    return data

def detect_policy_violations(df: pd.DataFrame, rules: list) -> pd.DataFrame:
    """Evaluates each rule and returns violations as a DataFrame with JSON‑safe row_context."""
    violations = []

    for rule in rules:
        col = rule.get("column")
        condition = rule["condition"]
        description = rule.get("description", "No description")

        if col and col not in df.columns:
            print(f"⚠️ Skipping rule: column '{col}' not found in Excel data.")
            continue

        for _, row in df.iterrows():
            try:
                local_vars = {c: row[c] for c in df.columns}
                local_vars["x"] = row[col] if col else None
                local_vars["pd"] = pd

                if eval(condition, {}, local_vars):
                    row_context = _make_row_context(row)
                    violations.append({
                        "description": description,
                        "row_context": pyjson.dumps(row_context, ensure_ascii=False)
                    })

            except Exception as e:
                row_context = _make_row_context(row)
                violations.append({
                    "description": f"Error evaluating rule: {e}",
                    "row_context": pyjson.dumps(row_context, ensure_ascii=False)
                })

    return pd.DataFrame(violations)
