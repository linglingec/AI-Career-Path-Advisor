import requests
from typing import Dict, List
import json
import re

class RecommendationEngine:
    def __init__(self):
        self.stepik_api_url = "https://stepik.org/api/courses"
        self.hh_api_url = "https://api.hh.ru/vacancies"
        self.hh_area = 113  # Russia

    def is_russian(self, text):
        cyrillic = len(re.findall(r'[а-яА-ЯёЁ]', text))
        latin = len(re.findall(r'[a-zA-Z]', text))
        return cyrillic > latin and cyrillic > 0

    def is_english(self, text):
        latin = len(re.findall(r'[a-zA-Z]', text))
        cyrillic = len(re.findall(r'[а-яА-ЯёЁ]', text))
        return latin > cyrillic and latin > 0

    def is_kazakh(self, text):
        kazakh_letters = "әғқңөұүһі"
        return any(ch in text for ch in kazakh_letters)

    def _search_and_filter(self, query: str, level: str = None, lang: str = 'ru') -> List[Dict]:
        params = {"search": query, "is_public": "true"}
        try:
            resp = requests.get(self.stepik_api_url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            results = []
            exclude_keywords = [
                "введение", "beginner", "основы", "для начинающих", "introduction",
                "егэ", "школьный", "с нуля", "новичок"
            ]
            include_keywords = [
                "data science", "machine learning", "deep learning", "statistics", "analysis",
                "python", "ml", "ai", "specialization", "advanced", "pro", "expert", "intermediate"
            ]
            for course in data.get("courses", []):
                title = (course.get("title") or "").lower()
                summary = (course.get("summary") or "").lower()
                # Языковой фильтр: только русский или английский, исключая казахский
                if self.is_kazakh(title + summary):
                    continue
                if not (self.is_russian(title + summary) or self.is_english(title + summary)):
                    continue
                # Фильтрация по уровню
                if level in ["intermediate", "advanced"]:
                    if any(kw in title or kw in summary for kw in exclude_keywords):
                        continue
                    if not any(kw in title or kw in summary for kw in include_keywords):
                        continue
                if level == "beginner":
                    if not any(kw in title or kw in summary for kw in exclude_keywords):
                        continue
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

    def get_position_keywords(self, position: str) -> List[str]:
        position = position.lower()
        if "data scientist" in position or "data science" in position:
            return [
                "data science", "machine learning", "ml", "deep learning", "нейронные сети", "статистика",
                "анализ данных", "big data", "pandas", "numpy", "scikit-learn", "regression", "classification",
                "clustering", "ai", "data analysis", "data visualization", "matplotlib", "feature engineering",
                "kaggle", "data mining", "time series", "nlp", "natural language processing", "tensorflow", "pytorch"
            ]
        # Можно добавить другие позиции и их ключевые слова
        return []

    def get_stepik_courses(self, query: str, level: str, skills: List[str], position: str) -> List[Dict]:
        if level == "advanced":
            return []
        thematic_keywords = self.get_position_keywords(position)
        if not thematic_keywords:
            thematic_keywords = ["python"]  # fallback
        search_keywords = [kw for kw in skills if kw in thematic_keywords]
        if not search_keywords:
            search_keywords = thematic_keywords
        results = []
        for kw in search_keywords:
            found = self._search_and_filter(kw, level)
            # Фильтруем только курсы, где есть тематические слова для позиции
            filtered = [c for c in found if any(dk in (c['title'] or '').lower() or dk in (c['summary'] or '').lower() for dk in thematic_keywords)]
            results.extend(filtered)
            if len(results) >= 5:
                break
        return results[:5]

    def get_hh_vacancies(self, position: str, level: str) -> List[Dict]:
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
        recommendations["courses"] = self.get_stepik_courses(
            desired_position, experience_level.lower(), skills, desired_position
        )
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