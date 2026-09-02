"""Main scraper logic for Njuškalo."""
import asyncio
from datetime import datetime
from typing import Dict, Optional
import logging

from apify import Actor
from .utils import parse_proxy, fetch_page, build_search_url, cleanup_browser
from .parser import extract_initial_state, extract_listings_from_state, extract_listings_from_html

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main scraper entry point."""
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        
        # Extract input parameters with defaults
        category = actor_input.get('category', 'auti')
        search_query = actor_input.get('searchQuery', '')
        location = actor_input.get('location', '')
        price_min = actor_input.get('priceMin', 0)
        price_max = actor_input.get('priceMax', 0)
        condition = actor_input.get('condition', 'Any')
        sort_by = actor_input.get('sortBy', 'datum-silazno')
        include_description = actor_input.get('includeDescription', True)
        max_results = actor_input.get('maxResults', 50)
        proxy_config = actor_input.get('proxyConfiguration')
        
        logger.info('🚀 Njuškalo Scraper starting...')
        logger.info(f'📂 Category: {category}')
        logger.info(f'🔍 Search: {search_query or "All"}')
        logger.info(f'📍 Location: {location or "All"}')
        logger.info(f'💰 Price range: {price_min}-{price_max}')
        logger.info(f'🔢 Max results: {max_results}')
        
        # Parse proxy (now returns Playwright proxy dict)
        proxy_config_dict = parse_proxy(proxy_config)
        if proxy_config_dict:
            logger.info('🌐 Using Apify residential proxy')
        else:
            logger.info('⚠️ No proxy configured - direct connection')
        
        # Statistics
        items_scraped = 0
        requests_made = 0
        errors = 0
        page = 1
        
        try:
            while items_scraped < max_results:
                # Build URL for current page
                url = build_search_url(
                    category=category,
                    search_query=search_query,
                    location=location,
                    price_min=price_min,
                    price_max=price_max,
                    condition=condition,
                    sort_by=sort_by,
                    page=page
                )
                
                logger.info(f'📄 Fetching page {page}: {url}')
                
                # Fetch page with retries
                html = None
                for attempt in range(3):
                    try:
                        html = await fetch_page(url, proxy_config_dict)
                        requests_made += 1
                        
                        if html:
                            break
                        
                        if attempt < 2:
                            wait_time = (attempt + 1) * 2
                            logger.warning(f'⏳ Retry {attempt + 1}/3 in {wait_time}s...')
                            await asyncio.sleep(wait_time)
                            
                    except Exception as e:
                        logger.error(f'Error on attempt {attempt + 1}: {e}')
                        errors += 1
                        
                        if attempt < 2:
                            await asyncio.sleep((attempt + 1) * 2)
                
                if not html:
                    logger.error(f'❌ Failed to fetch page {page} after 3 attempts')
                    break
                
                # Extract listings
                listings = []
                
                # Try __INITIAL_STATE__ first
                state = extract_initial_state(html)
                if state:
                    listings = extract_listings_from_state(state)
                    logger.info(f'✅ Extracted {len(listings)} listings from __INITIAL_STATE__')
                
                # Fallback to HTML parsing
                if not listings:
                    logger.warning('⚠️ __INITIAL_STATE__ extraction failed, trying HTML parsing...')
                    listings = extract_listings_from_html(html)
                    logger.info(f'✅ Extracted {len(listings)} listings from HTML')
                
                if not listings:
                    logger.warning(f'❌ No listings found on page {page}')
                    break
                
                # Process and push listings
                timestamp = datetime.utcnow().isoformat() + 'Z'
                
                for listing in listings:
                    if items_scraped >= max_results:
                        break
                    
                    # Set scraped timestamp
                    listing['scrapedAt'] = timestamp
                    
                    # Ensure all fields exist (set to empty string if missing)
                    for field in ['url', 'title', 'price', 'location', 'category', 
                                  'condition', 'description', 'seller', 'postedDate', 'imageUrl']:
                        if field not in listing or listing[field] is None:
                            listing[field] = ''
                    
                    # Push to dataset
                    await Actor.push_data(listing)
                    items_scraped += 1
                    
                    # Log progress every 10 items
                    if items_scraped % 10 == 0:
                        logger.info(f'📊 Progress: {items_scraped}/{max_results} items scraped')
                
                # Check if we should continue to next page
                if items_scraped >= max_results:
                    logger.info(f'✅ Reached max results limit ({max_results})')
                    break
                
                if len(listings) == 0:
                    logger.info('📭 No more listings found, stopping pagination')
                    break
                
                # Move to next page
                page += 1
                
                # Rate limiting
                await asyncio.sleep(1)
            
            # Final statistics
            logger.info('=' * 50)
            logger.info('📊 SCRAPING COMPLETE')
            logger.info(f'✅ Items scraped: {items_scraped}')
            logger.info(f'📄 Pages processed: {page}')
            logger.info(f'🌐 Requests made: {requests_made}')
            logger.info(f'❌ Errors: {errors}')
            logger.info('=' * 50)
            
            # Save task context (MANDATORY for Apify)
            try:
                env = Actor.get_env()
                await Actor.set_value('SAVED-TASK', {
                    'actorId': env.get('actor_id'),
                    'actorRunId': env.get('actor_run_id'),
                    'defaultDatasetId': env.get('default_dataset_id'),
                    'startedAt': env.get('started_at'),
                    'input': actor_input,
                    'stats': {
                        'itemsScraped': items_scraped,
                        'requestsMade': requests_made,
                        'errors': errors,
                        'pagesProcessed': page
                    }
                })
                logger.info('💾 Saved task context to SAVED-TASK')
            except Exception as e:
                logger.error(f'Failed to save task context: {e}')
            
            if items_scraped == 0:
                logger.error('⚠️ WARNING: Zero items scraped! Check:')
                logger.error('   1. URL parameters and category')
                logger.error('   2. Site structure changes')
                logger.error('   3. Proxy/blocking issues')
                logger.error('   4. __INITIAL_STATE__ extraction logic')
            
        except Exception as e:
            logger.error(f'💥 Fatal error: {e}')
            import traceback
            traceback.print_exc()
            raise
        finally:
            # Cleanup browser resources
            await cleanup_browser()
            logger.info('🧹 Browser cleanup complete')


if __name__ == '__main__':
    asyncio.run(main())
