from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS for all origins (adjust as needed for more restricted access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Path to the directory containing your .whl file
whl_directory = Path("/home/david/PycharmProjects/sparql-template-lib/dist")

@app.get("/whl/{filename}")
async def get_wheel_file(filename: str):
    file_path = whl_directory / filename
    logger.info(f"Requested file path: {file_path}")
    if file_path.exists():
        return FileResponse(file_path, media_type="application/octet-stream")
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050)
