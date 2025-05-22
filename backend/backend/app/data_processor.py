import spacy
import pymupdf
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util

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
        # Multilingual model for semantic similarity (English, Russian, etc.)
        self.sim_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def semantic_match(self, query: str, candidates: list, threshold: float = 0.7) -> list:
        """
        Returns candidates that are semantically similar to the query above the threshold.
        """
        if not candidates:
            return []
        emb_query = self.sim_model.encode(query, convert_to_tensor=True)
        emb_cand = self.sim_model.encode(candidates, convert_to_tensor=True)
        cos_scores = util.cos_sim(emb_query, emb_cand)[0].cpu().numpy()
        return [candidates[i] for i, score in enumerate(cos_scores) if score >= threshold]

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file."""
        doc = pymupdf.open(stream=pdf_file.read())
        text = ""
        for page in doc: # iterate the document pages
            text += "\n".join([block[4].replace("\n", " ") for block in page.get_text("blocks")])
        return text

    def extract_skills(self, text: str) -> List[str]:
        """
        Extracts skills from text using semantic similarity (multilingual) and keyword matching.
        """
        doc = self.nlp(text.lower())
        found_skills = set()
        # Semantic search for each skill in IT_SKILLS
        for skill in IT_SKILLS:
            matches = self.semantic_match(skill, [text], threshold=0.45)
            if matches:
                found_skills.add(skill)
        # Entity search (e.g., ORG, PRODUCT)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT"]:
                matches = self.semantic_match(ent.text.lower(), IT_SKILLS, threshold=0.7)
                found_skills.update(matches)
        return sorted(list(found_skills))

    def extract_education(self, text: str) -> str:
        """
        Extracts education information from text.
        """
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

    def extract_projects_section(self, text: str) -> list:
        """
        Extracts projects from resume text using semantic and keyword search.
        """
        # Simple heuristic: look for lines containing 'project' or 'проект'
        projects = []
        for line in text.splitlines():
            if any(self.semantic_match(line, [kw], threshold=0.6) for kw in ["project", "проект"]):
                projects.append(line.strip())
        return projects

    def extract_certifications_section(self, text: str) -> list:
        """
        Extracts certifications from resume text.
        """
        certs = []
        for line in text.splitlines():
            if any(self.semantic_match(line, [kw], threshold=0.6) for kw in ["certificate", "сертификат", "certification"]):
                certs.append(line.strip())
        return certs

    def extract_languages_section(self, text: str) -> list:
        """
        Extracts languages from resume text.
        """
        langs = []
        for line in text.splitlines():
            if any(self.semantic_match(line, [kw], threshold=0.6) for kw in ["language", "язык"]):
                langs.append(line.strip())
        return langs

    def extract_summary_section(self, text: str) -> str:
        """
        Extracts summary/objective from resume text.
        """
        for line in text.splitlines():
            if any(self.semantic_match(line, [kw], threshold=0.6) for kw in ["summary", "objective", "цель", "о себе"]):
                return line.strip()
        return ""

    def extract_achievements_section(self, text: str) -> list:
        """
        Extracts achievements/awards from resume text.
        """
        achievements = []
        for line in text.splitlines():
            if any(self.semantic_match(line, [kw], threshold=0.6) for kw in ["achievement", "award", "достижение", "награда"]):
                achievements.append(line.strip())
        return achievements

    def extract_interests_section(self, text: str) -> list:
        """
        Extracts interests/hobbies from resume text.
        """
        interests = []
        for line in text.splitlines():
            if any(self.semantic_match(line, [kw], threshold=0.6) for kw in ["interest", "hobby", "интерес", "хобби"]):
                interests.append(line.strip())
        return interests

    def extract_publications_section(self, text: str) -> list:
        """
        Extracts publications from resume text.
        """
        pubs = []
        for line in text.splitlines():
            if any(self.semantic_match(line, [kw], threshold=0.6) for kw in ["publication", "публикация"]):
                pubs.append(line.strip())
        return pubs

    def extract_volunteer_section(self, text: str) -> list:
        """
        Extracts volunteer/extracurricular from resume text.
        """
        vols = []
        for line in text.splitlines():
            if any(self.semantic_match(line, [kw], threshold=0.6) for kw in ["volunteer", "extracurricular", "волонтер", "внеучебная"]):
                vols.append(line.strip())
        return vols

    def extract_contacts_section(self, text: str) -> dict:
        """
        Extracts contacts (email, phone, social) from resume text.
        """
        import re
        contacts = {}
        email = re.search(r'[\w\.-]+@[\w\.-]+', text)
        phone = re.search(r'\+?\d[\d\-\s\(\)]{7,}\d', text)
        if email:
            contacts['email'] = email.group(0)
        if phone:
            contacts['phone'] = phone.group(0)
        # Socials (simple heuristic)
        socials = re.findall(r'(linkedin\.com/\S+|github\.com/\S+|vk\.com/\S+)', text, re.IGNORECASE)
        if socials:
            contacts['socials'] = socials
        return contacts

    def extract_structured_resume(self, text: str) -> dict:
        """
        Returns structured resume with all relevant blocks for recommendations.
        """
        return {
            "experience": self.extract_experience_section(text),
            "education": self.extract_education_section(text),
            "skills": self.extract_skills_section(text),
            "projects": self.extract_projects_section(text),
            "certifications": self.extract_certifications_section(text),
            "languages": self.extract_languages_section(text),
            "summary": self.extract_summary_section(text),
            "achievements": self.extract_achievements_section(text),
            "interests": self.extract_interests_section(text),
            "publications": self.extract_publications_section(text),
            "volunteer": self.extract_volunteer_section(text),
            "contacts": self.extract_contacts_section(text)
        }

    def extract_courses_grades_credits(self, text: str) -> list:
        """
        Extracts courses, grades, and credits from transcript text.
        """
        import re
        courses = []
        # Example: MA030111 Introduction to Data Science 3 A 108 Term 1B 2022-2023
        course_pattern = re.compile(
            r'([A-Z]{2,}\d{6,})\s+([A-Za-zА-Яа-я0-9 ,\-&]+)\s+(\d+)\s+([A-FPassFail]+)\s+(\d+)\s+Term\s+\d+[A-B]?\s+\d{4}-\d{4}',
            re.IGNORECASE
        )
        for match in course_pattern.finditer(text):
            code, name, ects, grade, hours = match.groups()
            courses.append({
                "code": code,
                "name": name.strip(),
                "ects": ects,
                "grade": grade,
                "hours": hours
            })
        return courses

    def extract_personal_info_from_transcript(self, text: str) -> dict:
        """
        Extracts personal info (full name, date of birth, student ID, etc.) from transcript text.
        """
        import re
        info = {}
        fio_match = re.search(r"Student ([A-Za-zА-Яа-я ]+)", text)
        if fio_match:
            info["full_name"] = fio_match.group(1).strip()
        dob_match = re.search(r"Date of Birth ([0-9]{4}-[A-Za-z]{3}-[0-9]{2})", text)
        if dob_match:
            info["date_of_birth"] = dob_match.group(1)
        id_match = re.search(r"Student ID ([0-9A-Za-z-]+)", text)
        if id_match:
            info["student_id"] = id_match.group(1)
        return info

    def extract_degree_from_transcript(self, text: str) -> str:
        """
        Extracts degree/program from transcript (e.g., MSc Educational Program Data Science).
        """
        import re
        degree_match = re.search(r'Completion Level (.+?) Educational Program (.+?) Field of Knowledge', text)
        if degree_match:
            return degree_match.group(1).strip() + ' ' + degree_match.group(2).strip()
        return ""

    def extract_major_program(self, text: str) -> str:
        """
        Extracts major/program from transcript text.
        """
        import re
        match = re.search(r'Program ([A-Za-zА-Яа-я0-9 ]+?) Field of Knowledge', text)
        if match:
            return match.group(1).strip()
        return ""

    def extract_dates(self, text: str) -> dict:
        """
        Extracts matriculation and completion dates from transcript text.
        """
        import re
        dates = {}
        matric = re.search(r'Matriculation Date ([0-9]{4}-[A-Za-z]{3}-[0-9]{2})', text)
        if matric:
            dates['matriculation'] = matric.group(1)
        compl = re.search(r'Date of Completion / Expected Date of ([0-9]{4}-[A-Za-z]{3}-[0-9]{2})', text)
        if compl:
            dates['completion'] = compl.group(1)
        return dates

    def extract_structured_transcript(self, text: str) -> dict:
        """
        Returns structured transcript with all relevant blocks for recommendations.
        """
        import re
        gpa = re.search(r'GPA[:\s]+([0-9\.]+)', text, re.IGNORECASE)
        university = re.search(r'(Skolkovo Institute of Science and Technology|[A-Za-zА-Яа-я ]+University)', text)
        lang_instr = re.search(r'language of instruction is ([A-Za-z]+)', text, re.IGNORECASE)
        return {
            "courses": self.extract_courses_grades_credits(text),
            "personal_info": self.extract_personal_info_from_transcript(text),
            "degree": self.extract_degree_from_transcript(text),
            "major_program": self.extract_major_program(text),
            "dates": self.extract_dates(text),
            "gpa": gpa.group(1) if gpa else None,
            "university": university.group(0) if university else None,
            "language_of_instruction": lang_instr.group(1) if lang_instr else None
        }

    def extract_experience_section(self, text: str) -> list:
        """
        Extracts work experience entries from resume text (company, position, years).
        """
        import re
        experience = []
        # Example: Company, Position, 2020-2022
        exp_pattern = re.compile(
            r'([A-Za-zА-Яа-я0-9 .,&-]+),\s*([A-Za-zА-Яа-я0-9 .,&-]+),\s*(\d{4})[-–](\d{4}|Present|Now|Настоящее время)',
            re.IGNORECASE
        )
        for match in exp_pattern.finditer(text):
            company, position, start, end = match.groups()
            experience.append({
                "company": company.strip(),
                "position": position.strip(),
                "start": start,
                "end": end
            })
        return experience

    def extract_education_section(self, text: str) -> list:
        """
        Extracts education entries from resume text (institution, degree, years).
        """
        import re
        education = []
        edu_pattern = re.compile(
            r'([A-Za-zА-Яа-я0-9 .,&-]+),\s*([A-Za-zА-Яа-я0-9 .,&-]+),\s*(\d{4})[-–](\d{4}|Present|Now|Настоящее время)',
            re.IGNORECASE
        )
        for match in edu_pattern.finditer(text):
            institution, degree, start, end = match.groups()
            education.append({
                "institution": institution.strip(),
                "degree": degree.strip(),
                "start": start,
                "end": end
            })
        return education

    def extract_skills_section(self, text: str) -> list:
        """
        Extracts skills from resume text (comma, semicolon, or line separated lists, multilingual).
        """
        import re
        skills = []
        # Look for a block after 'skills' or 'навыки'
        skills_block = re.search(r'(skills|навыки)[:\n]+([\s\S]+?)(\n\w+:|\n\n|$)', text, re.IGNORECASE)
        if skills_block:
            block = skills_block.group(2)
            # Split by comma, semicolon, bullet, or newline
            for skill in re.split(r'[\n,;•·]', block):
                skill = skill.strip()
                if skill and len(skill) < 40:  # filter out noise
                    skills.append(skill)
        return skills