import json
import time
import requests

# Base endpoint from the official documentation
BASE_URL = "https://ameo.dev"

# Configuration using your permanent user IDs
USER_IDS_TO_UPDATE = [15534828, 39123148]
GAME_MODE = 0  # 0 = Standard osu!


def update_osutrack_user(user_id, mode=0):
    """Sends a POST request to update a user's stats on osu!track."""
    # The API reads both string names and numerical IDs in this parameter
    params = {"user": user_id, "mode": mode}

    try:
        print(f"🔄 Triggering update for User ID: {user_id}...")
        response = requests.post(BASE_URL, params=params)

        # Handle rate-limiting gracefully
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 12)
            print(
                f"⚠️ Rate limit hit (429). Waiting {retry_after} seconds before retrying..."
            )
            time.sleep(int(retry_after))
            return update_osutrack_user(user_id, mode)

        # Check for other network errors
        response.raise_for_status()

        # Parse the JSON response data
        data = response.json()

        # Check if the user ID exists on the platform
        if not data or ("exists" in data and not data["exists"]):
            print(f"❌ User ID '{user_id}' does not exist on osu!track.")
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
            # Extract basic metrics from the API response payload
            new_rank = result.get("pp_rank", "N/A")
            pp_count = result.get("pp_raw", "N/A")
            print(
                f"📊 ID {user_id} Stats -> Global Rank: {new_rank} | PP: {pp_count}"
            )

        # Strict 15-second delay to stay well under the 5 requests/minute API limit
        print("🕒 Sleeping 15 seconds to respect endpoint rate limits...")
        time.sleep(15)

    print("🏁 Batch update process finished.")


if __name__ == "__main__":
    main()