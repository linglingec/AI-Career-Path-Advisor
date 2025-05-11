# AI Career Path Advisor

AI-powered system that analyzes a student's or graduate's profile (transcript, resume, GitHub) and recommends relevant courses, internships, and jobs.

## Features

- **Profile Analysis**
  - Extracts skills from resume using NLP
  - Analyzes education level from transcript
  - Evaluates GitHub activity and repositories
  - Calculates experience level based on multiple factors

- **Recommendations**
  - Courses from Stepik platform
  - Internships and jobs from hh.ru
  - Filtered by experience level and desired position

## Project Structure

```
backend/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── data_processor.py    # Profile analysis logic
│   │   └── recommendation_engine.py  # Course and job recommendations
│   ├── requirements.txt
│   └── README.md
└── README.md
```

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-Career-Path-Advisor
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd backend/backend
   pip install -r requirements.txt
   ```

4. **Install spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

The server will start at `http://localhost:8000`

## API Endpoints

### Analyze Profile
```
POST /analyze-profile
```
Analyzes user profile and returns recommendations.

**Request Parameters:**
- `desired_position`: Desired job position
- `transcript`: PDF file with academic transcript
- `resume`: PDF file with resume
- `github_profile`: (Optional) GitHub profile URL

**Response:**
```json
{
    "status": "success",
    "message": "Profile analysis completed",
    "data": {
        "experience_level": "Intermediate",
        "skills": ["python", "machine learning", ...],
        "education": "Bachelor's Degree",
        "github_data": {
            "repositories": 10,
            "languages": ["python", "javascript"],
            "stars": 5,
            "forks": 3,
            "activity_score": 18
        },
        "recommendations": {
            "courses": [...],
            "internships": [...],
            "jobs": [...]
        }
    }
}
```

### Health Check
```
GET /health
```
Returns server health status.

## Development

- The project uses FastAPI for the backend
- Profile analysis is done using spaCy for NLP
- Course recommendations are fetched from Stepik API
- Job recommendations are fetched from hh.ru API

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
