from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from weather_service import analyze_city

app = FastAPI(title="Florida Weather Tracker API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    threshold: int
    cities: List[str]
    consecutive_days: int

@app.post("/analyze")
async def analyze_weather(request: AnalysisRequest):
    results = []
    for city in request.cities:
        res = analyze_city(city, request.threshold, request.consecutive_days)
        if "error" not in res:
            results.append(res)

    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
