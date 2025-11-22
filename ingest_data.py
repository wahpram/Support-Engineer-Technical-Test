import os
import requests
import time
import gspread
import datetime
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

API_BASE = os.getenv("API_BASE")
SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_spreadsheets():
    """Initialize, and return Google Sheets client"""
    
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client


def fetch_and_update_data(base_url, client, limit=10):
    """Fetch data per page and update to spreadhseet"""
    
    page = 1
    total_fetched = 0
        
    try:
        spreadsheet = client.open_by_key(SPREADSHEET_KEY)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        print(f"Found existing worksheet: {WORKSHEET_NAME}")
        
        existing_data = worksheet.get_all_values()
        existing_rows = len(existing_data)
        current_row = existing_rows
            
    except gspread.WorksheetNotFound:
        print("ERROR: Worksheet not found")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to open worksheet: {e}")
        return 0
    
    while True:
        url = f"{base_url}?limit={limit}&page={page}"
        print(f"\nFetching data on page {page}...")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            items = data.get("items", [])
            if not items:
                break
            
            print(f"  Fetched {len(items)} records")
            print(f"  Updating spreadsheet...")
            
            success, rows_added = update_spreadsheets(worksheet, items, current_row)
            
            if success:
                total_fetched += rows_added
                current_row += rows_added
                print(f"  Spreadsheet updated (Total new records: {total_fetched})")
            else:
                print(f"  Failed to update spreadsheet")
                break
            
            if not data.get("hasNextPage", False):
                print("\nAll pages fetched")
                break
            
            page += 1
            time.sleep(0.5)
            
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            break
    
    return total_fetched

def get_skills(data):
    """Get skills from data"""
    skills = []
    
    attr_skills = data.get("attrSkill", []) or []
    for group in attr_skills:
        group_name = group.get("groupName", "")
        group_skills = group.get("skills", []) or []
        for skill_item in group_skills:
            skill = skill_item.get("skill", {})
            skill_name = skill.get("prettyName", "")
            if skill_name:
                skills.append(skill_name)
    
    skill_1 = skills[0] if len(skills) > 0 else ""
    skill_2 = skills[1] if len(skills) > 1 else ""
    
    return skill_1, skill_2


def get_agency(data):
    """Get agency info from data"""
    agency_name = ""
    agency_logo = ""
    agency_summary = ""
    agency_top_rated = ""
    
    extended = data.get("extendedAgencies", []) or []
    if extended:
        agency = extended[0]
        agency_name = agency.get("name", "")
        agency_logo = agency.get("logo", "") or ""
        agency_summary = agency.get("summarySanitized", "") or agency.get("summary", "") or ""
        agency_top_rated = agency.get("agencyTopRatedStatus", "") or ""
    
    if not agency_name:
        agencies = data.get("agencies", []) or []
        if agencies:
            agency_name = agencies[0].get("name", "")
    
    return agency_name, agency_logo, agency_summary, agency_top_rated


def get_services(data):
    """Get service profile from data"""
    services = data.get("serviceProfileNames", []) or []
    return ", ".join(services) if services else ""


def format_currency(amount):
    """Format currency as $XXK or $XXX"""
    if not amount:
        return ""
    try:
        amt = float(amount)
        if amt >= 1000:
            return f"${int(amt/1000)}K"
        return f"${int(amt)}"
    except:
        return ""
    
    
def format_member_since(member_since):
    """Format member since date"""
    if not member_since:
        return "", ""
    
    try:
        dt = datetime.strptime(member_since, "%B %d, %Y")
        formatted = dt.strftime("%d/%m/%Y")
        display = dt.strftime(" %B %Y")
        return formatted, display
    except:
        return member_since, member_since


def get_location_country(data):
    """Get country from location"""
    country = data.get("location", {}) or {}
    return country.get("country", "")


def transform_data(data):
    """Transform API data to spreadsheet row format"""
    
    # Extract ciphertext
    ciphertext = data.get("ciphertext", "")
    ciphertext_clean = ciphertext.replace("~", "") if ciphertext else ""
    
    # Build Upwork profile URL
    portrait_url = data.get("portrait", "")
    
    # Agency info
    agency_name, agency_logo, agency_summary, agency_top_rated = get_agency(data)
    
    # Skills from agency
    skill1, skill2 = get_skills(data)
    
    # Member since formatting
    member_since_raw = data.get("memberSince", "")
    member_since_formatted, member_since_display = format_member_since(member_since_raw)
    
    # Currency formatting
    combined_total_revenue = data.get("combinedTotalRevenue", "")
    combined_recent_earnings = data.get("combinedRecentEarnings", "")
    
    # Clean description
    description = data.get("description", "") or ""
    description = description.replace("&amp;", "&")
    
    # Create row data match on spreadhseet rows
    row = {
        "TEMP08-ciphertext": ciphertext,
        "Do Not Delete": ciphertext_clean,
        "TEMP09-shortName": data.get("shortName", ""),
        "TEMP12-companyFullName": agency_name,
        "TEMP15-upworkUrl": portrait_url,
        "Status": "RAW",
        "Date": datetime.now().strftime("%d-%m-%Y"),
        "First name": "",
        "Last name": "",
        "Freelancer": False,
        "Email": "",
        "Phone": "",
        "Company Phone": "",
        "Job Title": data.get("title", ""),
        "PD11-Department": "",
        "PD12-Seniority-Level": "",
        "PD13-Persona": "",
        "PC01-Company-Short": "",
        "PC02-CompanyS": "",
        "PC06-2nd-person-full": "",
        "PC07-2nd-person-first": "",
        "PC08-Website": "",
        "PD06-Company-Country": get_location_country(data),
        "PC10-Company-Linkedin": "",
        "PD01-Prospect-Linkedin": "",
        "Source URL": "",
        "PD07-Industry": "",
        "PD09-Company-Size": "",
        "UN01-Solutions": "",
        "PD16-SignOff": "",
        "PD17-SignOffForward": "",
        "PD10-Daytime": "",
        "PC03-Client1": "",
        "PC04-Client2": "",
        "PC05-Client3": "",
        "PD02-combinedTotalRevenue": format_currency(combined_total_revenue),
        "PD03-totalHourlyJobs": data.get("totalHourlyJobs", ""),
        "PD14-combinedRecentEarnings": format_currency(combined_recent_earnings),
        "TEMP01-workingYears": data.get("workingYears", ""),
        "TEMP02-avgDeadlinesScore": data.get("avgDeadlinesScore", ""),
        "TEMP03-serviceProfileNames": get_services(data),
        "TEMP04-agencyTopRatedStatus": data.get("topRatedStatus", "") or agency_top_rated,
        "TEMP05-summarySanitized": agency_summary,
        "TEMP06-skill1": skill1,
        "TEMP07-skill2": skill2,
        "TEMP10-memberSince": member_since_formatted,
        "PD20-memberSince": member_since_display,
        "TEMP11-combinedRecentEarnings": format_currency(combined_recent_earnings),
        "TEMP13-combinedTotalRevenue": format_currency(combined_total_revenue),
        "TEMP14-description": description,
        "TEMP15-avgFeedbackscore": data.get("avgFeedbackScore", ""),
        "PD18-companyLogo": agency_logo or "",
        "PC09-Owner": "",
        "PD08-Research-Campaign": "",
        "TEMP16-Created": datetime.now().strftime("%d/%m/%Y"),
        "Last Modified Date & TIme": "",
    }
    
    return row


def get_headers():
    """Return spreadsheet headers"""
    
    return [
        "TEMP08-ciphertext", "Do Not Delete", "TEMP09-shortName", 
        "TEMP12-companyFullName", "TEMP15-upworkUrl", "Status", "Date",
        "First name", "Last name", "Freelancer", "Email", "Phone", 
        "Company Phone", "Job Title", "PD11-Department", "PD12-Seniority-Level",
        "PD13-Persona", "PC01-Company-Short", "PC02-CompanyS", 
        "PC06-2nd-person-full", "PC07-2nd-person-first", "PC08-Website",
        "PD06-Company-Country", "PC10-Company-Linkedin", "PD01-Prospect-Linkedin",
        "Source URL", "PD07-Industry", "PD09-Company-Size", "UN01-Solutions",
        "PD16-SignOff", "PD17-SignOffForward", "PD10-Daytime",
        "PC03-Client1", "PC04-Client2", "PC05-Client3",
        "PD02-combinedTotalRevenue", "PD03-totalHourlyJobs", 
        "PD14-combinedRecentEarnings", "TEMP01-workingYears",
        "TEMP02-avgDeadlinesScore", "TEMP03-serviceProfileNames",
        "TEMP04-agencyTopRatedStatus", "TEMP05-summarySanitized",
        "TEMP06-skill1", "TEMP07-skill2", "TEMP10-memberSince",
        "PD20-memberSince", "TEMP11-combinedRecentEarnings",
        "TEMP13-combinedTotalRevenue", "TEMP14-description",
        "TEMP15-avgFeedbackscore", "PD18-companyLogo", "PC09-Owner",
        "PD08-Research-Campaign", "TEMP16-Created", "Last Modified Date & TIme"
    ]
    
    
def add_status_dropdown(worksheet, start_row, num_rows):
    """Add dropdown validation to Status column"""
    try:
        end_row = start_row + num_rows - 1
        
        # Define status options
        status_options = ['RAW', 'READY', 'UPL', 'NOT FOUND', 'NDM', 'DONE', 'ONLY LINKEDIN', 'DUPLICATE', 'EMAIL NOT FOUND']
        
        # Create validation rule
        validation_rule = {
            'requests': [{
                'setDataValidation': {
                    'range': {
                        'sheetId': worksheet.id,
                        'startRowIndex': start_row - 1,
                        'endRowIndex': end_row,
                        'startColumnIndex': 5,
                        'endColumnIndex': 6
                    },
                    'rule': {
                        'condition': {
                            'type': 'ONE_OF_LIST',
                            'values': [{'userEnteredValue': option} for option in status_options]
                        },
                        'showCustomUi': True,
                        'strict': True
                    }
                }
            }]
        }
        
        worksheet.spreadsheet.batch_update(validation_rule)
        
    except Exception as e:
        print(f"  Warning: Could not add dropdown validation: {e}")


def update_spreadsheets(worksheet, data, current_row):
    """Update data in Google Spreadsheet with data from API"""
    try:
        headers = get_headers()
        rows = []
        
        for d in data:
            transformed = transform_data(d)
            row = [str(transformed.get(h, "")) for h in headers]
            rows.append(row)
        
        if rows:
            start_row = current_row + 1
            range_name = f'A{start_row}'
            worksheet.update(range_name=range_name, values=rows)
            add_status_dropdown(worksheet, start_row, len(rows))
            print(f"  Added {len(rows)} rows starting at row {start_row}")
            return True, len(rows)
        
        return True, 0
        
    except Exception as e:
        print(f"  Error appending to spreadsheet: {e}")
        return False, 0


def main():
    """Main function"""
    print("=" * 60)
    print("Data Ingestion")
    print("=" * 60)
    print(f"API Base: {API_BASE}")
    print(f"Spreadsheet Key: {SPREADSHEET_KEY}")
    print(f"Worksheet: {WORKSHEET_NAME}")
    print("=" * 60)
    
    if not SPREADSHEET_KEY:
        print("ERROR: SPREADSHEET_KEY not set in environment")
        return
    
    print("\nInitializing Google Sheets client...")
    client = get_spreadsheets()

    total_data = fetch_and_update_data(API_BASE, client)
    
    if not total_data:
        print("No data found!")
        return
    
    print(f"\nTotal data fetched: {total_data}")
    
    print("\n" + "=" * 60)
    print("Ingestion complete!")
    print("=" * 60)
     
     
if __name__ == "__main__":
    main()