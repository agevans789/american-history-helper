American History Helper

This fullstack application is designed to pull sources about topics from Internet Archive about American History.
Simultaneously, the "Related Topics" tab pull sources for the context of the time (ie. music, fashion, etc.)

Backend: Python 3.11, FastAPI Async, HTTPX Clients, Pydantic DTO Schemas
Frontend: Vite JS, React JS
Database architecture: SQLite, SQLAlchemy
API: Internet Archive

1. Set up backend

install system dependencies (fastapi, uvicorn, httpx, pydantic, sqlalchemy, aiosqlite)

2. Populate database

run python seed.py to have the information within this seed file inform the rest of the backend

3. Set up backend API server

Start Uvicorn engine with uvicorn api.main:app --reload
This half of the terminal will show the backend processes

4. Set up frontend

in separate frontend terminal, install node modules with npm install
open browser with npm run dev 

Core Functionality
-displays top 10 historical records related to searched keyword 
-each record card links back to the original on Internet Archive
-tracks keywords to match related topics in literature, music, etc. to the specific era of the topic
-provides profile management with a secure login