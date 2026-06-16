# import modules
import requests
import json
from datetime import datetime, timedelta
import time # Import time module for delays

today = datetime.now()
tomorrow = today + timedelta(days=1)
tomorrow = tomorrow.strftime("%Y-%m-%d")
today = today.strftime("%Y-%m-%d")

# Specify the list of user IDs you want to process
USER_IDS = [15534828, 39123148] # Example User IDs. You can add more here.
MODE = 0 # Standard Mode

# Function to process each user
def process_user_update(user_id, mode):
    print(f"\nProcessing update for User ID: {user_id}")

    # set url parameters as a dictionary
    url_params = {'user': user_id, 'mode': mode, 'from': today, 'to': tomorrow}

    # data dictionary is still being sent as json.
    data = {'key': 'value'}

    # send update request to API
    response = requests.post('https://osutrack-api.ameo.dev/update', json=data, params=url_params)
    notimestamp = True

    # Handling the Response
    if response.status_code == 200:
        print(f"Request successful with status code: {response.status_code}")
        jsonout = response.json()

        # Find the latest date
        if notimestamp == True:
          for key, value in jsonout.items():
            print(f"{key}: {value}")
        elif notimestamp == False:
          # This branch might not be reached for 'update' calls if notimestamp is always True
          # but kept for consistency if logic changes later.
          latest_date = max(item['timestamp'] for item in jsonout) # Find the maximum date
          latest_data = next(item for item in jsonout if item['timestamp'] == latest_date)
          for key, value in latest_data.items():
            print(f"{key}: {value}")
        else:
          print(json.dumps(jsonout, indent=4))

    else:
        print(f"Request failed for User ID {user_id} with status code: {response.status_code}")
        print(f"Response content: {response.text}")

# Loop through the list of user IDs and process each one
for user_id in USER_IDS:
    process_user_update(user_id, MODE)
    # Add a delay to avoid hitting rate limits on the API
    print("Waiting for 5 seconds before next request...")
    time.sleep(5)

print("\nAll specified user IDs have been processed.")
