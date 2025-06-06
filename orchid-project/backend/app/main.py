from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from . import scraper
from . import llm_client
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup, Comment

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

def simplify_html_for_llm(html_content: str) -> str:
    """
    Intelligently simplifies HTML to reduce token count for an LLM
    by removing JS-animation attributes and fixing visibility issues.
    """
    if not html_content:
        return ""
        
    soup = BeautifulSoup(html_content, 'html.parser')

    for tag in soup.find_all(['script', 'noscript']):
        tag.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
        
    for tag in soup.find_all(True):
        attrs_to_remove = [key for key in tag.attrs if key.startswith('data-sr') or key.startswith('data-tilt')]
        for attr in attrs_to_remove:
            del tag[attr]

        if tag.get('class'):
            tag['class'] = [c for c in tag.get('class') if c not in ['load-hidden', 'sr']]
            if not tag['class']:
                del tag['class']

        if tag.get('style'):
            original_style = tag.get('style', '')
            import re
            style_clean = re.sub(r'(visibility|opacity|transform)\s*:[^;]+;?', '', original_style)
            
            style_clean = ' '.join(style_clean.split())
            
            if style_clean:
                tag['style'] = style_clean
            else:
                del tag['style']

    return str(soup)


class CloneRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Website Cloning API"}

@app.post("/clone")
async def clone_website(request: CloneRequest):
    try:
        source_html = await scraper.scrape_url(request.url)
        if not source_html:
            raise HTTPException(status_code=500, detail="Failed to scrape the website.")

        simplified_html = simplify_html_for_llm(source_html)
        if not simplified_html:
             raise HTTPException(status_code=500, detail="Failed to simplify the scraped HTML.")

        final_html = await llm_client.generate_html(simplified_html, request.url)
        if not final_html:
            raise HTTPException(status_code=500, detail="Failed to generate HTML from source.")

        return {"html": final_html}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 