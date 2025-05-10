# AI Career Path Advisor

An intelligent system that provides personalized career path recommendations for IT students and recent graduates based on their profile and desired position.

## Features

- Profile analysis based on transcript and resume
- GitHub profile integration
- Experience level assessment
- Personalized course recommendations from Stepik
- Job and internship recommendations from hh.ru
- Modern web interface

## Setup

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

4. Run the backend server:
```bash
cd backend
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── data_processor.py    # Data processing and analysis
│   └── recommendation_engine.py  # Recommendation system
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Endpoints

- `POST /analyze-profile`: Analyze user profile and get recommendations
  - Required fields:
    - `desired_position`: Target job position
    - `transcript`: Academic transcript (PDF)
    - `resume`: Resume/CV (PDF)
  - Optional fields:
    - `github_profile`: GitHub profile URL

- `GET /health`: Health check endpoint

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 