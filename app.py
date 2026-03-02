from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from ultralytics import YOLO
from PIL import Image
import numpy as np
import base64
import io

app = FastAPI()
templates = Jinja2Templates(directory="templates")

model = YOLO("best.pt")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/detect")
async def detect(data: dict):
    image_data = data["image"]

    # Remove header
    image_data = image_data.split(",")[1]
    image_bytes = base64.b64decode(image_data)

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    results = model(np.array(image))
    plotted = results[0].plot()

    img = Image.fromarray(plotted)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")

    result_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return JSONResponse({
        "image": f"data:image/jpeg;base64,{result_base64}"
    })