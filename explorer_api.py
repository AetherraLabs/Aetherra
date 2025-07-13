# explorer_api.py

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

# Change this path to your actual Aetherra project root
BASE_DIR = Path("C:\\Users\\enigm\\Desktop\\Aetherra Project").resolve()


@app.get("/tree")
def list_directory(path: str = ""):
    try:
        target_path = (BASE_DIR / path).resolve()
        if not target_path.is_dir():
            return JSONResponse(
                status_code=400, content={"error": "Invalid directory path"}
            )

        items = []
        for item in sorted(target_path.iterdir()):
            items.append(
                {"name": item.name, "type": "dir" if item.is_dir() else "file"}
            )

        return {"path": str(target_path.relative_to(BASE_DIR)), "items": items}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/file")
def get_file(path: str = Query(...)):
    try:
        file_path = (BASE_DIR / path).resolve()
        if not file_path.exists() or file_path.is_dir():
            return JSONResponse(
                status_code=400, content={"error": "File not found or is a directory"}
            )

        return FileResponse(str(file_path))
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/read")
def read_file_content(path: str = Query(...), lines: int = 200):
    try:
        file_path = (BASE_DIR / path).resolve()
        if not file_path.exists() or file_path.is_dir():
            return JSONResponse(
                status_code=400, content={"error": "File not found or is a directory"}
            )

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.readlines()[:lines]

        return {"path": str(file_path.relative_to(BASE_DIR)), "lines": content}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run("explorer_api:app", host="127.0.0.1", port=8080, reload=True)
