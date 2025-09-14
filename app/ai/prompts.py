from typing import Dict


def build_insights_prompt(data_json: str) -> str:
    """Return a compact instruction asking for strict JSON with insights.

    The assistant must return a JSON object with keys:
    - executive_summary_en: string
    - executive_summary_hi: string
    - recommendations: string[] (3-5 concise bullets)
    - kpi_commentary: { [kpi: string]: string }
    - risks: string[] (optional)
    - opportunities: string[] (optional)
    """
    schema_note = (
        "Return STRICT JSON with keys: executive_summary_en, executive_summary_hi, "
        "recommendations (array of strings), kpi_commentary (object), risks (array), opportunities (array)."
    )
    return (
        f"You are an expert retail analyst. Analyze the following JSON data and provide actionable, concise insights. "
        f"Use an upbeat but professional tone. {schema_note}\n\nDATA:\n" + data_json
    )


