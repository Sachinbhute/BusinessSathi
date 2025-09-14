"""
AI Business Saathi - Retail Analytics Dashboard
A Streamlit app for analyzing shop transactions and generating AI-powered insights.
"""

import io
import os
import sys
import tempfile
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
from dotenv import load_dotenv, find_dotenv

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.client_factory import AIClient, AIProvider
from app.ai.prompts import build_insights_prompt
from app.utils.data_utils import (
    build_json_for_ai,
    compute_kpis,
    load_transactions_from_csv,
    make_pdf_report,
    normalize_transactions,
    plot_daily_revenue_line,
    plot_top_products_bar,
)

# Load environment variables (robust): always try project root .env
# _env_path = find_dotenv(usecwd=True)
# if not _env_path:
#     _env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
# load_dotenv(_env_path)

# Page config
st.set_page_config(
    page_title="AI Business Saathi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .insight-box {
        background-color: #f0f9ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0ea5e9;
        margin: 1rem 0;
        color: #1f2937;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'transactions_df' not in st.session_state:
        st.session_state.transactions_df = pd.DataFrame()
    if 'kpis' not in st.session_state:
        st.session_state.kpis = {}
    if 'insights' not in st.session_state:
        st.session_state.insights = {}
    if 'ai_client' not in st.session_state:
        # Use Gemini as the default provider
        st.session_state.ai_client = AIClient(provider=AIProvider.GEMINI)

def load_sample_data(scenario: str) -> pd.DataFrame:
    """Load predefined sample data scenarios."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_files = {
        "Normal Week": os.path.join(project_root, "sample_data", "shop_sample.csv"),
        "Weekend Boost": os.path.join(project_root, "sample_data", "demo_weekend_boost.csv"), 
        "Slow Week": os.path.join(project_root, "sample_data", "demo_slow_week.csv"),
        "High Value Orders": os.path.join(project_root, "sample_data", "demo_high_value.csv")
    }
    
    file_path = sample_files.get(scenario)
    if file_path and os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return normalize_transactions(df)
    return pd.DataFrame()

def process_transactions(df: pd.DataFrame) -> Tuple[Dict, Dict]:
    """Process transactions and generate KPIs and insights."""
    if df.empty:
        return {}, {}
    
    # Compute KPIs
    kpis = compute_kpis(df)
    
    # Generate AI insights
    try:
        data_json = build_json_for_ai(df, kpis)
        prompt = build_insights_prompt(data_json)
        insights = st.session_state.ai_client.generate_business_insights(prompt)
    except Exception as e:
        st.error(f"❌ **AI Error:** {str(e)}")
        st.info("Please check your API key and internet connection, then try again.")
        insights = {}
    
    return kpis, insights

def render_sidebar():
    """Render the sidebar with data input options."""
    st.sidebar.header("📥 Data Input")
    
    
    # Data source selection
    data_source = st.sidebar.radio(
        "Choose data source:",
        ["Upload CSV", "Manual Entry", "Sample Data"]
    )
    
    if data_source == "Upload CSV":
        uploaded_file = st.sidebar.file_uploader(
            "Upload transaction CSV",
            type=['csv'],
            help="CSV should have columns: date, product, quantity, unit_price (optional: category, discount, payment_method)"
        )
        
        if uploaded_file is not None:
            try:
                df = load_transactions_from_csv(uploaded_file.getvalue())
                st.session_state.transactions_df = df
                st.sidebar.success(f"✅ Loaded {len(df)} transactions")
            except Exception as e:
                st.sidebar.error(f"❌ Error loading file: {str(e)}")
    
    elif data_source == "Manual Entry":
        st.sidebar.subheader("Add Transaction")
        
        with st.sidebar.form("manual_entry"):
            date = st.date_input("Date")
            product = st.text_input("Product")
            quantity = st.number_input("Quantity", min_value=1, value=1)
            unit_price = st.number_input("Unit Price (₹)", min_value=0.0, value=0.0)
            category = st.text_input("Category (optional)")
            discount = st.number_input("Discount (₹)", min_value=0.0, value=0.0)
            payment_method = st.selectbox("Payment Method", ["Cash", "Card", "UPI", "Wallet"])
            
            if st.form_submit_button("Add Transaction"):
                if product and unit_price > 0:
                    new_row = pd.DataFrame([{
                        'date': pd.Timestamp(date),
                        'product': product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'category': category if category else None,
                        'discount': discount,
                        'payment_method': payment_method
                    }])
                    
                    if st.session_state.transactions_df.empty:
                        st.session_state.transactions_df = normalize_transactions(new_row)
                    else:
                        st.session_state.transactions_df = pd.concat([
                            st.session_state.transactions_df, 
                            normalize_transactions(new_row)
                        ], ignore_index=True)
                    
                    st.sidebar.success("✅ Transaction added!")
                    st.rerun()
    
    elif data_source == "Sample Data":
        scenario = st.sidebar.selectbox(
            "Choose demo scenario:",
            ["Normal Week", "Weekend Boost", "Slow Week", "High Value Orders"]
        )
        
        if st.sidebar.button("Load Sample Data"):
            df = load_sample_data(scenario)
            if not df.empty:
                st.session_state.transactions_df = df
                st.sidebar.success(f"✅ Loaded {len(df)} transactions from {scenario}")
            else:
                st.sidebar.error("❌ Sample data not found. Run scripts/generate_sample_data.py first.")
    
    # Clear data button
    if not st.session_state.transactions_df.empty:
        if st.sidebar.button("🗑️ Clear All Data"):
            st.session_state.transactions_df = pd.DataFrame()
            st.session_state.kpis = {}
            st.session_state.insights = {}
            st.rerun()

def render_main_content():
    """Render the main dashboard content."""
    st.markdown('<h1 class="main-header">🤖 AI Business Saathi</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6b7280; margin-bottom: 2rem;">Retail Analytics Dashboard with AI-Powered Insights</p>', unsafe_allow_html=True)
    
    if st.session_state.transactions_df.empty:
        st.info("👈 Please load some transaction data using the sidebar to get started!")
        return
    
    # Process data
    with st.spinner("Processing data and generating insights..."):
        kpis, insights = process_transactions(st.session_state.transactions_df)
        st.session_state.kpis = kpis
        st.session_state.insights = insights
    
    # KPIs Section
    st.header("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=f"₹{kpis.get('total_revenue', 0):,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Orders",
            value=f"{kpis.get('total_orders', 0):,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Avg Order Value",
            value=f"₹{kpis.get('avg_order_value', 0):,.2f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Top Product",
            value=kpis.get('top_product', 'N/A'),
            delta=None
        )
    
    # Charts Section
    st.header("📈 Analytics Charts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Products by Revenue")
        top_products_chart = plot_top_products_bar(st.session_state.transactions_df)
        st.image(top_products_chart, use_column_width=True)
    
    with col2:
        st.subheader("Daily Revenue Trend")
        daily_revenue_chart = plot_daily_revenue_line(st.session_state.transactions_df)
        st.image(daily_revenue_chart, use_column_width=True)
    
    # AI Insights Section
    st.header("🤖 AI-Powered Insights")
    
    if not insights:
        st.warning("⚠️ AI insights are not available. Please check your API key and try again.")
        return
    
    # Executive Summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Executive Summary (English)")
        st.markdown(f'<div class="insight-box">{insights.get("executive_summary_en", "No insights available")}</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("Executive Summary (हिंदी)")
        st.markdown(f'<div class="insight-box">{insights.get("executive_summary_hi", "कोई अंतर्दृष्टि उपलब्ध नहीं")}</div>', unsafe_allow_html=True)
    
    # Recommendations
    recommendations = insights.get("recommendations", [])
    recommendations_hi = insights.get("recommendations_hi", [])
    if recommendations:
        st.subheader("💡 Top Recommendations")
        
        # Create tabs for English and Hindi recommendations
        rec_tab1, rec_tab2 = st.tabs(["English", "हिंदी"])
        
        with rec_tab1:
            for i, rec in enumerate(recommendations[:5], 1):
                st.markdown(f"**{i}.** {rec}")
        
        with rec_tab2:
            if recommendations_hi:
                for i, rec in enumerate(recommendations_hi[:5], 1):
                    st.markdown(f"**{i}.** {rec}")
            else:
                st.info("Hindi recommendations not available")
    
    # KPI Commentary
    kpi_commentary = insights.get("kpi_commentary", {})
    kpi_commentary_hi = insights.get("kpi_commentary_hi", {})
    if kpi_commentary:
        st.subheader("📝 KPI Commentary")
        
        # Create tabs for English and Hindi KPI commentary
        kpi_tab1, kpi_tab2 = st.tabs(["English", "हिंदी"])
        
        with kpi_tab1:
            for kpi, commentary in kpi_commentary.items():
                st.markdown(f"**{kpi.replace('_', ' ').title()}:** {commentary}")
        
        with kpi_tab2:
            if kpi_commentary_hi:
                for kpi, commentary in kpi_commentary_hi.items():
                    st.markdown(f"**{kpi.replace('_', ' ').title()}:** {commentary}")
            else:
                st.info("Hindi KPI commentary not available")
    
    # Data Table
    st.header("📋 Transaction Data")
    st.dataframe(
        st.session_state.transactions_df.head(100),
        width="stretch",
        hide_index=True
    )
    
    # Export Section
    st.header("📄 Export Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Generate PDF Report", type="primary"):
            with st.spinner("Generating PDF report..."):
                try:
                    top_products_png = plot_top_products_bar(st.session_state.transactions_df)
                    daily_rev_png = plot_daily_revenue_line(st.session_state.transactions_df)
                    
                    pdf_bytes = make_pdf_report(
                        st.session_state.kpis,
                        top_products_png,
                        daily_rev_png,
                        st.session_state.insights
                    )
                    
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"business_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ PDF report generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    with col2:
        # CSV Export
        csv_data = st.session_state.transactions_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV Data",
            data=csv_data,
            file_name=f"transactions_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def main():
    """Main application function."""
    initialize_session_state()
    render_sidebar()
    render_main_content()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #9ca3af;">AI Business Saathi - Powered by Google Gemini & Streamlit</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
