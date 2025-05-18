import spacy
import pymupdf
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup

# Example list of IT skills for keyword search
IT_SKILLS = [
    'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'sql', 'html', 'css',
    'docker', 'kubernetes', 'git', 'linux', 'tensorflow', 'pytorch', 'scikit-learn',
    'pandas', 'numpy', 'react', 'angular', 'vue', 'django', 'flask', 'fastapi',
    'aws', 'azure', 'gcp', 'machine learning', 'deep learning', 'nlp', 'data analysis',
    'data science', 'computer vision', 'opencv', 'bash', 'shell', 'matlab', 'r',
    'scala', 'go', 'swift', 'kotlin', 'php', 'ruby', 'spark', 'hadoop', 'tableau',
    'powerbi', 'excel', 'jira', 'agile', 'scrum', 'rest', 'graphql', 'api', 'sqlalchemy'
]

class DataProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file."""
        doc = pymupdf.open(stream=pdf_file.read())
        text = ""
        for page in doc: # iterate the document pages
            text += "\n".join([block[4].replace("\n", " ") for block in page.get_text("blocks")])
        return text

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using NLP and keyword matching."""
        doc = self.nlp(text.lower())
        found_skills = set()
        # Keyword search
        for skill in IT_SKILLS:
            if skill in text.lower():
                found_skills.add(skill)
        # Entity search (e.g., ORG, PRODUCT)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT"] and ent.text.lower() in IT_SKILLS:
                found_skills.add(ent.text.lower())
        return sorted(list(found_skills))

    def extract_education(self, text: str) -> str:
        """Extract education information from text."""
        # Simple search by keywords
        education_keywords = {
            "BSc": ["bachelor", "bsc", "бакалавр"],
            "MSc": ["master", "msc", "магистр"],
            "PhD": ["phd", "кандидат наук"],
        }
        degrees = dict()
        for line in text.splitlines():
            for degree, degree_kw in education_keywords.items():
                for kw in degree_kw:
                    if kw.lower() in line.lower():
                        degrees[degree] = line
                        break

        return ", ".join(degrees.keys())

    def analyze_github_profile(self, github_url: Optional[str]) -> Dict:
        """Analyze GitHub profile and extract relevant information using GitHub API."""
        if not github_url:
            return {}
        # Remove @ and spaces if present
        github_url = github_url.strip().replace('@', '')
        username = github_url.rstrip('/').split('/')[-1]
        api_url = f"https://api.github.com/users/{username}/repos"
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(api_url, headers=headers)
        # Log status and response body for debugging
        if response.status_code != 200:
            return {
                "error": f"GitHub API error: {response.status_code}",
                "detail": response.json() if response.content else {},
                "api_url": api_url,
                "username": username
            }
        repos = response.json()
        if not isinstance(repos, list):
            return {"error": "Unexpected response from GitHub API", "raw": repos}
        languages = set()
        stars = 0
        forks = 0
        for repo in repos:
            lang = repo.get('language')
            if lang:
                languages.add(lang.lower())
            stars += repo.get('stargazers_count', 0)
            forks += repo.get('forks_count', 0)
        activity_score = len(repos) + stars + forks
        return {
            "repositories": len(repos),
            "languages": sorted(list(languages)),
            "stars": stars,
            "forks": forks,
            "activity_score": activity_score,
            "username": username
        }

    def calculate_experience_level(self, profile_data: Dict) -> str:
        score = 0
        # Example logic: add points for each feature
        if profile_data.get("education"):
            score += 10
        if profile_data.get("skills"):
            score += min(len(profile_data["skills"]) * 2, 20)
        github = profile_data.get("github_data", {})
        score += min(github.get("repositories", 0) * 2, 20)
        score += min(github.get("stars", 0), 10)
        score += min(github.get("forks", 0), 10)
        score += min(github.get("activity_score", 0) // 5, 10)
        # Thresholds
        if score < 20:
            return "Beginner"
        elif score < 50:
            return "Intermediate"
        else:
            return "Advanced"

    def process_profile(self, 
                       transcript_text: str,
                       resume_text: str,
                       github_profile: Optional[str] = None) -> Dict:
        skills = self.extract_skills(resume_text)
        education = self.extract_education(transcript_text)
        github_data = self.analyze_github_profile(github_profile)
        profile_data = {
            "skills": skills,
            "education": education,
            "github_data": github_data
        }
        experience_level = self.calculate_experience_level(profile_data)
        return {
            "skills": skills,
            "education": education,
            "experience_level": experience_level,
            "github_data": github_data
        }