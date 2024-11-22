from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from uhub import uhub_ai_assistant

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from emital import extract_environmental_data  # Import the data extraction function
app = FastAPI()

# CORS configuration
origins = ["*"]

app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

@app.get("/")
async def root():
   return uhub_ai_assistant("Hi there!")

@app.post("/assistant")
async def assistant(user_query: str):
    response = uhub_ai_assistant(user_query)
    print(f"Input Data:{user_query}")
    print(response)
    return {"response": response}

# Set up templates directory
templates = Jinja2Templates(directory="templates")


@app.get("/emit", response_class=HTMLResponse)
async def emit_form(request: Request):
    return templates.TemplateResponse("emit_form.html", {"request": request})


@app.post("/emit", response_class=HTMLResponse)
async def emit_predict(request: Request, longitude: float = Form(...), latitude: float = Form(...)):
    # Extract and enrich environmental data using emital.py
    result = extract_environmental_data(latitude, longitude)
    
    # Return the result to be displayed on the HTML page
    return templates.TemplateResponse("emit_form.html", {"request": request, "result": result})
