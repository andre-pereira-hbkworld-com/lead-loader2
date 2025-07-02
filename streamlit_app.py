import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

HUBSPOT_ACCESS_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN', 'YOUR_HUBSPOT_ACCESS_TOKEN')
HUBSPOT_BASE_URL = 'https://api.hubapi.com'
REQUESTS_VERIFY = False  # Disable SSL verification for testing
st.write("Token loaded:", bool(HUBSPOT_ACCESS_TOKEN and HUBSPOT_ACCESS_TOKEN != 'YOUR_HUBSPOT_ACCESS_TOKEN'))
st.write("Token preview:", HUBSPOT_ACCESS_TOKEN[:6] if HUBSPOT_ACCESS_TOKEN else "None")

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
        contact_id = contact['id']
        resp = requests.patch(f"{url}/{contact_id}", headers=hubspot_headers(), json=data, verify=REQUESTS_VERIFY)
    else:
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

st.title("Hubspot Integration Test App")

st.header("Find Contact by Email")
email = st.text_input("Email to search")
if st.button("Find Contact"):
    try:
        contact = find_contact_by_email(email)
        st.write(contact if contact else "No contact found.")
    except Exception as e:
        st.error(str(e))

st.header("Create or Update Contact")
with st.form("create_update_contact"):
    email2 = st.text_input("Email", key="email2")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    company = st.text_input("Company")
    phone = st.text_input("Phone")
    submitted = st.form_submit_button("Create/Update Contact")
    if submitted:
        lead = {
            'Email': email2,
            'First Name': first_name,
            'Last Name': last_name,
            'Company': company,
            'Phone': phone
        }
        try:
            result = create_or_update_contact(lead)
            st.success(f"Contact created/updated: {result}")
        except Exception as e:
            st.error(str(e))

st.header("Enroll Contact in Workflow")
with st.form("enroll_workflow"):
    contact_id = st.text_input("Contact ID")
    workflow_id = st.text_input("Workflow ID")
    submitted2 = st.form_submit_button("Enroll Contact")
    if submitted2:
        try:
            enrolled = enroll_in_workflow(contact_id, workflow_id)
            if enrolled:
                st.success("Enrolled in workflow.")
            else:
                st.error("Failed to enroll.")
        except Exception as e:
            st.error(str(e))

st.header("Create Deal for Contact")
with st.form("create_deal"):
    contact_id2 = st.text_input("Contact ID for Deal")
    deal_props_str = st.text_area("Deal Properties (key=value, one per line)")
    submitted3 = st.form_submit_button("Create Deal")
    if submitted3:
        deal_props = {}
        for line in deal_props_str.splitlines():
            if '=' in line:
                k, v = line.split('=', 1)
                deal_props[k.strip()] = v.strip()
        try:
            deal = create_deal_for_contact(contact_id2, deal_props)
            st.success(f"Deal created: {deal}")
        except Exception as e:
            st.error(str(e))
