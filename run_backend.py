import uvicorn
from backend.config import PORT

if __name__ == "__main__":
    print(f"Avvio Sneaker Showcase API su http://localhost:{PORT}")
    print(f"Documentazione Swagger interattiva su http://localhost:{PORT}/docs")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=PORT, reload=True)
