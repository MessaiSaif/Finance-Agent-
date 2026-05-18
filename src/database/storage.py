import json
import os
from datetime import datetime

DB_PATH = "data/db/invoices.json"
CHAT_HISTORY_PATH = "data/db/chat_history.json"

def save_chat_history(messages):
    """Saves chat messages to a JSON file."""
    if not os.path.exists(os.path.dirname(CHAT_HISTORY_PATH)):
        os.makedirs(os.path.dirname(CHAT_HISTORY_PATH))
    with open(CHAT_HISTORY_PATH, "w") as f:
        json.dump(messages, f, indent=4)

def load_chat_history():
    """Loads chat messages from a JSON file."""
    if os.path.exists(CHAT_HISTORY_PATH):
        with open(CHAT_HISTORY_PATH, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def clear_chat_history():
    """Deletes the chat history file."""
    if os.path.exists(CHAT_HISTORY_PATH):
        os.remove(CHAT_HISTORY_PATH)

def save_invoice_data(data):
    """Saves invoice data to a JSON file."""
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    
    existing_data = []
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    
    # Check if invoice already exists to avoid duplicates
    invoice_id = data.get("invoice_id")
    if invoice_id:
        existing_data = [inv for inv in existing_data if inv.get("invoice_id") != invoice_id]
    
    existing_data.append(data)
    
    with open(DB_PATH, "w") as f:
        json.dump(existing_data, f, indent=4)

def get_all_invoices():
    """Retrieves all invoice data."""
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def get_monthly_stats():
    """Calculates statistics per month."""
    invoices = get_all_invoices()
    stats = {}
    
    for inv in invoices:
        date_str = inv.get("date")
        try:
            # Assumes date format DD/MM/YYYY or similar
            date_obj = None
            for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue
            
            if date_obj:
                month_key = date_obj.strftime("%Y-%m")
                total_ttc = float(str(inv.get("total_ttc", 0)).replace(',', ''))
                
                if month_key not in stats:
                    stats[month_key] = {"count": 0, "total": 0.0}
                
                stats[month_key]["count"] += 1
                stats[month_key]["total"] += total_ttc
        except Exception as e:
            print(f"Error processing invoice date {date_str}: {e}")
            
    return stats
