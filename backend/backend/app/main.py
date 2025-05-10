from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from app.data_processor import DataProcessor
from app.recommendation_engine import RecommendationEngine
app = FastAPI(title="AI Career Path Advisor")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our services
data_processor = DataProcessor()
recommendation_engine = RecommendationEngine()

class UserProfile(BaseModel):
    desired_position: str
    skills: List[str]
    education: str
    experience_level: str
    github_profile: Optional[str] = None

@app.post("/analyze-profile")
async def analyze_profile(
    desired_position: str = Form(...),
    transcript: UploadFile = File(...),
    resume: UploadFile = File(...),
    github_profile: Optional[str] = Form(None)
):
    # Process uploaded files
    transcript_text = data_processor.extract_text_from_pdf(transcript.file)
    resume_text = data_processor.extract_text_from_pdf(resume.file)
    
    # Process profile data
    profile_data = data_processor.process_profile(
        transcript_text=transcript_text,
        resume_text=resume_text,
        github_profile=github_profile
    )
    
    # Get recommendations
    recommendations = recommendation_engine.get_recommendations(
        desired_position=desired_position,
        experience_level=profile_data["experience_level"],
        skills=profile_data["skills"]
    )
    
    return {
        "status": "success",
        "message": "Profile analysis completed",
        "data": {
            "experience_level": profile_data["experience_level"],
            "skills": profile_data["skills"],
            "education": profile_data["education"],
            "github_data": profile_data["github_data"],
            "recommendations": recommendations
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 