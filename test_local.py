"""Quick test script for Playwright scraping."""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils import fetch_page, build_search_url
from parser import extract_initial_state, extract_listings_from_state


async def test_scrape():
    """Test basic scraping."""
    print("🔧 Testing Njuskalo scraper with Playwright...")
    
    # Build URL for auti category
    url = build_search_url(category='auti', page=1)
    print(f"📍 URL: {url}")
    
    # Fetch page
    print("🌐 Fetching page...")
    html = await fetch_page(url, proxy_url=None, timeout=30)
    
    if not html:
        print("❌ Failed to fetch page")
        return 0
    
    print(f"✅ Fetched {len(html)} bytes")
    
    # Extract data
    print("🔍 Extracting data...")
    state = extract_initial_state(html)
    
    if not state:
        print("❌ Failed to extract __INITIAL_STATE__")
        return 0
    
    print(f"✅ Extracted state with keys: {list(state.keys())}")
    
    # Extract listings
    listings = extract_listings_from_state(state)
    
    if not listings:
        print("❌ No listings extracted")
        return 0
    
    print(f"✅ Extracted {len(listings)} listings")
    
    # Show first listing
    if listings:
        first = listings[0]
        print("\n📋 First listing:")
        print(f"  Title: {first.get('title', 'N/A')}")
        print(f"  Price: {first.get('price', 'N/A')}")
        print(f"  Location: {first.get('location', 'N/A')}")
        print(f"  URL: {first.get('url', 'N/A')}")
    
    return len(listings)


if __name__ == '__main__':
    count = asyncio.run(test_scrape())
    print(f"\n🎯 Result: {count} items scraped")
    sys.exit(0 if count > 0 else 1)
