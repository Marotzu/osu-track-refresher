import json
import time
import requests

# Added a trailing slash to prevent server redirects
BASE_URL = "https://ameo.dev"

USER_IDS_TO_UPDATE = [15534828, 39123148]
GAME_MODE = 0 

def update_osutrack_user(user_id, mode=0):
    params = {"user": user_id, "mode": mode}
    try:
        print(f"🔄 Triggering update for User ID: {user_id}...")
        
        # We try POST first but pass allow_redirects=False to catch routing quirks
        response = requests.post(BASE_URL, params=params, allow_redirects=False)

        # If POST isn't accepted or redirects, try GET as a fallback
        if response.status_code in [301, 302, 307, 405]:
            print("ℹ️ Adjusting request format (switching to GET)...")
            response = requests.get(BASE_URL.rstrip('/'), params=params)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 12)
            print(f"⚠️ Rate limit hit. Waiting {retry_after} seconds...")
            time.sleep(int(retry_after))
            return update_osutrack_user(user_id, mode)

        response.raise_for_status()
        data = response.json()

        if not data or ("exists" in data and not data["exists"]):
            print(f"❌ User ID '{user_id}' does not exist.")
            return None

        print(f"✅ Successfully updated User ID: {user_id}!")
        return data

    except requests.exceptions.RequestException as e:
        print(f"💥 Network error updating User ID {user_id}: {e}")
        return None

def main():
    print("🚀 Starting osu!track Daily Batch Update...")
    for user_id in USER_IDS_TO_UPDATE:
        result = update_osutrack_user(user_id, mode=GAME_MODE)
        if result:
            new_rank = result.get("pp_rank", "N/A")
            pp_count = result.get("pp_raw", "N/A")
            print(f"📊 ID {user_id} Stats -> Global Rank: {new_rank} | PP: {pp_count}")
        
        print("🕒 Sleeping 15 seconds to respect rate limits...")
        time.sleep(15)
    print("🏁 Batch update process finished.")

if __name__ == "__main__":
    main()
