from fpdf import FPDF
import pandas as pd

def generate_dashboard_pdf(stats, invoices):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=16, style="B")
    pdf.cell(190, 10, "Financial Agent - Dashboard Report", align='C')
    pdf.ln(15)
    
    # Overview
    df = pd.DataFrame([
        {"Month": m, "Invoices": d["count"], "Total TTC": d["total"]}
        for m, d in stats.items()
    ]).sort_values("Month")
    total_revenue = df["Total TTC"].sum()
    total_count = df["Invoices"].sum()
    avg_invoice = total_revenue / total_count if total_count > 0 else 0
    
    pdf.set_font("Helvetica", size=12, style="B")
    pdf.cell(190, 10, "Global Overview:")
    pdf.ln(10)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(190, 8, f"Total Volume: {total_revenue:,.2f} TND")
    pdf.ln(8)
    pdf.cell(190, 8, f"Processed Docs: {total_count}")
    pdf.ln(8)
    pdf.cell(190, 8, f"Avg Value: {avg_invoice:,.2f} TND")
    pdf.ln(12)
    
    # Monthly Stats
    pdf.set_font("Helvetica", size=12, style="B")
    pdf.cell(190, 10, "Monthly Revenue Trend:")
    pdf.ln(10)
    pdf.set_font("Helvetica", size=10)
    
    # Table header
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(60, 10, "Month", border=1, fill=True)
    pdf.cell(60, 10, "Invoices Count", border=1, fill=True)
    pdf.cell(60, 10, "Total TTC (TND)", border=1, fill=True)
    pdf.ln()
    
    for _, row in df.iterrows():
        pdf.cell(60, 10, str(row["Month"]), border=1)
        pdf.cell(60, 10, str(row["Invoices"]), border=1)
        pdf.cell(60, 10, f"{row['Total TTC']:,.2f}", border=1)
        pdf.ln()
    
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12, style="B")
    pdf.cell(190, 10, "Recent Invoices (Top 5):")
    pdf.ln(10)
    pdf.set_font("Helvetica", size=10)
    
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(60, 10, "Invoice ID", border=1, fill=True)
    pdf.cell(60, 10, "Date", border=1, fill=True)
    pdf.cell(60, 10, "Total TTC", border=1, fill=True)
    pdf.ln()
    
    invoices_df = pd.DataFrame(invoices)[["invoice_id", "date", "total_ttc"]].tail(5)
    for _, row in invoices_df.iterrows():
        pdf.cell(60, 10, str(row["invoice_id"]), border=1)
        pdf.cell(60, 10, str(row["date"]), border=1)
        pdf.cell(60, 10, str(row["total_ttc"]), border=1)
        pdf.ln()
        
    return bytes(pdf.output())
