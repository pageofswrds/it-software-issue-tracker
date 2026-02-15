# IT Software Issue Tracker

Crawls public forums for reported issues with enterprise software, classifies them by severity using an LLM, and displays them in a searchable dashboard.

## Prerequisites

- Docker
- Node.js 20+
- Python 3.11+

## API Keys

The crawler requires three sets of credentials:

| Key | Where to get it | Used for |
|-----|----------------|----------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) | Issue classification |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/) | Embeddings + semantic search |
| `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) | Crawling Reddit |

## Setup

```bash
# 1. Start PostgreSQL
docker-compose up -d

# 2. Set up the API
cd api
cp .env.example .env        # edit with your OPENAI_API_KEY
npm install

# 3. Set up the crawler
cd ../crawler
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # edit with your API keys

# 4. Set up the frontend
cd ../web
npm install
```

## Run

Open three terminals:

```bash
# Terminal 1: API
cd api && npm run dev

# Terminal 2: Frontend
cd web && npm run dev

# Terminal 3: Crawl (when ready)
cd crawler && source .venv/bin/activate
python main.py crawl                        # crawl all apps
python main.py crawl --app "Adobe Acrobat"  # crawl one app
```

Then open http://localhost:3000.

## CLI Commands

```bash
python main.py list-apps                                          # list monitored apps
python main.py add-app --name "Firefox" --vendor "Mozilla" \
  --keywords "firefox,firefox browser"                            # add an app
python main.py crawl                                              # crawl all apps
```
