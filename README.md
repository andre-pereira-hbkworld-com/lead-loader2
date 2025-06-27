# Lead Loader

This project is a Python automation tool to help users upload tradeshow leads from an Excel template into Hubspot. It will:

- Allow users to select and upload an Excel file.
- Use the Hubspot API to create new contacts and update existing ones based on email matching.
- Enroll all contacts in a predefined Hubspot workflow to create deals.
- Retrieve the resulting deals/MQLs and validate them against business rules.
- Output an Excel report listing any rule violations and instructions for fixing them in Hubspot.

## Requirements
- Python 3.8+
- Open source libraries only (e.g., pandas, openpyxl, requests)
- Hubspot API key or OAuth credentials

## Setup
1. Install Python 3.8 or higher.
2. (Recommended) Create a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage
1. Run the app:
   ```powershell
   python app.py
   ```
2. Follow the prompts to select your Excel file and process leads.

## Notes
- All code and dependencies are open source and free.
- The app will provide clear error messages and documentation for users.
