import os
import json
import time
import requests
from dotenv import load_dotenv
from serpapi.google_search import GoogleSearch
from together import Together

# ANSI color codes
class Colors:
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

# Load environment variables
load_dotenv()

# Initialize clients
together_api_key = os.getenv("TOGETHER_API_KEY")
if not together_api_key:
    print(f"{Colors.RED}Error: TOGETHER_API_KEY not found in environment variables{Colors.RESET}")
    
client = Together(api_key=together_api_key)
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
serp_api_key = os.getenv("SERP_API_KEY")

if not firecrawl_api_key:
    print(f"{Colors.RED}Warning: FIRECRAWL_API_KEY not found in environment variables{Colors.RESET}")

def search_google(query):
    """Search Google using SerpAPI and return top results."""
    print(f"{Colors.YELLOW}Searching Google for '{query}'...{Colors.RESET}")
    search = GoogleSearch({"q": query, "api_key": serp_api_key})
    return search.get_dict().get("organic_results", [])

def select_urls_with_gemini(company, objective, serp_results):
    """
    Use Llama 4 Maverick to select URLs from SERP results.
    Returns a list of URLs.
    """
    try:
        serp_data = [{"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet")} 
                     for r in serp_results if r.get("link")]
        
        print(f"{Colors.CYAN}Found {len(serp_data)} search results to analyze{Colors.RESET}")
        
        if not serp_data:
            print(f"{Colors.YELLOW}No search results found to analyze{Colors.RESET}")
            return []

        prompt = (
            "Task: Select the most relevant URLs from search results, prioritizing official sources.\n\n"
            "Instructions:\n"
            "1. PRIORITIZE official company websites, documentation, and press releases first\n"
            "2. Select ONLY URLs that directly contain information about the requested topic\n"
            "3. Return ONLY a JSON object with the following structure: {\"selected_urls\": [\"url1\", \"url2\"]}\n"
            "4. Do not include social media links (Twitter, LinkedIn, Facebook, etc.)\n"
            "5. Exclude any LinkedIn URLs as they cannot be accessed\n"
            "6. Select a MAXIMUM of 3 most relevant URLs\n"
            "7. Order URLs by relevance: official sources first, then trusted news/industry sources\n"
            "8. IMPORTANT: Only output the JSON object, no other text or explanation\n\n"
            f"Company: {company}\n"
            f"Information Needed: {objective}\n"
            f"Search Results: {json.dumps(serp_data, indent=2)}\n\n"
            "Response Format: {\"selected_urls\": [\"https://example.com\", \"https://example2.com\"]}\n\n"
            "Remember: Prioritize OFFICIAL sources and limit to 3 MOST RELEVANT URLs only."
        )

        try:
            print(f"{Colors.YELLOW}Calling Together AI model...{Colors.RESET}")
            response = client.chat.completions.create(
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                messages=[{"role": "user", "content": prompt}],
            )
            print(f"{Colors.GREEN}Got response from Together AI{Colors.RESET}")
            print(f"{Colors.CYAN}Raw response: {response.choices[0].message.content}{Colors.RESET}")
            
            cleaned_response = response.choices[0].message.content.strip()

            # Find the JSON object in the response
            import re
            json_match = re.search(r'\{[\s\S]*"selected_urls"[\s\S]*\}', cleaned_response)
            if json_match:
                cleaned_response = json_match.group(0)
                print(f"{Colors.CYAN}Extracted JSON: {cleaned_response}{Colors.RESET}")

            # Clean the response text
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response.split('```')[1]
                if cleaned_response.startswith('json'):
                    cleaned_response = cleaned_response[4:]
            cleaned_response = cleaned_response.strip()

            try:
                # Parse JSON response
                result = json.loads(cleaned_response)
                if isinstance(result, dict) and "selected_urls" in result:
                    urls = result["selected_urls"]
                else:
                    print(f"{Colors.YELLOW}Response did not contain the expected 'selected_urls' key{Colors.RESET}")
                    urls = []
            except json.JSONDecodeError as e:
                print(f"{Colors.YELLOW}Failed to parse JSON: {str(e)}{Colors.RESET}")
                # Fallback to text parsing
                urls = [line.strip() for line in cleaned_response.split('\n') 
                       if line.strip().startswith(('http://', 'https://'))]

            # Clean up URLs
            cleaned_urls = [url.replace('/*', '').rstrip('/') for url in urls]
            cleaned_urls = [url for url in cleaned_urls if url]

            if not cleaned_urls:
                print(f"{Colors.YELLOW}No valid URLs found in response.{Colors.RESET}")
                return []

            print(f"{Colors.CYAN}Selected URLs for extraction:{Colors.RESET}")
            for url in cleaned_urls:
                print(f"- {url}")

            return cleaned_urls

        except Exception as e:
            print(f"{Colors.RED}Error calling Together AI: {str(e)}{Colors.RESET}")
            return []

    except Exception as e:
        print(f"{Colors.RED}Error selecting URLs: {str(e)}{Colors.RESET}")
        return []

def extract_company_info(urls, prompt, company, api_key):
    """Use requests to call Firecrawl's extract endpoint with selected URLs."""
    print(f"{Colors.YELLOW}Extracting structured data from the provided URLs using Firecrawl...{Colors.RESET}")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        "urls": urls,
        "prompt": prompt + " for " + company,
        "enableWebSearch": True
    }
    
    try:
        print(f"{Colors.CYAN}Making request to Firecrawl API...{Colors.RESET}")
        response = requests.post(
            "https://api.firecrawl.dev/v1/extract",
            headers=headers,
            json=payload,
            timeout=120  # Increased timeout to 120 seconds
        )
        
        if response.status_code != 200:
            print(f"{Colors.RED}API returned status code {response.status_code}: {response.text}{Colors.RESET}")
            return None
            
        data = response.json()
        
        if not data.get('success'):
            print(f"{Colors.RED}API returned error: {data.get('error', 'No error message')}{Colors.RESET}")
            return None
        
        extraction_id = data.get('id')
        if not extraction_id:
            print(f"{Colors.RED}No extraction ID found in response.{Colors.RESET}")
            return None

        return poll_firecrawl_result(extraction_id, api_key, interval=5, max_attempts=120)  # Increased polling attempts

    except requests.exceptions.Timeout:
        print(f"{Colors.RED}Request timed out. The operation might still be processing in the background.{Colors.RESET}")
        print(f"{Colors.YELLOW}You may want to try again with fewer URLs or a more specific prompt.{Colors.RESET}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Request failed: {e}{Colors.RESET}")
        return None
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Failed to parse response: {e}{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.RED}Failed to extract data: {e}{Colors.RESET}")
        return None

def poll_firecrawl_result(extraction_id, api_key, interval=10, max_attempts=60):
    """Poll Firecrawl API to get the extraction result."""
    url = f"https://api.firecrawl.dev/v1/extract/{extraction_id}"
    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    print(f"{Colors.YELLOW}Waiting for extraction to complete...{Colors.RESET}")
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get('success') and data.get('data'):
                print(f"{Colors.GREEN}Data successfully extracted:{Colors.RESET}")
                print(json.dumps(data['data'], indent=2))
                return data['data']
            elif data.get('success') and not data.get('data'):
                if attempt % 6 == 0:  
                    print(f"{Colors.YELLOW}Still processing... (attempt {attempt}/{max_attempts}){Colors.RESET}")
                time.sleep(interval)
            else:
                print(f"{Colors.RED}API Error: {data.get('error', 'No error message provided')}{Colors.RESET}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"{Colors.RED}Request error: {str(e)}{Colors.RESET}")
            return None
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}JSON parsing error: {str(e)}{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
            return None

    print(f"{Colors.RED}Max polling attempts reached. Extraction did not complete in time.{Colors.RESET}")
    return None

def main():
    company = input(f"{Colors.BLUE}Enter the company name: {Colors.RESET}")
    objective = input(f"{Colors.BLUE}Enter what information you want about the company: {Colors.RESET}")
    
    serp_results = search_google(f"{company}")
    if not serp_results:
        print(f"{Colors.RED}No search results found.{Colors.RESET}")
        return
    
    selected_urls = select_urls_with_gemini(company, objective, serp_results)
    
    if not selected_urls:
        print(f"{Colors.RED}No URLs were selected.{Colors.RESET}")
        return
    
    data = extract_company_info(selected_urls, objective, company, firecrawl_api_key)
    
    if data:
        print(f"{Colors.GREEN}Extraction completed successfully.{Colors.RESET}")
    else:
        print(f"{Colors.RED}Failed to extract the requested information. Try refining your prompt or choosing a different company.{Colors.RESET}")

if __name__ == "__main__":
    main()