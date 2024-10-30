from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from uhub import uhub_ai_assistant
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
   return response