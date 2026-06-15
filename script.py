import json
import time
import requests

# Fixed URL: No trailing slash, as requested by the source routing
BASE_URL = "https://ameo.dev"

USER_IDS_TO_UPDATE = [15534828, 39123148]
GAME_MODE = 0  # 0 = Standard osu!

def update_osutrack_user(user_id, mode=0):
    params = {"user": user_id, "mode": mode}
    
    # Adding a custom User-Agent ensures the server doesn't block GitHub's automated traffic
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) osu-track-updater"
    }

    try:
        print(f"🔄 Triggering update for User ID: {user_id}...")
        
        # Switched to a clean GET request based on the internal API routing structures
        response = requests.get(BASE_URL, params=params, headers=headers)

        # Handle rate-limiting gracefully
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 15)
            print(f"⚠️ Rate limit hit. Waiting {retry_after} seconds...")
            time.sleep(int(retry_after))
            return update_osutrack_user(user_id, mode)

        # If it returns an unexpected error code, print out the raw text for clear debugging
        if response.status_code != 200:
            print(f"❌ Server returned status code {response.status_code}. Raw response text: {response.text[:200]}")
            return None

        # Safe JSON decoding
        data = response.json()

        # Handle formatting errors if the server sends back an unexpected empty array or error
        if isinstance(data, list) and len(data) == 0:
            print(f"ℹ️ User ID '{user_id}' was processed, but returned no new data updates.")
            return True
            
        if isinstance(data, dict) and "exists" in data and not data["exists"]:
            print(f"❌ User ID '{user_id}' does not exist on osu!track.")
            return None

        print(f"✅ Successfully updated User ID: {user_id}!")
        return data

    except json.JSONDecodeError:
        print(f"💥 Parsing error: The server returned plain text/HTML instead of JSON data. Raw context: {response.text[:150]}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"💥 Network error updating User ID {user_id}: {e}")
        return None

def main():
    print("🚀 Starting osu!track Daily Batch Update...")
    for user_id in USER_IDS_TO_UPDATE:
        result = update_osutrack_user(user_id, mode=GAME_MODE)
        
        # If the API gave us a valid update dictionary with statistical changes
        if isinstance(result, dict):
            new_rank = result.get("pp_rank", "N/A")
            pp_count = result.get("pp_raw", "N/A")
            print(f"📊 ID {user_id} Stats -> Global Rank: {new_rank} | PP: {pp_count}")
        
        # Enforce a 15-second gap between targets to strictly honor the developer's requested guidelines
        print("🕒 Sleeping 15 seconds to respect rate limits...")
        time.sleep(15)
        
    print("🏁 Batch update process finished.")

if __name__ == "__main__":
    main()
