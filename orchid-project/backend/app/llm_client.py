import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_llm_client():
    """Returns a configured Gemini client."""
    return genai.GenerativeModel('gemini-1.5-flash')

async def generate_html(source_html: str, original_url: str) -> str:
    """
    Generates a single, self-contained HTML file from the source HTML of a website.
    """
    model = get_llm_client()
    prompt = f"""
You are an expert web developer tasked with converting a website's source HTML into a single, self-contained file. The original URL of the page was: {original_url}

**GOAL:**
Analyze the provided HTML source code and create a new HTML file that visually replicates the original page, ensuring all assets are linked correctly.

**INSTRUCTIONS:**
1.  **Consolidate CSS:** Combine all CSS into a single `<style>` block in the `<head>`.
2.  **Handle Image Paths:** This is critical. For all `<img>` tags, inspect the `src` attribute. If it is a relative path (e.g., '/images/pic.jpg' or 'assets/logo.png'), you **MUST** convert it into an absolute URL using the original page URL as a base. For example, if the original URL is `https://example.com/about/` and you see `<img src="/images/header.png">`, the new tag must be `<img src="https://example.com/images/header.png">`.
3.  **Remove Scripts:** Remove all JavaScript (`<script>` tags) and any elements related to script execution, such as `onclick` attributes or `div`s with classes like `js-tilt-glare`. The output must be purely static HTML and CSS.
4.  **Ensure Visibility:** All content should be visible. In the CSS, ensure there are no styles like `opacity: 0` or `visibility: hidden` that would hide text. If you find them, override them to make the content visible (e.g., `opacity: 1 !important;`).
5.  **Self-Contained:** The final file must be a single HTML file. Do not embed image data as base64. Link to the absolute URLs as instructed above.

**SOURCE HTML CONTENT:**
---
{source_html}
---

Generate only the complete, consolidated HTML code for the new file.
"""
    try:
        response = await model.generate_content_async(prompt)
        
        if response.text:
            cleaned_html = response.text.strip()
            if cleaned_html.startswith("```html"):
                cleaned_html = cleaned_html[7:]
            if cleaned_html.endswith("```"):
                cleaned_html = cleaned_html[:-3]
            
            return cleaned_html.strip()
        else:
            return "<html><body><p>Error: Could not generate HTML. The response from the model was empty.</p></body></html>"
    except Exception as e:
        print(f"Gemini API call failed. Details: {e}")
        return f"<html><body><h1>Error</h1><p>Failed to generate the cloned page. The AI model returned an error.</p><pre>{e}</pre></body></html>" 