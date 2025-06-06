import os
import httpx

async def scrape_url(url: str):
    """
    Scrapes a URL using the Firecrawl API, extracting the raw HTML source.
    """
    firecrawl_host = os.getenv("FIRECRAWL_HOST", "http://localhost:3002")
    api_url = f"{firecrawl_host}/v0/scrape"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": url,
        "pageOptions": {
            "onlyMainContent": False,
            "includeHtml": True
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url, json=payload, headers=headers, timeout=120.0)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('html')
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
            raise 