import requests
from typing import Dict, List
import json

class RecommendationEngine:
    def __init__(self):
        self.stepik_api_url = "https://stepik.org/api/courses"
        self.hh_api_url = "https://api.hh.ru/vacancies"
        self.hh_area = 113  # Russia

    def get_stepik_courses(self, query: str, level: str) -> List[Dict]:
        """Get relevant courses from Stepik."""
        params = {"search": query, "is_public": "true"}
        try:
            resp = requests.get(self.stepik_api_url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for course in data.get("courses", [])[:5]:
                results.append({
                    "title": course.get("title"),
                    "url": f'https://stepik.org/course/{course.get("id")}',
                    "summary": course.get("summary", "")
                })
            return results
        except Exception as e:
            return [{"error": f"Stepik API error: {str(e)}"}]

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
        """Get personalized recommendations based on user profile."""
        recommendations = {
            "courses": [],
            "internships": [],
            "jobs": []
        }
        # Get courses based on experience level
        if experience_level == "Beginner":
            recommendations["courses"] = self.get_stepik_courses(
                f"basics {desired_position}", "beginner"
            )
        elif experience_level == "Intermediate":
            recommendations["courses"] = self.get_stepik_courses(
                f"advanced {desired_position}", "intermediate"
            )
        else:  # Advanced
            recommendations["courses"] = self.get_stepik_courses(
                f"specialized {desired_position}", "advanced"
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