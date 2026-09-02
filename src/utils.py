"""Utility functions for Njuškalo scraper."""
import httpx
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


def parse_proxy(proxy_config: Optional[Dict]) -> Optional[str]:
    """Parse Apify proxy configuration to proxy URL.
    
    Args:
        proxy_config: Proxy configuration from input
        
    Returns:
        Proxy URL string or None
    """
    if not proxy_config or not proxy_config.get('useApifyProxy'):
        return None
    
    groups = proxy_config.get('apifyProxyGroups', ['RESIDENTIAL'])
    group = groups[0] if groups else 'RESIDENTIAL'
    
    # Use Apify proxy URL format
    import os
    token = os.getenv('APIFY_PROXY_PASSWORD', os.getenv('APIFY_TOKEN', ''))
    
    if not token:
        logger.warning('No APIFY_TOKEN found for proxy authentication')
        return None
    
    return f'http://groups-{group}:{token}@proxy.apify.com:8000'


async def fetch_page(url: str, proxy_url: Optional[str] = None, timeout: int = 30) -> Optional[str]:
    """Fetch page HTML with error handling and anti-bot evasion.
    
    Args:
        url: URL to fetch
        proxy_url: Optional proxy URL
        timeout: Request timeout in seconds
        
    Returns:
        HTML content or None on failure
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        # Build client args
        client_args = {
            'timeout': timeout,
            'follow_redirects': True,
            'headers': headers
        }
        
        # Add proxy if provided (httpx 0.27+ uses 'proxy' not 'proxies')
        if proxy_url:
            client_args['proxy'] = proxy_url
        
        async with httpx.AsyncClient(**client_args) as client:
            response = await client.get(url)
            
            # Check for anti-bot redirects
            if 'validate.perfdrive' in str(response.url) or 'shield' in response.text.lower():
                logger.warning(f'Anti-bot redirect detected: {response.url}')
                logger.warning('Recommendation: Enable residential proxies for this site')
                return None
            
            if response.status_code != 200:
                logger.warning(f'HTTP {response.status_code} for {url}')
                return None
            
            if len(response.text) < 500:
                logger.warning(f'Response too small ({len(response.text)} bytes) for {url}')
                return None
            
            return response.text
            
    except httpx.TimeoutException:
        logger.error(f'Timeout fetching {url}')
        return None
    except Exception as e:
        logger.error(f'Error fetching {url}: {e}')
        return None


def build_search_url(category: str, search_query: str = '', location: str = '', 
                     price_min: int = 0, price_max: int = 0, condition: str = 'Any',
                     sort_by: str = 'datum-silazno', page: int = 1) -> str:
    """Build Njuškalo search URL with filters.
    
    Args:
        category: Main category
        search_query: Search keywords
        location: City/region filter
        price_min: Minimum price
        price_max: Maximum price
        condition: Item condition
        sort_by: Sort order
        page: Page number
        
    Returns:
        Complete search URL
    """
    base_url = 'https://www.njuskalo.hr'
    
    # Map category to URL path
    category_map = {
        'auti': 'auti',
        'nekretnine': 'nekretnine',
        'poslovi': 'poslovi',
        'elektronika': 'elektronika',
        'odijeca-obuća': 'odjeca-obuca',
        'sport-fitness': 'sport-fitness',
        'kućanski-aparati': 'kucanski-aparati',
        'namještaj': 'namjestaj',
        'sve-kategorije': ''
    }
    
    category_path = category_map.get(category, category)
    
    if category_path:
        url = f'{base_url}/{category_path}'
    else:
        url = base_url
    
    # Add search query if provided
    params = []
    
    if search_query:
        params.append(f'keywords={search_query.replace(" ", "+")}')
    
    if location and location != 'Any':
        params.append(f'location={location}')
    
    if price_min > 0:
        params.append(f'price[from]={price_min}')
    
    if price_max > 0:
        params.append(f'price[to]={price_max}')
    
    if condition and condition != 'Any':
        params.append(f'condition={condition}')
    
    if sort_by:
        params.append(f'sort={sort_by}')
    
    if page > 1:
        params.append(f'page={page}')
    
    if params:
        url += '?' + '&'.join(params)
    
    return url
