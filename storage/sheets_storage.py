import os
import pandas as pd
import gspread
from config import SERVICE_ACCOUNT_FILE, GOOGLE_SHEET_NAME

def get_gspread_client():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"⚠️ Service account file '{SERVICE_ACCOUNT_FILE}' not found. Google Sheets sync disabled.")
        return None
    try:
        client = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
        return client
    except Exception as e:
        print(f"⚠️ Failed to connect to Google Sheets API: {e}")
        return None

def save_jobs_to_sheets(jobs_data: list[dict], sheet_name: str = GOOGLE_SHEET_NAME) -> bool:
    """
    Saves or appends structured job records to Google Sheets.
    """
    client = get_gspread_client()
    if not client:
        return False

    try:
        # Open or create spreadsheet
        try:
            sh = client.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            sh = client.create(sheet_name)

        worksheet = sh.sheet1

        # Check if headers exist
        existing_records = worksheet.get_all_values()
        headers = ["Title", "Company", "Location", "Match Score", "Tech Stack", "Fit Summary", "Job URL"]

        if not existing_records:
            worksheet.append_row(headers)

        rows_to_add = []
        for j in jobs_data:
            rows_to_add.append([
                j.get("title", "N/A"),
                j.get("company", "N/A"),
                j.get("location", "N/A"),
                j.get("match_score", 0),
                ", ".join(j.get("tech_stack", [])),
                j.get("fit_summary", ""),
                j.get("job_url", "")
            ])

        if rows_to_add:
            worksheet.append_rows(rows_to_add)
            print(f"✅ Saved {len(rows_to_add)} records to Google Sheet: {sheet_name}")
            return True
    except Exception as e:
        print(f"⚠️ Failed to write to Google Sheet: {e}")
        return False
    return False
