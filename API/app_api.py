from fastapi import HTTPException, FastAPI,status
from API.router_api import router as service_router
import uvicorn

app = FastAPI(title="My Ap", version="0.0.1")
app.include_router(service_router)

@app.get("/health")
def health()->dict:
    return {"status":"ok"}

def run_server():
    uvicorn.run(
        app="API.app_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    run_server()
