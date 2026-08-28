import os
import requests
import json
import sys

# --- ZEMALA COCKPIT: READ -> VERIFY -> NORMALIZE -> RETURN ---
API_KEY = os.environ.get("YOUTUBE_API_KEY")
HANDLE = "lofowelt"

def verify_and_get_uploads_id():
    if not API_KEY or len(API_KEY) < 10:
        print("[!] ERROR: YOUTUBE_API_KEY environment variable is missing or invalid.")
        sys.exit(1)
        
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,contentDetails",
        "forHandle": HANDLE,
        "key": API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "error" in data:
        error = data["error"]
        print(f"[!] API ERROR: {error.get('message')} (Code: {error.get('code')})")
        sys.exit(1)
        
    items = data.get("items", [])
    if not items:
        print(f"[!] IDENTITY FAIL: Channel '@{HANDLE}' could not be resolved.")
        sys.exit(1)
        
    channel_item = items[0]
    channel_id = channel_item.get("id")
    channel_title = channel_item.get("snippet", {}).get("title")
    uploads_id = channel_item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    
    if not uploads_id:
        print("[!] IDENTITY FAIL: Uploads playlist ID not found in channel response.")
        sys.exit(1)
        
    print(f"[✓] IDENTITY MATCH: Channel '@{HANDLE}' -> ID: {channel_id} ('{channel_title}')")
    print(f"[✓] PASS: Verified Uploads-ID resolved -> {uploads_id}")
    return uploads_id

def fetch_and_normalize_playlist_items(uploads_id):
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    normalized_videos = []
    page_token = None
    
    print("[*] Initiating playlistItems fetch across pages...")
    
    while True:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": uploads_id,
            "maxResults": 50,
            "key": API_KEY
        }
        if page_token:
            params["pageToken"] = page_token
            
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error" in data:
            print(f"[!] PLAYLIST FETCH ERROR: {data['error'].get('message')}")
            break
            
        items = data.get("items", [])
        for item in items:
            snippet = item.get("snippet", {})
            content_details = item.get("contentDetails", {})
            
            norm_item = {
                "video_id": content_details.get("videoId") or snippet.get("resourceId", {}).get("videoId"),
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "published_at": snippet.get("publishedAt")
            }
            normalized_videos.append(norm_item)
            
        page_token = data.get("nextPageToken")
        if not page_token:
            break
            
    print(f"[✓] NORMALIZE COMPLETE: Total videos processed: {len(normalized_videos)}")
    return normalized_videos

if __name__ == "__main__":
    uploads_playlist_id = verify_and_get_uploads_id()
    videos = fetch_and_normalize_playlist_items(uploads_playlist_id)
    
    print("\n--- RETURN PREVIEW (First 2 Kondensationsplatten) ---")
    print(json.dumps(videos[:2], indent=2, ensure_ascii=False))
