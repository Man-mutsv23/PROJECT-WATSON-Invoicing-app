import json
import os
from datetime import datetime
from ibm_watsonx_orchestrate.agent_builder.tools import tool

DB_FILE = 'finance_data.json'

def _load_data():
    if not os.path.exists(DB_FILE):
        return {"invoices": []}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def _save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@tool()
def create_invoice(client_name: str, amount: float, description: str) -> str:
    """
    Creates a new freelance invoice and saves it to the local JSON database.
    """
    data = _load_data()
    invoice = {
        "id": len(data['invoices']) + 1,
        "client": client_name,
        "amount": amount,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": "Pending"  # <--- Adding this ensures data consistency
    }
    data['invoices'].append(invoice)
    _save_data(data)
    return f"Done! Invoice #{invoice['id']} for {client_name} has been recorded as Pending."

@tool()
def mark_invoice_as_paid(invoice_id: int) -> str:
    """
    Updates an invoice status to 'Paid' using its unique ID.
    Use this when the user says they received payment for a specific job.
    """
    data = _load_data()
    found = False
    
    for invoice in data['invoices']:
        if invoice['id'] == invoice_id:
            invoice['status'] = 'Paid'
            found = True
            break
    
    if found:
        _save_data(data)
        return f"Success! Invoice #{invoice_id} has been marked as Paid."
    else:
        return f"Error: Could not find an invoice with ID #{invoice_id}."


@tool()
def get_financial_summary() -> str:
    """
    Calculates the total amount of paid and pending invoices.
    Use this when the user asks 'How much have I made?' or 'What is my status?'.
    """
    data = _load_data()
    total_paid = sum(inv['amount'] for inv in data['invoices'] if inv['status'] == 'Paid')
    total_pending = sum(inv['amount'] for inv in data['invoices'] if inv['status'] == 'Pending')
    
    return (f"Financial Overview:\n"
            f"- Total Paid: ${total_paid:.2f}\n"
            f"- Total Pending: ${total_pending:.2f}\n"
            f"- Outstanding Invoices: {len([i for i in data['invoices'] if i['status'] == 'Pending'])}")

@tool()
def delete_invoice(invoice_id: int) -> str:
    """
    Permanently removes an invoice from the database using its ID.
    Use this if the user made a mistake or needs to cancel a billing record.
    """
    data = _load_data()
    initial_count = len(data['invoices'])
    
    # Filter out the invoice with the matching ID
    data['invoices'] = [inv for inv in data['invoices'] if inv['id'] != invoice_id]
    
    if len(data['invoices']) < initial_count:
        _save_data(data)
        return f"Invoice #{invoice_id} has been successfully deleted."
    else:
        return f"Error: No invoice found with ID #{invoice_id}."

@tool()
def remove_duplicate_invoices() -> str:
    """
    Scans the database and removes invoices that have identical 
    client names, amounts, and descriptions.
    """
    data = _load_data()
    original_count = len(data['invoices'])
    
    unique_invoices = []
    seen_signatures = set()
    
    for inv in data['invoices']:
        # Create a unique 'fingerprint' for each invoice
        signature = (inv.get('client'), inv.get('amount'), inv.get('description'))
        
        if signature not in seen_signatures:
            unique_invoices.append(inv)
            seen_signatures.add(signature)
            
    # Update the file with the cleaned list
    data['invoices'] = unique_invoices
    _save_data(data)
    
    removed_count = original_count - len(unique_invoices)
    return f"Cleanup complete! Removed {removed_count} duplicate entries."