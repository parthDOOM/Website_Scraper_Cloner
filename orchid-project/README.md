# Website Cloner AI

This project is a full-stack web application that uses AI to create a visual clone of any given public website. It consists of a Next.js frontend and a Python FastAPI backend.

The user provides a URL to the frontend, which sends a request to the backend. The backend then uses Firecrawl to scrape the website's content into markdown format and then feeds that markdown to an AI model (Google's Gemini) to generate a single, self-contained HTML file that visually mimics the original site.

## Project Structure

```
orchid-project/
├── backend/       # FastAPI application
│   ├── app/
│   └── ...
├── frontend/      # Next.js application
│   ├── pages/
│   └── ...
└── README.md      # This file
```

## Prerequisites

- Docker and Docker Compose (for running the Firecrawl service)
- Python 3.8+ and `pip`
- Node.js 18+ and `npm` (or `yarn`/`pnpm`)

## Setup & Running the Application

Follow these steps in order to get the full application running locally.

### 1. Start the Firecrawl Service

The Firecrawl scraping service must be running in the background.

```bash
cd ../firecrawl

docker-compose up -d
```
This will start the Firecrawl API, which the backend depends on. It runs on port 3002.

### 2. Set Up and Run the Backend

The backend is a FastAPI server that handles the core logic.

```bash
cd ../orchid-project/backend

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
```

Now, open the `.env` file and add your Google Gemini API key:
```.env
GEMINI_API_KEY=your_gemini_api_key_here
FIRECRAWL_HOST=http://localhost:3002
```

Finally, run the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Set Up and Run the Frontend

The frontend is a Next.js application.

```bash
cd ../frontend

npm install

npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000). You can now open this URL in your browser and use the application. 