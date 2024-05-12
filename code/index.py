import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "backend connected"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
