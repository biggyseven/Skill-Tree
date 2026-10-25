"""Point d'entrée CLI : python main.py <commande>, dont « backup »."""
from app.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
from fastapi.responses import FileResponse

@app.get("/lab.html")
async def lab_page():
    return FileResponse("lab.html")