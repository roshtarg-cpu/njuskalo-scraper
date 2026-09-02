"""Utility functions for Njuškalo scraper."""
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from typing import Optional, Dict
import logging
import asyncio
import random

logger = logging.getLogger(__name__)

# Global Playwright and browser instances
_playwright: Optional[Playwright] = None
_browser: Optional[Browser] = None


def parse_proxy(proxy_config: Optional[Dict]) -> Optional[Dict]:
    """Parse Apify proxy configuration to Playwright proxy format.
    
    Args:
        proxy_config: Proxy configuration from input
        
    Returns:
        Playwright proxy dict or None
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
    
    return {
        'server': 'http://proxy.apify.com:8000',
        'username': f'groups-{group}',
        'password': token
    }


async def get_browser() -> Browser:
    """Get or create global browser instance with anti-detection settings.
    
    Returns:
        Playwright Browser instance
    """
    global _playwright, _browser
    
    if _browser and _browser.is_connected():
        return _browser
    
    if not _playwright:
        _playwright = await async_playwright().start()
    
    _browser = await _playwright.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-software-rasterizer',
            '--disable-extensions',
            '--window-size=1920,1080',
            '--start-maximized',
        ]
    )
    
    logger.info('🌐 Browser launched with anti-detection settings')
    return _browser


async def cleanup_browser() -> None:
    """Cleanup browser and playwright instances."""
    global _playwright, _browser
    
    if _browser:
        await _browser.close()
        _browser = None
    
    if _playwright:
        await _playwright.stop()
        _playwright = None


async def setup_stealth_page(page: Page) -> None:
    """Configure page with comprehensive stealth settings to bypass ShieldSquare/Radware.
    
    Args:
        page: Playwright Page instance
    """
    # Comprehensive anti-detection script
    await page.add_init_script("""
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false
        });
        
        // Override the navigator.plugins to have length
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer'},
                {name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                {name: 'Native Client', description: '', filename: 'internal-nacl-plugin'}
            ],
        });
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Add chrome object
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['hr-HR', 'hr', 'en-US', 'en']
        });
        
        // Override platform
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });
        
        // Override hardwareConcurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
        
        // Override deviceMemory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });
        
        // Override connection
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                downlink: 10,
                rtt: 50,
                saveData: false
            })
        });
        
        // Override maxTouchPoints
        Object.defineProperty(navigator, 'maxTouchPoints', {
            get: () => 0
        });
        
        // Mock battery API
        navigator.getBattery = () => Promise.resolve({
            charging: true,
            chargingTime: 0,
            dischargingTime: Infinity,
            level: 1,
            addEventListener: () => {}
        });
        
        // Add realistic screen properties
        Object.defineProperty(screen, 'availWidth', { get: () => 1920 });
        Object.defineProperty(screen, 'availHeight', { get: () => 1040 });
        Object.defineProperty(screen, 'width', { get: () => 1920 });
        Object.defineProperty(screen, 'height', { get: () => 1080 });
        Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
        Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
        
        // Override Intl.DateTimeFormat to use Europe/Zagreb
        const originalDateTimeFormat = Intl.DateTimeFormat;
        Intl.DateTimeFormat = function(...args) {
            if (args.length === 0 || !args[0]) {
                args[0] = 'hr-HR';
            }
            if (!args[1]) {
                args[1] = { timeZone: 'Europe/Zagreb' };
            }
            return new originalDateTimeFormat(...args);
        };
        Intl.DateTimeFormat.prototype = originalDateTimeFormat.prototype;
        
        // Make sure toString doesn't reveal function proxy
        const toStringProxy = Function.prototype.toString;
        Function.prototype.toString = function() {
            if (this === navigator.permissions.query) {
                return 'function query() { [native code] }';
            }
            return toStringProxy.call(this);
        };
    """)


async def fetch_page(url: str, proxy_url: Optional[Dict] = None, timeout: int = 60) -> Optional[str]:
    """Fetch page HTML using Playwright with comprehensive anti-bot evasion.
    
    Args:
        url: URL to fetch
        proxy_url: Optional proxy configuration (Playwright format)
        timeout: Request timeout in seconds (increased default to 60)
        
    Returns:
        HTML content or None on failure
    """
    context: Optional[BrowserContext] = None
    try:
        browser = await get_browser()
        
        # Randomize user agent slightly to appear more organic
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        ]
        user_agent = random.choice(user_agents)
        
        # Create context with comprehensive stealth settings
        context_args = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': user_agent,
            'locale': 'hr-HR',
            'timezone_id': 'Europe/Zagreb',
            'color_scheme': 'light',
            'device_scale_factor': 1,
            'has_touch': False,
            'is_mobile': False,
            'extra_http_headers': {
                'Accept-Language': 'hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
            }
        }
        
        if proxy_url:
            context_args['proxy'] = proxy_url
            logger.info(f'Using proxy: {proxy_url["server"]}')
        
        context = await browser.new_context(**context_args)
        
        # Block unnecessary resources to speed up loading
        await context.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf}", lambda route: route.abort())
        
        page = await context.new_page()
        
        # Apply comprehensive stealth scripts
        await setup_stealth_page(page)
        
        # Random delay before navigation (human-like)
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Navigate to page
        logger.info(f'Loading {url}...')
        response = await page.goto(url, wait_until='domcontentloaded', timeout=timeout * 1000)
        
        # Wait for body to be present
        try:
            await page.wait_for_selector('body', timeout=5000)
        except:
            pass
        
        # Additional wait for JS execution
        await asyncio.sleep(random.uniform(2, 4))
        
        if not response:
            logger.error(f'No response for {url}')
            await context.close()
            return None
        
        # Check for anti-bot redirects in URL
        current_url = page.url
        if 'validate.perfdrive' in current_url or 'shieldsquare' in current_url.lower():
            logger.warning(f'⚠️ Anti-bot redirect detected in URL: {current_url}')
            logger.warning('💡 Recommendation: Use residential proxies (ShieldSquare is blocking datacenter IPs)')
            await context.close()
            return None
        
        if response.status != 200:
            logger.warning(f'HTTP {response.status} for {url}')
            await context.close()
            return None
        
        # Get HTML content
        html = await page.content()
        
        if len(html) < 500:
            logger.warning(f'Response too small ({len(html)} bytes) for {url}')
            await context.close()
            return None
        
        # Check if we got blocked content in HTML
        if 'validate.perfdrive' in html or 'ShieldSquare' in html or '_pxBlock' in html:
            logger.warning(f'⚠️ Anti-bot content detected in HTML ({len(html)} bytes)')
            # Log a snippet for debugging
            snippet = html[:500] if len(html) > 500 else html
            logger.warning(f'HTML snippet: {snippet[:200]}...')
            logger.warning('💡 This site requires residential proxies to bypass bot detection')
            await context.close()
            return None
        
        logger.info(f'✅ Fetched {len(html)} bytes from {url}')
        
        await context.close()
        return html
        
    except Exception as e:
        logger.error(f'Error fetching {url}: {e}')
        if context:
            try:
                await context.close()
            except:
                pass
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
