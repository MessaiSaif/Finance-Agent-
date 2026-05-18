from langchain.tools import tool
from src.database.storage import get_all_invoices, get_monthly_stats
from src.core.rag_engine import search_invoices
import json

@tool
def query_invoice_database(query: str) -> str:
    """Useful for answering questions about specific invoices using RAG (search). 
    Input should be a natural language question."""
    results = search_invoices(query)
    context = "\n---\n".join([r.page_content for r in results])
    return f"Relevant information from invoices:\n{context}"

@tool
def generate_bilan_report() -> str:
    """Useful for generating a summary report (bilan) of all invoices, 
    including monthly totals and counts. No input required."""
    stats = get_monthly_stats()
    if not stats:
        return "No invoice data available to generate a report."
    
    report = "Monthly Invoice Summary (Bilan):\n"
    total_revenue = 0
    for month, data in sorted(stats.items()):
        report += f"- {month}: {data['count']} invoices, Total TTC: {data['total']:.3f}\n"
        total_revenue += data['total']
    
    report += f"\nGrand Total TTC: {total_revenue:.3f}"
    return report

@tool
def get_invoice_details(invoice_id: str) -> str:
    """Useful for getting the full structured details of a specific invoice by its ID."""
    invoices = get_all_invoices()
    for inv in invoices:
        if inv.get("invoice_id") == invoice_id:
            return json.dumps(inv, indent=2)
    return f"Invoice with ID {invoice_id} not found."

@tool
def list_all_invoices_summary() -> str:
    """Useful for seeing a numbered list of all available invoices to find one by its position (e.g. 'the fifth invoice')."""
    invoices = get_all_invoices()
    if not invoices:
        return "No invoices found in the database."
    
    summary = "List of all invoices:\n"
    for i, inv in enumerate(invoices, 1):
        summary += f"{i}. ID: {inv.get('invoice_id')} | Date: {inv.get('date')} | Total: {inv.get('total_ttc')}\n"
    return summary
