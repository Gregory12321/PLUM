import requests
import urllib.parse
from datetime import datetime

API_BASE_URL = "https://bills-api.parliament.uk/api/v1/Bills"

def get_bill_info(bill_id):
    """
    Retrieve bill details and its progress for the given bill number.
    Expects the bill details JSON to include an 'introducedDate' (or 'lastUpdate') field.
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
            # Retrieve progress status via get_bill_progress (i.e. check_bill_progress)
            progress_status = check_bill_progress(bill_id)
            # For this example, use the 'lastUpdate' as the introduced date.
            introduced_date = data.get("lastUpdate", None)
            sessionID = data.get("introducedSessionId", "N/A")
            
            return bill_id, long_title, short_title, orig_house, progress_status, sessionID, introduced_date
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Response for Bill ID {bill_id} is not valid JSON. Response:", response.text)
        return None

    except requests.exceptions.JSONDecodeError:
        print(f"Error: Response for Bill ID {bill_id} is not valid JSON. Response:", response.text)
        return False

def format_date_for_api(date_str):
    """
    Convert an ISO date string (e.g., "2007-10-27T16:26:00") to the format YYYY-MM-DD.
    """
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", ""))
    except Exception as e:
        print("Error parsing date:", e)
        return None
    return dt.strftime("%Y-%m-%d")

def get_first_sponsor_party(bill_id):
    """
    Retrieve the party of the first sponsor of the given bill.
    
    Assumes that the bill sponsors are available via the endpoint:
    /api/v1/Bills/{bill_id}/Sponsors and that the first sponsor's party
    is available under the key path: value -> sponsorParty -> name.
    """
    url = f"{API_BASE_URL}/{bill_id}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    
    try:
        data = response.json()
        sponsor = data.get("sponsors",[])
        if not sponsor:
            print("No sponsors found for the bill.")
            return None
        
        
        # Get the first sponsor
        sponsor_party = sponsor[0]["member"]["party"]
        
        if sponsor_party:
            return sponsor_party
        else:
            print("Sponsor party information not available.")
            return None
    except Exception as e:
        print("Error retrieving sponsor info:", e)
        return None


def get_commons_seat_counts(for_date):
    """
    Retrieve the state of the parties in the House of Commons on a given date,
    returning a dictionary mapping party names to the total number of seats.
    
    Uses the endpoint: /api/Parties/StateOfTheParties/commons/{forDate}
    where for_date must be URL encoded.
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
        print(f"Error: Unable to retrieve Commons data (Status Code: {response.status_code})")
        print("Response:", response.text)
        return None

def check_bill_progress(bill_id):
    """Checks if a bill is an act using the isAct field from the API."""
    url = f"https://bills-api.parliament.uk/api/v1/Bills/{bill_id}"  
    headers = {"accept": "application/json"}  
    
    response = requests.get(url, headers=headers)

    try:
        data = response.json()  
        if 'isAct' in data:
            return 2 if data['isAct'] else 1
        else:
            print(f"'isAct' field not found for Bill ID {bill_id}")
            return 3  

    except requests.exceptions.JSONDecodeError:
        print(f"Error: Response for Bill ID {bill_id} is not valid JSON. Response:", response.text)
        return False

bill_number = input("Enter bill number: ")

bill_details = get_bill_info(bill_number)
sponsor_party = get_first_sponsor_party(bill_number)
if sponsor_party:
    print(f"First Sponsor's Party: {sponsor_party}")
else:
    print("No sponsor party information available.")

if bill_details:
    bill_id, long_title, short_title, orig_house, progress_status, sessionID, introduced_date = bill_details
    print(f"\nBill ID: {bill_id}")
    print(f"Long Title: {long_title}")
    print(f"Short Title: {short_title}")
    print(f"Originating House: {orig_house}")
    print(f"Progress Status: {progress_status}")
    print(f"Introduced Session ID: {sessionID}")
    
    if introduced_date:
        print(f"Introduced Date (raw): {introduced_date}")
        # Format the date to YYYY-MM-DD (i.e. remove the time)
        formatted_date = format_date_for_api(introduced_date)
        if formatted_date:
            print(f"Formatted Date for Commons API: {formatted_date}")
            seat_counts = get_commons_seat_counts(formatted_date)
            if seat_counts:
                print("\nHouse of Commons Seat Counts on that day:")
                for party, seats in seat_counts.items():
                    print(f"{party}: {seats} seats")
            else:
                print("No seat data available for that day.")
        else:
            print("Failed to format the introduced date.")
    else:
        print("Introduced date not available in bill data.")
else:
    print("Bill information not available.")
    



import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

labour_seats = 353
conservative_seats = 196
libdem_seats = 63
sponsor_party = "Labour"
progress_status = 2       

sample_features = {
    "Labour_seats": labour_seats,
    "Conservative_seats": conservative_seats,
    "LibDem_seats": libdem_seats,
    "Sponsor_party": sponsor_party,
    "Progress_Status": progress_status  
}

data = [
    {"Labour_seats": 353, "Conservative_seats": 196, "LibDem_seats": 63, 
     "Sponsor_party": "Labour", "Progress_Status": 2},
    {"Labour_seats": 350, "Conservative_seats": 200, "LibDem_seats": 60, 
     "Sponsor_party": "Conservative", "Progress_Status": 0},
    {"Labour_seats": 360, "Conservative_seats": 190, "LibDem_seats": 65, 
     "Sponsor_party": "Labour", "Progress_Status": 2},
    {"Labour_seats": 340, "Conservative_seats": 210, "LibDem_seats": 55, 
     "Sponsor_party": "Liberal Democrat", "Progress_Status": 0},
    {"Labour_seats": 355, "Conservative_seats": 195, "LibDem_seats": 62, 
     "Sponsor_party": "Labour", "Progress_Status": 1},
    {"Labour_seats": 348, "Conservative_seats": 202, "LibDem_seats": 58, 
     "Sponsor_party": "Conservative", "Progress_Status": 0},
]

df = pd.DataFrame(data)

X = df.drop("Progress_Status", axis=1)
y = df["Progress_Status"]

X_encoded = pd.get_dummies(X, columns=["Sponsor_party"], drop_first=True)
print("Encoded Features:")
print(X_encoded)

X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.25, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

sample_df = pd.DataFrame([{
    "Labour_seats": sample_features["Labour_seats"],
    "Conservative_seats": sample_features["Conservative_seats"],
    "LibDem_seats": sample_features["LibDem_seats"],
    "Sponsor_party": sample_features["Sponsor_party"]
}])

sample_encoded = pd.get_dummies(sample_df, columns=["Sponsor_party"], drop_first=True)

for col in X_encoded.columns:
    if col not in sample_encoded.columns:
        sample_encoded[col] = 0
sample_encoded = sample_encoded[X_encoded.columns] 

prediction = model.predict(sample_encoded)
print("\nPrediction for the sample (Progress Status):", prediction[0])


import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

np.random.seed(42)

def assign_progress_status(sponsor_party):
    if sponsor_party == "Labour":
        return 2
    else:
        return 0

n_samples = 1000
sponsor_choices = ["Labour", "Conservative", "Liberal Democrat"]

train_data = []
for _ in range(n_samples):
    sponsor_party = np.random.choice(sponsor_choices)
    labour_seats = np.random.normal(350, 10)  
    conservative_seats = np.random.normal(200, 10)  
    libdem_seats = np.random.normal(60, 5) 
    
    progress_status = assign_progress_status(sponsor_party)
    
    train_data.append({
        "Labour_seats": int(round(labour_seats)),
        "Conservative_seats": int(round(conservative_seats)),
        "LibDem_seats": int(round(libdem_seats)),
        "Sponsor_party": sponsor_party,
        "Progress_Status": progress_status
    })

df_train = pd.DataFrame(train_data)

X_train = df_train.drop("Progress_Status", axis=1)
y_train = df_train["Progress_Status"]

X_train_encoded = pd.get_dummies(X_train, columns=["Sponsor_party"], drop_first=True)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_encoded, y_train)


test_data = []
for _ in range(10000):
    sponsor_party = np.random.choice(sponsor_choices)
    labour_seats = np.random.normal(350, 10)
    conservative_seats = np.random.normal(200, 10)
    libdem_seats = np.random.normal(60, 5)
    
    progress_status = assign_progress_status(sponsor_party)
    
    test_data.append({
        "Labour_seats": int(round(labour_seats)),
        "Conservative_seats": int(round(conservative_seats)),
        "LibDem_seats": int(round(libdem_seats)),
        "Sponsor_party": sponsor_party,
        "Progress_Status": progress_status
    })


outlier = {
    "Labour_seats": 400,  
    "Conservative_seats": 180,
    "LibDem_seats": 70,
    "Sponsor_party": "Labour",
    "Progress_Status": 0  
}
test_data.append(outlier)

df_test = pd.DataFrame(test_data)

X_test = df_test.drop("Progress_Status", axis=1)
y_test = df_test["Progress_Status"]

X_test_encoded = pd.get_dummies(X_test, columns=["Sponsor_party"], drop_first=True)

for col in X_train_encoded.columns:
    if col not in X_test_encoded.columns:
        X_test_encoded[col] = 0
X_test_encoded = X_test_encoded[X_train_encoded.columns] 

predictions = model.predict(X_test_encoded)

df_test["Predicted_Progress_Status"] = predictions

print("Test Samples Evaluation:")
print(df_test)
print("\nAccuracy on test samples: {:.2f}%".format(accuracy_score(y_test, predictions) * 100))



import requests
import urllib.parse
import pandas as pd
from datetime import datetime

API_BASE_URL = "https://bills-api.parliament.uk/api/v1/Bills"

def get_bill_info(bill_id):
    """
    Retrieve bill details and its progress for the given bill number.
    Uses the 'lastUpdate' field as the introduced date.
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
            introduced_date = data.get("lastUpdate", None)
            sessionID = data.get("introducedSessionId", "N/A")
            
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
    """
    Checks if a bill has failed to progress by searching news articles.
    Returns:
        1 if phrases indicating no further progress are found,
        2 if phrases indicating the bill is now an Act of Parliament are found,
        3 otherwise.
    """
    url = f"{API_BASE_URL}/{bill_id}/NewsArticles"
    headers = {"accept": "text/plain"}
    
    response = requests.get(url, headers=headers)
    try:
        data = response.json()
        if not isinstance(data, dict) or "items" not in data:
            print(f"Unexpected response format for Bill ID {bill_id}: {data}")
            return None
        
        phrase = "bill will make no further progress"
        phrase2 = "bill is now an Act of Parliament"
        phrase3 = "not progress any further"
        
        for article in data.get("items", []):
            content = article.get("content", "").upper()
            if phrase.upper() in content:
                return 1
            if phrase2.upper() in content:
                return 2
            if phrase3.upper() in content:
                return 1
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
            return None
    except Exception as e:
        print(f"Error retrieving sponsor info for bill id {bill_id}: {e}")
        return None

def format_date_for_api(date_str):
    """
    Convert an ISO date string (e.g., "2007-10-27T16:26:00") to the format YYYY-MM-DD.
    """
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", ""))
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

def collect_bills_data(start_id, end_id):
    """
    Loop over a range of bill IDs and collect their information.
    Returns a list of dictionaries with bill data.
    """
    results = []
    for bill_id in range(start_id, end_id + 1):
        info = get_bill_info(bill_id)
        if info is not None:
            sponsor_party = get_first_sponsor_party(bill_id)
            info["sponsor_party"] = sponsor_party if sponsor_party else "N/A"
            if info["introduced_date"]:
                formatted_date = format_date_for_api(info["introduced_date"])
                info["formatted_date"] = formatted_date
                seat_counts = get_commons_seat_counts(formatted_date)
                info["seat_counts"] = seat_counts
            else:
                info["formatted_date"] = None
                info["seat_counts"] = None
            results.append(info)
        else:
            print(f"No data for bill id {bill_id}")
    return results

if __name__ == "__main__":
    bills_data = collect_bills_data(1, 1000)
    
    df = pd.DataFrame(bills_data)
    print(df.head())
    
    df.to_csv("bills_data.csv", index=False)
