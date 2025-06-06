# Backend API

This directory contains the FastAPI backend for the Website Cloner AI application.

## Functionality

- Provides a `/clone` endpoint that accepts a URL.
- Calls the Firecrawl service (expected to be running locally) to scrape the URL and convert its content to Markdown.
- Sends the Markdown to the Google Gemini API (`gemini-1.5-flash` model) to generate a visually similar HTML page.
- Returns the generated HTML to the frontend.

## Setup & Running

**Note:** For full project setup, please see the main `README.md` in the root `orchid-project` directory.

1.  **Navigate to this directory:**
    ```bash
    cd orchid-project/backend
    ```

2.  **Install dependencies:**
    Make sure you have a virtual environment activated.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment:**
    Ensure you have a `.env` file in this directory with the following variables:
    ```
    GEMINI_API_KEY=your_gemini_api_key
    FIRECRAWL_HOST=http://localhost:3002
    ```

4.  **Run the server:**
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
The API will be running at `http://localhost:8000`. 