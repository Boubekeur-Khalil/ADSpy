import requests
import json
import os
import time
import csv
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import parse_qs, urlparse  # Add this import
import argparse
from constants import DEFAULT_COUNTRY, DEFAULT_LIMIT, API_FIELDS, GRAPH_API_URL

# Load environment variables (make sure you have ACCESS_TOKEN=.env)
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# After load_dotenv()
if not ACCESS_TOKEN:
    print("❌ ERROR: ACCESS_TOKEN not found in .env file")
    exit(1)

# ===============================
# CONFIGURATION
# ===============================
COUNTRY = "DZ"             # Change to your target country (e.g. DZ)
SEARCH_TERM = "salviano"      # Must have search_terms or search_page_ids
LIMIT = 10                 # Number of ads to fetch per request (max 100)
GRAPH_API_VERSION = "v24.0"
GRAPH_API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/ads_archive"

# ===============================
# API PARAMETERS
# ===============================
params = {
    "access_token": ACCESS_TOKEN,
    "ad_reached_countries": COUNTRY,
    "ad_active_status": "ALL",
    "ad_type": "ALL",
    "search_terms": SEARCH_TERM,
    "limit": LIMIT,
    # ✅ Supported fields in v24.0
    "fields": (
        "id,"
        "ad_creation_time,"
        "ad_creative_bodies,"
        "ad_creative_link_titles,"
        "ad_creative_link_descriptions,"
        "page_name,"
        "ad_snapshot_url,"
        "ad_reached_countries"
    ),
}

# ===============================
# API REQUEST
# ===============================
def fetch_all_ads(params):
    all_ads = []
    page_count = 0
    max_retries = 3
    
    try:
        while True:
            page_count += 1
            print(f"📄 Fetching page {page_count}...", end='\r')
            
            # Add delay between requests
            if page_count > 1:
                time.sleep(1)
            
            # Stop after reasonable number of pages
            if page_count > 10:
                print("\n⚠️ Reached maximum number of pages (10)")
                break
                
            for attempt in range(max_retries):
                try:
                    # Add timeout to prevent hanging
                    response = requests.get(GRAPH_API_URL, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    break
                except requests.Timeout:
                    if attempt == max_retries - 1:
                        print("\n❌ Request timed out after multiple attempts")
                        return all_ads
                    print(f"\n⚠️ Timeout occurred, retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)
                except requests.RequestException as e:
                    print(f"\n❌ HTTP Error: {e}")
                    return all_ads
                except json.JSONDecodeError:
                    print("\n❌ Invalid JSON response")
                    return all_ads
            
            if "error" in data:
                print("\n❌ API Error:")
                print(json.dumps(data, indent=2))
                break
            
            current_ads = data.get("data", [])
            if not current_ads:
                break
            
            all_ads.extend(current_ads)
            print(f"✅ Found {len(current_ads)} ads on page {page_count}      ")
            
            # Get next page if available
            paging = data.get("paging", {})
            if "next" not in paging:
                break
            
            # Fix: Parse the next URL properly
            next_url = paging["next"]
            parsed_url = urlparse(next_url)
            params = parse_qs(parsed_url.query)
            # Convert list values to single strings
            params = {k: v[0] for k, v in params.items()}
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        return all_ads
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return all_ads
    
    return all_ads

# ===============================
# DISPLAY RESULTS
# ===============================
def display_results(ads):
    print(f"✅ Found {len(ads)} ads matching '{SEARCH_TERM}' in {COUNTRY}.\n")
    
    for i, ad in enumerate(ads, start=1):
        print(f"🔹 [{i}] {ad.get('page_name', 'Unknown Page')}")
        print(f"🕒 Created: {ad.get('ad_creation_time')}")
        print(f"📄 Title: {', '.join(ad.get('ad_creative_link_titles', [])) if ad.get('ad_creative_link_titles') else '—'}")
        print(f"💬 Description: {', '.join(ad.get('ad_creative_link_descriptions', [])) if ad.get('ad_creative_link_descriptions') else '—'}")
        print(f"📢 Body: {', '.join(ad.get('ad_creative_bodies', []))[:150] if ad.get('ad_creative_bodies') else '—'}...")
        print(f"🔗 Snapshot: {ad.get('ad_snapshot_url')}")
        print("-" * 80)
    
    print("\n✅ Done.")

def save_results(ads):
    # Create 'results' directory if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_filename = f"fb_ads_{COUNTRY}_{SEARCH_TERM}_{timestamp}"
    
    # Save as JSON
    json_path = f"results/{base_filename}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(ads, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved JSON results to: {json_path}")
    
    # Save as CSV
    csv_path = f"results/{base_filename}.csv"
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # Write headers
        headers = [
            'Page Name',
            'Creation Time',
            'Link Title',
            'Link Description',
            'Ad Body',
            'Snapshot URL'
        ]
        writer.writerow(headers)
        
        # Write data
        for ad in ads:
            row = [
                ad.get('page_name', ''),
                ad.get('ad_creation_time', ''),
                ', '.join(ad.get('ad_creative_link_titles', [])),
                ', '.join(ad.get('ad_creative_link_descriptions', [])),
                ', '.join(ad.get('ad_creative_bodies', [])),
                ad.get('ad_snapshot_url', '')
            ]
            writer.writerow(row)
    print(f"✅ Saved CSV results to: {csv_path}")

def parse_args():
    parser = argparse.ArgumentParser(description='Facebook Ad Library Scraper')
    parser.add_argument('--country', type=str, default=DEFAULT_COUNTRY,
                      help='Target country code (e.g. US, DZ)')
    parser.add_argument('--keyword', type=str, required=True,
                      help='Search keyword')
    parser.add_argument('--limit', type=int, default=DEFAULT_LIMIT,
                      help='Number of ads to fetch per request (max 100)')
    return parser.parse_args()

# Modify the main() function
def main():
    args = parse_args()
    
    print(f"🔎 Fetching ads from Facebook Ad Library (v24.0) for country: {args.country} and keyword: '{args.keyword}' ...")
    
    # Update params with command line arguments
    params = {
        "access_token": ACCESS_TOKEN,
        "ad_reached_countries": args.country,
        "ad_active_status": "ALL",
        "ad_type": "ALL",
        "search_terms": args.keyword,
        "limit": args.limit,
        "fields": API_FIELDS,
    }
    
    # Fetch ads
    all_ads = fetch_all_ads(params)
    
    # Error handling
    if isinstance(all_ads, dict) and "error" in all_ads:
        print("❌ API Error:")
        print(json.dumps(all_ads, indent=2))
        return
    
    if not all_ads:
        print("⚠️ No ads found for this query.")
        return
        
    # Display results
    display_results(all_ads)
    
    # Save results
    save_results(all_ads)
    
    print("\n✅ Done.")

if __name__ == "__main__":
    main()
