"""Parser module for extracting data from Njuškalo pages."""
import json
import re
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


def extract_initial_state(html: str) -> Optional[Dict]:
    """Extract __INITIAL_STATE__ JSON from page HTML.
    
    Args:
        html: Page HTML content
        
    Returns:
        Parsed JSON state or None
    """
    try:
        # Find the start of __INITIAL_STATE__
        start_marker = 'window.__INITIAL_STATE__='
        start_idx = html.find(start_marker)
        
        if start_idx == -1:
            logger.warning('No __INITIAL_STATE__ found in HTML')
            return None
        
        # Extract JSON using bracket matching (handles large nested objects)
        json_start = start_idx + len(start_marker)
        bracket_count = 0
        in_string = False
        escape_next = False
        json_end = json_start
        
        # Scan up to 1MB max
        for i in range(json_start, min(json_start + 1000000, len(html))):
            char = html[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"':
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    bracket_count += 1
                elif char == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        json_end = i + 1
                        break
        
        if bracket_count != 0:
            logger.error(f'Unmatched brackets in __INITIAL_STATE__ (count={bracket_count})')
            return None
        
        state_json = html[json_start:json_end]
        state = json.loads(state_json)
        
        logger.info(f'✅ Extracted __INITIAL_STATE__ with keys: {list(state.keys())}')
        return state
        
    except json.JSONDecodeError as e:
        logger.error(f'Failed to parse __INITIAL_STATE__ JSON: {e}')
        return None
    except Exception as e:
        logger.error(f'Error extracting __INITIAL_STATE__: {e}')
        return None


def extract_listings_from_state(state: Dict) -> List[Dict]:
    """Extract listing data from __INITIAL_STATE__.
    
    Args:
        state: Parsed __INITIAL_STATE__ object
        
    Returns:
        List of listing dictionaries
    """
    listings = []
    
    try:
        # Navigate to browseListingsStore.pageData
        browse_store = state.get('browseListingsStore', {})
        page_data = browse_store.get('pageData', {})
        
        if not page_data:
            logger.warning('No pageData found in browseListingsStore')
            return listings
        
        # Collect all listing types
        all_listings = []
        
        for key in ['regularListings', 'promotedListings', 'latestListings', 'superVauListings']:
            if key in page_data and isinstance(page_data[key], list):
                items = page_data[key]
                logger.info(f'Found {len(items)} items in {key}')
                all_listings.extend(items)
        
        if not all_listings:
            logger.warning('No listings found in any category')
            return listings
        
        logger.info(f'Total raw listings: {len(all_listings)}')
        
        # Extract data from each item
        for item in all_listings:
            try:
                listing = extract_listing_data(item)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.error(f'Error extracting listing: {e}')
                continue
        
        logger.info(f'✅ Extracted {len(listings)} listings from state')
        
    except Exception as e:
        logger.error(f'Error parsing listings from state: {e}')
    
    return listings


def extract_listing_data(item: Dict) -> Optional[Dict]:
    """Extract structured data from a listing item.
    
    Args:
        item: Raw listing object from __INITIAL_STATE__
        
    Returns:
        Normalized listing dictionary or None
    """
    try:
        # Build listing URL from categorySlug, titleSlug, and id
        listing_id = item.get('id', '')
        title_slug = item.get('titleSlug', '')
        category_slug = item.get('categorySlug', '')
        
        if listing_id and title_slug and category_slug:
            url = f'https://www.njuskalo.hr/{category_slug}/{title_slug}/{listing_id}'
        else:
            url = ''
        
        # Extract location from abstracts or location field
        location = item.get('location', '')
        if not location and 'abstracts' in item:
            for abstract in item.get('abstracts', []):
                caption = abstract.get('caption', '')
                if caption and 'lokacija' in caption.lower():
                    location = abstract.get('value', '')
                    break
        
        # Extract fields
        listing = {
            'url': url,
            'title': item.get('title', ''),
            'price': item.get('priceFormatted', '') or item.get('priceMinFormatted', '') or '',
            'location': location,
            'category': item.get('categorySlug', ''),
            'condition': item.get('condition', ''),
            'description': '',  # Not in listing view, would need detail page
            'seller': '',  # Not in listing view
            'postedDate': item.get('createdAtFormatted', '') or item.get('createdAt', ''),
            'imageUrl': item.get('image', ''),
            'scrapedAt': None  # Will be set by main
        }
        
        # Add abstracts as description
        if 'abstracts' in item:
            abstracts = item.get('abstracts', [])
            desc_parts = [a.get('value', '') for a in abstracts if a.get('value')]
            listing['description'] = ' | '.join(desc_parts)
        
        return listing
        
    except Exception as e:
        logger.error(f'Error extracting listing data: {e}')
        return None


def extract_listings_from_html(html: str) -> List[Dict]:
    """Fallback: Extract listings from raw HTML using BeautifulSoup.
    
    Args:
        html: Page HTML content
        
    Returns:
        List of listing dictionaries
    """
    listings = []
    
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Try to find listing containers
        # Common patterns: class containing 'listing', 'item', 'oglas', 'card', 'ad'
        containers = soup.find_all(['article', 'div'], class_=re.compile(r'listing|item|oglas|card|ad', re.I))
        
        if not containers:
            # Try finding links to /oglas/
            containers = soup.find_all('a', href=re.compile(r'/oglas/'))
        
        logger.info(f'Found {len(containers)} potential listing containers in HTML')
        
        for container in containers[:100]:  # Limit to first 100
            try:
                # Extract title
                title_elem = container.find(['h2', 'h3', 'h4', 'a'])
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # Extract URL
                link_elem = container.find('a', href=True)
                url = link_elem['href'] if link_elem else ''
                if url and not url.startswith('http'):
                    url = f'https://www.njuskalo.hr{url}'
                
                # Extract price
                price_elem = container.find(string=re.compile(r'€|kn|EUR|HRK|\d+[.,]\d+'))
                price = price_elem.strip() if price_elem else ''
                
                # Extract location
                location_elem = container.find(string=re.compile(r'Zagreb|Split|Rijeka|Osijek|Zadar'))
                location = location_elem.strip() if location_elem else ''
                
                # Extract image
                img_elem = container.find('img', src=True)
                image_url = img_elem['src'] if img_elem else ''
                
                if title or url:
                    listings.append({
                        'url': url,
                        'title': title,
                        'price': price,
                        'location': location,
                        'category': '',
                        'condition': '',
                        'description': '',
                        'seller': '',
                        'postedDate': '',
                        'imageUrl': image_url,
                        'scrapedAt': None
                    })
                    
            except Exception as e:
                logger.error(f'Error parsing container: {e}')
                continue
        
        logger.info(f'Extracted {len(listings)} listings from HTML')
        
    except Exception as e:
        logger.error(f'Error parsing HTML: {e}')
    
    return listings
