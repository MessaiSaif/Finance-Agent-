import streamlit as st
import os
import pandas as pd
import plotly.express as px
from src.core.processor import process_invoice, extract_text_from_pdf
from src.database.storage import (
    save_invoice_data, get_all_invoices, get_monthly_stats,
    save_chat_history, load_chat_history, clear_chat_history
)
from src.core.rag_engine import index_invoice
from src.core.agent import get_agent_executor
from src.ui.styles import inject_custom_css, get_header_html, get_icon
from dotenv import load_dotenv

# Page config
st.set_page_config(page_title="Finance Agent", page_icon="💰", layout="wide")

# Load environment & CSS
load_dotenv()
inject_custom_css()

# Header
st.markdown(get_header_html(), unsafe_allow_html=True)

# Main Navigation
tab1, tab2, tab3 = st.tabs([
    f'Market Insights', 
    f'Invoice Processor', 
    f'Finance Chat'
])

# --- TAB 1: Insights ---
with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    header_col1, header_col2, header_col3 = st.columns([0.1, 0.6, 0.3])
    with header_col1:
        st.markdown(get_icon("accounting"), unsafe_allow_html=True)
    with header_col2:
        st.subheader("Financial Agent Dashboard")
    
    stats = get_monthly_stats()
    
    with header_col3:
        if stats:
            invoices = get_all_invoices()
            from src.core.pdf_generator import generate_dashboard_pdf
            pdf_data = generate_dashboard_pdf(stats, invoices)
            st.download_button(
                label="Export PDF",
                data=pdf_data,
                file_name="dashboard_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    
    if stats:
        df = pd.DataFrame([
            {"Month": m, "Invoices": d["count"], "Total TTC": d["total"]}
            for m, d in stats.items()
        ]).sort_values("Month")
        
        col1, col2, col3 = st.columns(3)
        total_revenue = df["Total TTC"].sum()
        total_count = df["Invoices"].sum()
        avg_invoice = total_revenue / total_count if total_count > 0 else 0
        
        col1.metric("Total Volume", f"{total_revenue:,.2f} TND")
        col2.metric("Processed Docs", total_count)
        col3.metric("Avg Value", f"{avg_invoice:,.2f} TND")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig = px.bar(df, x="Month", y="Total TTC", 
                         title="Monthly Revenue Trend",
                         template="plotly_dark",
                         color_discrete_sequence=["#00d2ff"])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.write("Recent Activity")
            invoices = get_all_invoices()
            if invoices:
                recent_df = pd.DataFrame(invoices)[["invoice_id", "date", "total_ttc"]].tail(5)
                st.table(recent_df)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Start by processing an invoice to see your insights.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: Processing ---
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Upload Invoice (PDF or Image)")
    uploaded_file = st.file_uploader("Drop your PDF or Image here", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        file_path = os.path.join("data/invoices", uploaded_file.name)
        if not os.path.exists("data/invoices"):
            os.makedirs("data/invoices")
            
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("Analyze & Store Data"):
            with st.status("Extracting Intelligence...", expanded=True) as status:
                try:
                    st.write("Analyzing document structure...")
                    data = process_invoice(file_path)
                    
                    st.write("Saving to secure database...")
                    save_invoice_data(data)
                    
                    if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                        st.write("Indexing text for search...")
                        text = extract_text_from_pdf(file_path)
                        index_invoice(text, {"invoice_id": data["invoice_id"], "date": data["date"]})
                    
                    status.update(label="Analysis Complete!", state="complete", expanded=False)
                    st.success(f"Invoice {data['invoice_id']} successfully integrated.")
                    st.json(data)
                except Exception as e:
                    status.update(label="Analysis Failed", state="error")
                    st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: Finance Chat ---
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Finance Intelligence Hub")
    st.info("Ask anything about your invoices, trends, or financial status.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Load history
    if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history()

    # Chat controls in columns
    ctrl1, ctrl2 = st.columns([6, 1])
    with ctrl2:
        if st.button("Clear History"):
            clear_chat_history()
            st.session_state.messages = []
            st.rerun()

    # Display history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            role_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
            st.markdown(f"""
                <div class="chat-bubble {role_class}">
                    <strong>{"You" if message["role"] == "user" else "Finance Assistant"}</strong><br>
                    {message["content"]}
                </div>
            """, unsafe_allow_html=True)

    # Input
    if prompt := st.chat_input("Query your invoice knowledge base..."):
        # Add to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_chat_history(st.session_state.messages)
        
        # Display immediately
        with chat_container:
            st.markdown(f'<div class="chat-bubble user-bubble"><strong>You</strong><br>{prompt}</div>', unsafe_allow_html=True)

        # Agent logic
        with chat_container:
            with st.spinner("Analyzing data..."):
                try:
                    agent = get_agent_executor()
                    response = agent.invoke({"input": prompt})
                    answer = response["output"]
                    
                    if isinstance(answer, list):
                        answer = "".join([item.get("text", "") for item in answer if isinstance(item, dict)])
                    
                    st.markdown(f'<div class="chat-bubble assistant-bubble"><strong>Finance Assistant</strong><br>{answer}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    save_chat_history(st.session_state.messages)
                except Exception as e:
                    st.error(f"Engine Error: {e}")
