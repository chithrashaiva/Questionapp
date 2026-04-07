# 🐍 FastAPI Backend

This is the backend server for your Quiz App. It handles question fetching, persistent score storage in a SQLite database, and leaderboard logic.

## Deployment Details

- **Framework**: FastAPI
- **Database**: SQLite (via SQLAlchemy)
- **Port**: Automatic by Render (`$PORT`), default `8000` locally.

## Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start server
uvicorn main:app --reload
```

## Render Config

- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
