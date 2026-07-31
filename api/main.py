from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import discover

app = FastAPI("American History Helper")

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:3000, http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"]
)

app.include_router(discover.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)