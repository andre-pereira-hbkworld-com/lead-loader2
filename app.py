import pandas as pd
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants for Hubspot API
# Use a Hubspot Private App Access Token (recommended)
HUBSPOT_ACCESS_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN', 'YOUR_HUBSPOT_ACCESS_TOKEN')
HUBSPOT_BASE_URL = 'https://api.hubapi.com'

# Excel template columns expected
REQUIRED_COLUMNS = ['First Name', 'Last Name', 'Email', 'Company', 'Phone']

# Business rules for deal validation (example)
DEAL_RULES = [
    lambda deal: deal.get('amount', 0) > 0 or 'Deal amount must be greater than 0',
    lambda deal: deal.get('dealstage') == 'qualifiedtobuy' or 'Deal must be in qualifiedtobuy stage',
]

def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title='Select Excel File',
        filetypes=[('Excel Files', '*.xlsx *.xls')]
    )
    return file_path

def load_excel(file_path):
    df = pd.read_excel(file_path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    return df

# --- Hubspot API Integration ---
# Disable SSL verification for all requests (not recommended for production)
REQUESTS_VERIFY = False

def hubspot_headers():
    return {
        'Authorization': f'Bearer {HUBSPOT_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

def find_contact_by_email(email):
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/search"
    payload = {
        "filterGroups": [
            {"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}
        ],
        "properties": ["email", "firstname", "lastname", "company", "phone"]
    }
    resp = requests.post(url, headers=hubspot_headers(), json=payload, verify=REQUESTS_VERIFY)
    resp.raise_for_status()
    results = resp.json().get('results', [])
    return results[0] if results else None

def create_or_update_contact(lead):
    contact = find_contact_by_email(lead['Email'])
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts"
    data = {
        "properties": {
            "email": lead['Email'],
            "firstname": lead['First Name'],
            "lastname": lead['Last Name'],
            "company": lead['Company'],
            "phone": str(lead['Phone'])
        }
    }
    if contact:
        # Update
        contact_id = contact['id']
        resp = requests.patch(f"{url}/{contact_id}", headers=hubspot_headers(), json=data, verify=REQUESTS_VERIFY)
    else:
        # Create
        resp = requests.post(url, headers=hubspot_headers(), json=data, verify=REQUESTS_VERIFY)
    resp.raise_for_status()
    return resp.json()

def enroll_in_workflow(contact_id, workflow_id):
    url = f"{HUBSPOT_BASE_URL}/automation/v3/workflows/{workflow_id}/enrollments/contacts/{contact_id}"
    resp = requests.post(url, headers=hubspot_headers(), verify=REQUESTS_VERIFY)
    resp.raise_for_status()
    return resp.status_code == 204

def create_deal_for_contact(contact_id, deal_props):
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/deals"
    data = {
        "properties": deal_props,
        "associations": [{
            "to": {"id": contact_id},
            "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 3}]
        }]
    }
    resp = requests.post(url, headers=hubspot_headers(), json=data, verify=REQUESTS_VERIFY)
    resp.raise_for_status()
    return resp.json()
# --- End Hubspot API Integration ---

def test_hubspot_functions():
    print("\n--- Hubspot Integration Test Menu ---")
    print("1. Find contact by email")
    print("2. Create or update contact")
    print("3. Enroll contact in workflow")
    print("4. Create deal for contact")
    print("5. Exit test menu")
    while True:
        choice = input("\nSelect an option (1-5): ").strip()
        if choice == '1':
            email = input("Enter email to search: ").strip()
            try:
                contact = find_contact_by_email(email)
                print("Result:", contact if contact else "No contact found.")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '2':
            lead = {
                'Email': input("Email: ").strip(),
                'First Name': input("First Name: ").strip(),
                'Last Name': input("Last Name: ").strip(),
                'Company': input("Company: ").strip(),
                'Phone': input("Phone: ").strip()
            }
            try:
                result = create_or_update_contact(lead)
                print("Contact created/updated:", result)
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '3':
            contact_id = input("Contact ID: ").strip()
            workflow_id = input("Workflow ID: ").strip()
            try:
                enrolled = enroll_in_workflow(contact_id, workflow_id)
                print("Enrolled in workflow." if enrolled else "Failed to enroll.")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '4':
            contact_id = input("Contact ID: ").strip()
            deal_props = {}
            print("Enter deal properties (key=value), blank line to finish:")
            while True:
                line = input()
                if not line.strip():
                    break
                if '=' in line:
                    k, v = line.split('=', 1)
                    deal_props[k.strip()] = v.strip()
            try:
                deal = create_deal_for_contact(contact_id, deal_props)
                print("Deal created:", deal)
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '5':
            print("Exiting test menu.")
            break
        else:
            print("Invalid option. Please select 1-5.")

if __name__ == "__main__":
    # Run the test menu for Hubspot integration
    test_hubspot_functions()
    # Exit after test menu to avoid running the rest of the script
    exit(0)
    try:
        file_path = select_file()
        if not file_path:
            print("No file selected.")
            exit(0)
        leads_df = load_excel(file_path)
        print(f"Loaded {len(leads_df)} leads from {file_path}")
        # TODO: Add Hubspot API integration, contact/deal creation, workflow enrollment, validation, and reporting
    except Exception as e:
        messagebox.showerror("Error", str(e))
        print(f"Error: {e}")
