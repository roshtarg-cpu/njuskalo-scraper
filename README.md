# 🇭🇷 Njuškalo Scraper - Croatia Marketplace Extractor

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-00D4AA?style=for-the-badge&logo=apify)](https://apify.com)
[![Claude Compatible](https://img.shields.io/badge/Claude-MCP_Compatible-5A67D8?style=for-the-badge&logo=anthropic)](https://claude.ai)
[![ChatGPT Compatible](https://img.shields.io/badge/ChatGPT-AI_Agent_Ready-10A37F?style=for-the-badge&logo=openai)](https://openai.com)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![License MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

> **🤖 AI-Agent Optimized**: Compatible with Claude, ChatGPT & AI agents via Apify MCP (Model Context Protocol)

Extract listings from **Njuškalo** (njuskalo.hr), Croatia's #1 online marketplace! Scrape cars, real estate, jobs, electronics, and more with advanced category filters, residential proxy support, and AI-friendly structured output.

## ✨ Features

- 🚗 **Multi-Category Support**: Cars (auti), real estate (nekretnine), jobs (poslovi), electronics, clothing, furniture & more
- 🎯 **Advanced Filters**: Search by keywords, location, price range, condition, and sort order
- 🌐 **Residential Proxy Support**: Built-in Apify residential proxy integration for reliable extraction
- 📊 **Structured Output**: Clean JSON/CSV/Excel export with all listing details
- 🤖 **AI-Agent Ready**: Optimized for Claude Code, ChatGPT plugins, and MCP integrations
- ⚡ **Fast & Reliable**: Automatic retries, pagination, and error handling
- 📝 **Full Descriptions**: Optional extraction of complete listing descriptions
- 🔄 **Real-time Progress**: Live logging and statistics during scraping

## 🚀 Quick Start

### Using Apify Console

1. Go to [Apify Console](https://console.apify.com)
2. Search for "Njuškalo Scraper" in the Store
3. Click "Try for free"
4. Configure inputs:
   - **Category**: Select category (cars, real estate, jobs, etc.)
   - **Search Query**: Keywords to filter listings (optional)
   - **Location**: City or region (Zagreb, Split, Rijeka, etc.)
   - **Price Range**: Min/max price filters
   - **Max Results**: Number of listings to scrape
5. Click "Start" and wait for results!

### Using API (Python)

```python
from apify_client import ApifyClient

client = ApifyClient('YOUR_APIFY_TOKEN')

# Scrape cars in Zagreb under 10,000 EUR
run_input = {
    "category": "auti",
    "searchQuery": "",
    "location": "Zagreb",
    "priceMin": 0,
    "priceMax": 10000,
    "maxResults": 50,
    "proxyConfiguration": {
        "useApifyProxy": True,
        "apifyProxyGroups": ["RESIDENTIAL"]
    }
}

run = client.actor('YOUR_USERNAME/njuskalo-scraper').call(run_input=run_input)

# Fetch results
for item in client.dataset(run['defaultDatasetId']).iterate_items():
    print(f"{item['title']} - {item['price']} - {item['location']}")
```

### Using Claude (MCP Integration) 🤖

With Claude Desktop and Apify MCP:

```
Claude, scrape 20 car listings from Njuškalo in Split under 15000 EUR
```

Claude will automatically:
1. Configure the Njuškalo scraper with appropriate filters
2. Run the actor via MCP
3. Parse and present results in a readable format

### Using ChatGPT (Plugin/Actions) 🤖

With ChatGPT Apify plugin:

```
Get me real estate listings in Zagreb from Njuškalo, max price 200000 EUR
```

## 📥 Input Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `category` | String | ✅ Yes | Main category to scrape | `"auti"` (cars) |
| `searchQuery` | String | No | Search keywords | `"BMW X5"` |
| `location` | String | No | City or region filter | `"Zagreb"` |
| `priceMin` | Integer | No | Minimum price (HRK/EUR) | `5000` |
| `priceMax` | Integer | No | Maximum price (HRK/EUR) | `20000` |
| `condition` | String | No | Item condition | `"novo"` (new) |
| `sortBy` | String | No | Sort order | `"datum-silazno"` |
| `includeDescription` | Boolean | No | Extract full descriptions | `true` |
| `maxResults` | Integer | ✅ Yes | Max listings to scrape | `50` |
| `proxyConfiguration` | Object | No | Apify proxy settings | See below |

### Categories

- 🚗 **auti** - Cars
- 🏠 **nekretnine** - Real Estate
- 💼 **poslovi** - Jobs
- 📱 **elektronika** - Electronics
- 👔 **odijeca-obuća** - Clothing & Shoes
- ⚽ **sport-fitness** - Sports & Fitness
- 🏡 **kućanski-aparati** - Home Appliances
- 🛋️ **namještaj** - Furniture
- 📋 **sve-kategorije** - All Categories

### Sort Options

- `datum-silazno` - Newest first (default)
- `datum-uzlazno` - Oldest first
- `cijena-silazno` - Highest price
- `cijena-uzlazno` - Lowest price

### Proxy Configuration

```json
{
  "useApifyProxy": true,
  "apifyProxyGroups": ["RESIDENTIAL"]
}
```

**Recommended**: Use residential proxies for reliable extraction and to avoid blocking.

## 📤 Output Format

Each listing contains:

```json
{
  "url": "https://www.njuskalo.hr/oglas/bmw-x5-m50d/12345678",
  "title": "BMW X5 M50d - 2019",
  "price": "45.000 €",
  "location": "Zagreb",
  "category": "Automobili",
  "condition": "Rabljeno",
  "description": "Full listing description...",
  "seller": "Auto Salon XYZ",
  "postedDate": "2024-01-15",
  "imageUrl": "https://static.njuskalo.hr/...",
  "scrapedAt": "2024-01-20T10:30:00Z"
}
```

## 🎯 Use Cases

- 🏢 **Market Research**: Analyze pricing trends across categories
- 🤖 **AI Agents**: Integrate with Claude/ChatGPT for automated searches
- 📊 **Price Monitoring**: Track item prices over time
- 🔍 **Lead Generation**: Find business opportunities in various categories
- 📈 **Data Analysis**: Build datasets for ML/analytics projects
- 🛒 **Competitor Analysis**: Monitor marketplace activity

## 🤖 AI Agent Integration

This actor is **optimized for AI agents** and supports:

### Model Context Protocol (MCP)

```typescript
// MCP tool definition
{
  "name": "njuskalo_scraper",
  "description": "Extract listings from Njuškalo marketplace",
  "inputSchema": {
    "type": "object",
    "properties": {
      "category": { "type": "string", "enum": ["auti", "nekretnine", "poslovi", ...] },
      "searchQuery": { "type": "string" },
      "maxResults": { "type": "integer", "default": 20 }
    }
  }
}
```

### Claude Code Integration

Claude can directly invoke this actor:

```python
# Claude's internal MCP call
await apify.run_actor(
    "YOUR_USERNAME/njuskalo-scraper",
    input={
        "category": "auti",
        "location": "Split",
        "maxResults": 10
    }
)
```

### ChatGPT Actions

Configure in ChatGPT custom actions:

```yaml
openapi: 3.0.0
paths:
  /run-sync:
    post:
      operationId: runNjuskaloScraper
      parameters:
        - name: category
        - name: maxResults
```

## 🛠️ Technical Details

- **Runtime**: Python 3.11
- **Framework**: Apify SDK 2.0+
- **HTTP Client**: httpx (async)
- **Parser**: BeautifulSoup4 + JSON extraction
- **Architecture**: Async/await for efficient I/O
- **Extraction Method**: __INITIAL_STATE__ JSON parsing with HTML fallback
- **Proxy**: Apify residential proxy support
- **Retries**: Automatic retry logic with exponential backoff

### Architecture

1. **Fetch**: Retrieve HTML with proxy support
2. **Extract**: Parse __INITIAL_STATE__ JSON from React app
3. **Fallback**: Use BeautifulSoup if JSON extraction fails
4. **Paginate**: Iterate through result pages
5. **Output**: Push structured data to Apify dataset

## 📊 Performance

- **Speed**: ~10-20 listings/second
- **Memory**: 512 MB - 1 GB RAM
- **Cost**: $0.005 per result (avg) + $0.05 start fee
- **Proxy**: Residential proxies recommended (~$0.50/GB)

## 🔧 Development

### Local Testing

```bash
# Clone repository
git clone https://github.com/roshtarg-cpu/njuskalo-scraper.git
cd njuskalo-scraper

# Install dependencies
pip install -r requirements.txt

# Set Apify token
export APIFY_TOKEN='your_token_here'

# Run locally
apify run
```

### Input Example (input.json)

```json
{
  "category": "auti",
  "searchQuery": "BMW",
  "location": "Zagreb",
  "priceMax": 20000,
  "maxResults": 30,
  "proxyConfiguration": {
    "useApifyProxy": true,
    "apifyProxyGroups": ["RESIDENTIAL"]
  }
}
```

## 📝 Changelog

### Version 1.0 (2024-01)
- 🎉 Initial release
- ✅ Multi-category support
- ✅ Advanced filtering
- ✅ Residential proxy support
- ✅ AI-agent optimization

## 🤝 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/roshtarg-cpu/njuskalo-scraper/issues)
- 💬 Discord: [Apify Community](https://discord.com/invite/jyEM2PRvMU)

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚖️ Legal & Ethics

This scraper is intended for:
- ✅ Market research and analysis
- ✅ Price monitoring
- ✅ Personal data collection for legitimate purposes

Please ensure compliance with:
- Njuškalo's Terms of Service
- Croatian data protection laws (GDPR)
- Robots.txt and rate limiting

**Do not use for**:
- ❌ Spam or unsolicited contact
- ❌ Copyright infringement
- ❌ Competitive harm

## 🌟 Keywords

`njuskalo`, `croatia`, `marketplace`, `scraper`, `apify`, `claude`, `chatgpt`, `ai-agent`, `mcp`, `model-context-protocol`, `web-scraping`, `data-extraction`, `croatia-marketplace`, `auti`, `nekretnine`, `poslovi`, `residential-proxy`, `structured-data`, `json-export`, `ai-compatible`, `automation`

---

**Made with ❤️ for AI agents & developers**

*Compatible with Claude, ChatGPT & AI agents via Apify MCP*
