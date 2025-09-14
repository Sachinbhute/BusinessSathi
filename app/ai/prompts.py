from typing import Dict


def build_insights_prompt(data_json: str) -> str:
    """Return a compact instruction asking for strict JSON with insights.

    The assistant must return a JSON object with keys:
    - executive_summary_en: string
    - executive_summary_hi: string
    - recommendations: string[] (3-5 concise bullets)
    - recommendations_hi: string[] (Hindi versions of recommendations)
    - kpi_commentary: { [kpi: string]: string }
    - kpi_commentary_hi: { [kpi: string]: string } (Hindi versions)
    - risks: string[] (optional)
    - opportunities: string[] (optional)
    """
    schema_note = (
        "Return STRICT JSON with keys: executive_summary_en, executive_summary_hi, "
        "recommendations (array of strings), recommendations_hi (array of Hindi strings), "
        "kpi_commentary (object), kpi_commentary_hi (object with Hindi strings), "
        "risks (array), opportunities (array)."
    )
    return (
        f"You are an expert retail analyst helping small business owners. Analyze the following JSON data and provide actionable, concise insights. "
        f"Use an upbeat but professional tone for English. For all Hindi fields (executive_summary_hi, recommendations_hi, kpi_commentary_hi), use simple, everyday language that small shop owners can easily understand - avoid formal business terms, use common Hindi words, and write as if talking to a friend. {schema_note}\n\nDATA:\n" + data_json
    )


