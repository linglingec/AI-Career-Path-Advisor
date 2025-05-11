import requests
from typing import Dict, List
import json

class RecommendationEngine:
    def __init__(self):
        self.stepik_api_url = "https://stepik.org/api/courses"
        self.hh_api_url = "https://api.hh.ru/vacancies"
        self.hh_area = 113  # Russia

    def _search_and_filter(self, query: str, level: str = None) -> List[Dict]:
        params = {"search": query, "is_public": "true"}
        try:
            resp = requests.get(self.stepik_api_url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            results = []
            level_keywords = {
                "beginner": ["введение", "beginner", "основы", "для начинающих", "introduction"],
                "intermediate": ["продвинутый", "advanced", "intermediate", "углубленный"],
                "advanced": ["специализация", "specialization", "профессионал", "pro", "expert"]
            }
            for course in data.get("courses", []):
                title = (course.get("title") or "").lower()
                summary = (course.get("summary") or "").lower()
                if level and level in level_keywords:
                    if any(kw in title or kw in summary for kw in level_keywords[level]):
                        results.append({
                            "title": course.get("title"),
                            "url": f'https://stepik.org/course/{course.get("id")}',
                            "summary": course.get("summary", "")
                        })
                else:
                    results.append({
                        "title": course.get("title"),
                        "url": f'https://stepik.org/course/{course.get("id")}',
                        "summary": course.get("summary", "")
                    })
                if len(results) >= 5:
                    break
            return results
        except Exception as e:
            return []

    def get_stepik_courses(self, query: str, level: str, skills: List[str], position: str) -> List[Dict]:
        # Define relevant keywords for Data Science/ML
        ds_keywords = ["data science", "machine learning", "python", "statistics", "deep learning", "ai", "ml"]
        # Compose search keywords from skills if possible
        search_keywords = [kw for kw in skills if kw in ds_keywords]
        if not search_keywords:
            search_keywords = ds_keywords
        results = []
        for kw in search_keywords:
            found = self._search_and_filter(kw, level)
            # Filter only courses with DS/ML keywords in title
            filtered = [c for c in found if any(dk in (c['title'] or '').lower() for dk in ds_keywords)]
            results.extend(filtered)
            if len(results) >= 5:
                break
        return results[:5]

    def get_hh_vacancies(self, position: str, level: str) -> List[Dict]:
        """Get relevant vacancies from hh.ru."""
        params = {"text": position, "area": self.hh_area, "per_page": 5}
        try:
            resp = requests.get(self.hh_api_url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for item in data.get("items", [])[:5]:
                results.append({
                    "name": item.get("name"),
                    "url": item.get("alternate_url"),
                    "snippet": item.get("snippet", {}).get("requirement", "")
                })
            return results
        except Exception as e:
            return [{"error": f"hh.ru API error: {str(e)}"}]

    def get_recommendations(self, 
                          desired_position: str,
                          experience_level: str,
                          skills: List[str]) -> Dict:
        recommendations = {
            "courses": [],
            "internships": [],
            "jobs": []
        }
        # Use improved DS/ML search for Stepik
        recommendations["courses"] = self.get_stepik_courses(
            desired_position, experience_level.lower(), skills, desired_position
        )
        # Get job recommendations
        if experience_level == "Beginner":
            recommendations["internships"] = self.get_hh_vacancies(
                f"intern {desired_position}", "beginner"
            )
        elif experience_level == "Intermediate":
            recommendations["jobs"] = self.get_hh_vacancies(
                f"junior {desired_position}", "intermediate"
            )
        else:  # Advanced
            recommendations["jobs"] = self.get_hh_vacancies(
                desired_position, "advanced"
            )
        return recommendations