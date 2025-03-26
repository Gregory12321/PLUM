import requests
import urllib.parse
from datetime import datetime

API_BASE_URL = "https://bills-api.parliament.uk/api/v1/Bills"

def get_bill_info(bill_id):
    """
    Retrieve bill details and its progress for the given bill id.
    Uses the first stage sitting date from current stage as the introduced date.
    """
    url = f"{API_BASE_URL}/{bill_id}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    
    try:
        data = response.json()
        if isinstance(data, dict):
            long_title = data.get("longTitle", "N/A")
            short_title = data.get("shortTitle", "N/A")
            orig_house = data.get("originatingHouse", "N/A")
            progress_status = check_bill_progress(bill_id)
            sessionID = data.get("introducedSessionId", "N/A")
            
            # Extract the introduced date from the first stage sitting in currentStage
            introduced_date = None
            current_stage = data.get("currentStage", None)
            if current_stage:
                stage_sitting = current_stage.get("stageSitting", None)
                if stage_sitting and isinstance(stage_sitting, list) and len(stage_sitting) > 0:
                    introduced_date = stage_sitting[0].get("date", None)
            
            return {
                "bill_id": bill_id,
                "long_title": long_title,
                "short_title": short_title,
                "originating_house": orig_house,
                "progress_status": progress_status,
                "sessionID": sessionID,
                "introduced_date": introduced_date
            }
    except Exception as e:
        print(f"Error processing bill id {bill_id}: {e}")
    return None

def check_bill_progress(bill_id):
    url = f"{API_BASE_URL}/{bill_id}"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    try:
        data = response.json()
        if 'isAct' in data:
            return 2 if data['isAct'] else 1
        else:
            return 3  
    except Exception as e:
        print(f"Error checking progress for bill id {bill_id}: {e}")
        return None

def get_first_sponsor_party(bill_id):
    """
    Retrieve the party of the first sponsor of the given bill.
    """
    url = f"{API_BASE_URL}/{bill_id}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    
    try:
        data = response.json()
        sponsors = data.get("sponsors", [])
        if sponsors:
            return sponsors[0].get("member", {}).get("party", "N/A")
        else:
            return "N/A"
    except Exception as e:
        print(f"Error retrieving sponsor info for bill id {bill_id}: {e}")
        return "N/A"

def format_date_for_api(date_str):
    """
    Convert an ISO date string (e.g., "2007-10-27T16:26:00") to the format YYYY-MM-DD.
    """
    try:
        if '.' in date_str:
            date_part, micro_part = date_str.split('.', 1)
            micro_part = ''.join(filter(str.isdigit, micro_part))
            micro_part = micro_part[:6]
            if len(micro_part) < 6:
                micro_part = micro_part.ljust(6, '0')
            new_date_str = f"{date_part}.{micro_part}"
        else:
            new_date_str = date_str
        
        dt = datetime.fromisoformat(new_date_str)
    except Exception as e:
        print("Error parsing date:", e)
        return None
    return dt.strftime("%Y-%m-%d")

def get_commons_seat_counts(for_date):
    """
    Retrieve the state of the parties in the House of Commons on a given date,
    returning a dictionary mapping party names to seat counts.
    """
    base_url = "https://members-api.parliament.uk/api/Parties/StateOfTheParties"
    encoded_date = urllib.parse.quote(for_date)
    url = f"{base_url}/commons/{encoded_date}"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        party_seat_counts = {}
        for item in items:
            value = item.get("value", {})
            party_info = value.get("party", {})
            party_name = party_info.get("name", "Unknown")
            total_seats = value.get("total", 0)
            party_seat_counts[party_name] = total_seats
        return party_seat_counts
    else:
        return None

if __name__ == "__main__":
    bill_id = input("Enter a specific bill ID: ").strip()
    print(f"\nProcessing Bill ID: {bill_id}\n")
    info = get_bill_info(bill_id)
    
    if info is not None:
        sponsor_party = get_first_sponsor_party(bill_id)
        info["sponsor_party"] = sponsor_party
        
        if info["introduced_date"]:
            formatted_date = format_date_for_api(info["introduced_date"])
            info["formatted_date"] = formatted_date
            seat_counts = get_commons_seat_counts(formatted_date) if formatted_date else None
            info["seat_counts"] = seat_counts
        else:
            info["formatted_date"] = None
            info["seat_counts"] = None
        
        print("Bill Information:")
        for key, value in info.items():
            print(f"{key}: {value}")
    else:
        print("No data found for bill ID:", bill_id)
