import pandas as pd
import requests
import urllib.parse
from datetime import datetime

API_BASE_URL = "https://bills-api.parliament.uk/api/v1/Bills"

def get_bill_info(bill_id):
    """
    Retrieve bill details and its progress for the given bill id.
    Uses the 'lastUpdate' field as the introduced date.
    """
    url = f"{API_BASE_URL}/{bill_id}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    
    try:
        data = response.json()
        if isinstance(data, dict):
            orig_house = data.get("originatingHouse", "N/A")
            progress_status = check_bill_progress(bill_id)
            
            sessionID = data.get("introducedSessionId", "N/A")

            introduced_date = getIntroducedDate(bill_id)
            
            
            
            return {
                "bill_id": bill_id,
                "originating_house": orig_house,
                "progress_status": progress_status,
                "sessionID": sessionID,
                "introduced_date": introduced_date
            }
    except Exception as e:
        print(f"Error processing bill id {bill_id}: {e}")
    return None



def getIntroducedDate(bill_id):
    """
    Retrieve the first date of the bill from the /Stages endpoint.
    The function sorts the stages by 'sortOrder' and returns the date
    from the first stage that has at least one 'stageSittings' entry.
    """
    stages_url = f"{API_BASE_URL}/{bill_id}/Stages"
    headers = {"accept": "application/json"}
    
    try:
        response = requests.get(stages_url, headers=headers)
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            print(f"No stages found for bill {bill_id}.")
            return None
        
        # Sort stages by sortOrder to get the first stage
        sorted_stages = sorted(items, key=lambda stage: stage.get("sortOrder", float('inf')))
        
        for stage in sorted_stages:
            stage_sittings = stage.get("stageSittings", [])
            if stage_sittings:
                # Return the date of the first stage sitting for the earliest stage
                return stage_sittings[0].get("date", None)
        
        print(f"No valid stage sitting dates found for bill {bill_id}.")
        return None
    except Exception as e:
        print(f"Error retrieving stages for bill {bill_id}: {e}")
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
            print(f"'isAct' field not found for Bill ID {bill_id}")
            return 3  
    except Exception as e:
        print(f"Error checking progress for bill id {bill_id}: {e}")
        return None

def get_first_sponsor_party(bill_id):
    """
    Retrieve the party of the first sponsor of the given bill.
    Assumes that the bill sponsors are available under the key "sponsors".
    """
    url = f"{API_BASE_URL}/{bill_id}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    
    try:
        data = response.json()
        sponsors = data.get("sponsors", [])
        if sponsors:
            sponsor_party = sponsors[0].get("member", {}).get("party", "N/A")
            return sponsor_party
        else:
            return "N/A"
    except Exception as e:
        print(f"Error retrieving sponsor info for bill id {bill_id}: {e}")
        return "N/A"

def format_date_for_api(date_str):
    """
    Convert an ISO date string (e.g., "2007-10-27T16:26:00") to the format YYYY-MM-DD.
    Truncates microseconds to 6 digits if necessary and pads with zeros when needed.
    """
    try:
        if '.' in date_str:
            date_part, micro_part = date_str.split('.', 1)
            # Remove any trailing non-digit characters (e.g., timezone info)
            micro_part = ''.join(filter(str.isdigit, micro_part))
            # Truncate to 6 digits, then pad with zeros if needed.
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
        print(f"Error: Unable to retrieve Commons data for date {for_date} (Status Code: {response.status_code})")
        return None

def collect_bill_details(bill_ids):
    """
    Loop over the unique bill IDs and collect details for each.
    """
    c =497
    results = []
    for bill_id in bill_ids[499:]:
        c +=1
        if c == 1800:
            return results
        if c %500 == 0:
            df_bills_current = pd.DataFrame(results)
            df_bills_current.to_excel(f'tempsave{c}.xlsx', index=False)
        print(f"Processing Bill ID: {bill_id}")
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
            results.append(info)
        else:
            print(f"No data for bill id {bill_id}")
    return results

def get_unique_bill_ids(files):
    """
    Read multiple CSV files and return a sorted list of unique Bill Ids.
    """
    unique_ids = set()
    for file in files:
        try:
            df = pd.read_csv(file)
            unique_ids.update(df["Bill Id"].dropna().unique())
        except Exception as e:
            print(f"Error processing file {file}: {e}")
    return sorted(unique_ids)


if __name__ == "__main__":
    # List of CSV files containing bill data
    csv_files = [
        "18_17 to 39.csv",
        "19_17 to 39.csv",
        "28_17 to 39.csv",
        "29_17 to 39.csv"
    ]
    
    # Get unique bill ids from the CSV files
    unique_bill_ids = get_unique_bill_ids(csv_files)
    print(f"Found {len(unique_bill_ids)} unique bill IDs.")

    # Collect bill details for each unique bill id
    bills_data = collect_bill_details(unique_bill_ids)
    
    # Convert the list of dictionaries to a DataFrame
    df_bills = pd.DataFrame(bills_data)
    
    # Save the details to an Excel file with a new sheet for every 500 samples
    output_excel = "collected_bills_data.xlsx"
    df_bills.to_excel(output_excel, index=False)
    
    print(f"Bill details saved to {output_excel}")