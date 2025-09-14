import io
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


REQUIRED_COLUMNS = ["date", "product", "quantity", "unit_price"]
OPTIONAL_COLUMNS = ["category", "payment_method", "discount"]


def load_transactions_from_csv(file_bytes: bytes, encoding: str = "utf-8") -> pd.DataFrame:
    """Load transactions from CSV bytes with robust parsing.

    Accepts CSVs with flexible headers and attempts to normalize columns.
    """
    try:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
    except Exception:
        # Try without encoding hint or with excel dialects
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as e:  # last resort
            raise ValueError(f"Unable to read CSV: {e}")
    return normalize_transactions(df)


def normalize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize common retail columns and ensure required columns exist.

    Column mapping supported:
    - date: [date, order_date, txn_date]
    - product: [product, sku, item]
    - quantity: [quantity, qty, units]
    - unit_price: [unit_price, price, selling_price]
    - discount: [discount, discount_amount, disc]
    - category: [category, cat]
    - payment_method: [payment_method, payment, pay_method]
    """
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    alias_map = {
        "date": ["date", "order_date", "txn_date", "timestamp"],
        "product": ["product", "sku", "item", "product_name"],
        "quantity": ["quantity", "qty", "units", "count"],
        "unit_price": ["unit_price", "price", "selling_price", "unitprice"],
        "discount": ["discount", "discount_amount", "disc"],
        "category": ["category", "cat"],
        "payment_method": ["payment_method", "payment", "pay_method", "paymenttype"],
    }

    def find_first(cols: List[str]) -> Optional[str]:
        for c in cols:
            if c in df.columns:
                return c
        return None

    mapped: Dict[str, Optional[str]] = {k: find_first(v) for k, v in alias_map.items()}

    # Create normalized columns
    for target in REQUIRED_COLUMNS + OPTIONAL_COLUMNS:
        src = mapped.get(target)
        if src and src in df.columns:
            df[target] = df[src]
        else:
            # Fill sensible defaults
            if target == "date":
                df[target] = pd.Timestamp("today").normalize()
            elif target == "product":
                df[target] = df.get("product", "Unknown")
            elif target == "quantity":
                df[target] = 1
            elif target == "unit_price":
                df[target] = 0.0
            elif target == "discount":
                df[target] = 0.0
            else:
                df[target] = np.nan

    # Coerce types
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0.0)
    df["product"] = df["product"].astype(str)
    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["date"] = df["date"].fillna(pd.Timestamp("today").normalize())

    # Derived
    df["revenue"] = (df["quantity"] * df["unit_price"]) - df["discount"].fillna(0.0)
    df["day"] = df["date"].dt.date
    return df[[
        "date", "day", "product", "category", "quantity", "unit_price", "discount", "revenue", "payment_method"
    ]]


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_orders": 0,
            "avg_order_value": 0.0,
            "top_product": None,
            "top_category": None,
        }

    total_revenue = float(df["revenue"].sum())
    total_orders = int(len(df))
    avg_order_value = float(total_revenue / total_orders) if total_orders else 0.0

    prod_rev = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=False)

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "avg_order_value": round(avg_order_value, 2),
        "top_product": None if prod_rev.empty else prod_rev.index[0],
        "top_category": None if cat_rev.empty else (cat_rev.index[0] if str(cat_rev.index[0]) != "nan" else None),
    }


def plot_top_products_bar(df: pd.DataFrame, top_n: int = 5) -> bytes:
    """Return PNG bytes of a matplotlib bar chart of top products by revenue."""
    fig, ax = plt.subplots(figsize=(6, 4))
    if df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        prod_rev = df.groupby("product")["revenue"].sum().sort_values(ascending=False).head(top_n)
        ax.bar(prod_rev.index.astype(str), prod_rev.values, color="#2563eb")
        ax.set_title("Top Products by Revenue")
        ax.set_ylabel("Revenue")
        ax.set_xlabel("Product")
        ax.tick_params(axis='x', rotation=30)
        ax.grid(axis="y", linestyle=":", alpha=0.4)
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def plot_daily_revenue_line(df: pd.DataFrame) -> bytes:
    """Return PNG bytes of a matplotlib line chart of revenue by day."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    if df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        day_rev = df.groupby("day")["revenue"].sum().sort_index()
        ax.plot(list(day_rev.index), list(day_rev.values), marker="o", color="#16a34a")
        ax.set_title("Revenue by Day")
        ax.set_ylabel("Revenue")
        ax.set_xlabel("Day")
        ax.grid(True, linestyle=":", alpha=0.4)
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def build_json_for_ai(df: pd.DataFrame, kpis: Dict[str, Any], max_rows: int = 50) -> str:
    """Compact JSON payload for LLM containing KPIs and a small sample of rows."""
    sample = df.head(max_rows)[["day", "product", "category", "quantity", "unit_price", "discount", "revenue"]].copy()
    sample["day"] = sample["day"].astype(str)
    payload = {
        "kpis": kpis,
        "sample_rows": sample.to_dict(orient="records"),
    }
    return json.dumps(payload, ensure_ascii=False)


def make_pdf_report(
    kpis: Dict[str, Any],
    top_products_png: bytes,
    daily_rev_png: Optional[bytes],
    insights: Dict[str, Any],
) -> bytes:
    """Build a simple PDF with KPIs, charts, and insights using reportlab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm)

    elements: List[Any] = []
    title_style = ParagraphStyle(name="Title", fontSize=18, leading=22, spaceAfter=10)
    h_style = ParagraphStyle(name="Heading", fontSize=14, leading=18, spaceBefore=10, spaceAfter=6)
    p_style = ParagraphStyle(name="Body", fontSize=10, leading=14)

    elements.append(Paragraph("AI Business Saathi — Executive Report", title_style))

    # KPIs table
    elements.append(Paragraph("Key Performance Indicators", h_style))
    kpi_rows = [
        ["Total Revenue", f"₹{kpis.get('total_revenue', 0):,.2f}"],
        ["Total Orders", f"{kpis.get('total_orders', 0):,}"],
        ["Avg Order Value", f"₹{kpis.get('avg_order_value', 0):,.2f}"],
        ["Top Product", str(kpis.get('top_product') or '-')],
        ["Top Category", str(kpis.get('top_category') or '-')],
    ]
    tbl = Table(kpi_rows, hAlign="LEFT", colWidths=[80 * mm, 60 * mm])
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 8))

    # Charts
    elements.append(Paragraph("Top Products", h_style))
    elements.append(Image(io.BytesIO(top_products_png), width=160 * mm, height=90 * mm))

    if daily_rev_png:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Revenue Trend", h_style))
        elements.append(Image(io.BytesIO(daily_rev_png), width=160 * mm, height=80 * mm))

    # Insights
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Executive Summary (EN)", h_style))
    elements.append(Paragraph(str(insights.get("executive_summary_en", "-")), p_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("Executive Summary (HI)", h_style))
    elements.append(Paragraph(str(insights.get("executive_summary_hi", "-")), p_style))

    recos = insights.get("recommendations", []) or []
    if recos:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Top Recommendations", h_style))
        for i, r in enumerate(recos[:3], start=1):
            elements.append(Paragraph(f"{i}. {r}", p_style))

    doc.build(elements)
    pdf = buf.getvalue()
    buf.close()
    return pdf


