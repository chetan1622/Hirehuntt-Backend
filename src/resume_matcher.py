import os
import re
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Predefined list of standard tools/skills for Data Science & Data Analyst roles
COMMON_SKILLS = [
    "python", "sql", "r language", "tableau", "power bi", "powerbi", "excel", "pandas", "numpy", 
    "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras", "machine learning", "deep learning", 
    "nlp", "natural language processing", "computer vision", "statistics", "probability", "big data", 
    "spark", "hadoop", "aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "tableau public",
    "data visualization", "data wrangling", "data cleaning", "etl", "data warehousing", "snowflake", 
    "redshift", "bigquery", "postgres", "postgresql", "mysql", "mongodb", "seaborn", "matplotlib", 
    "regression", "classification", "clustering", "time series", "a/b testing", "ab testing", "airflow", 
    "dashboard", "excel macros", "vba", "dax", "power query", "predictive modeling", "spss", "sas"
]

def extract_text_from_pdf(pdf_path):
    """Extracts all text from a PDF file."""
    if not os.path.exists(pdf_path):
        return ""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def clean_text(text):
    """Cleans text by converting to lowercase and removing punctuation/special chars."""
    text = text.lower()
    # Replace newlines/tabs with space
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep letters, numbers, and common symbols (like c++, c#)
    text = re.sub(r'[^a-z0-9\s\+\#\-\.]', '', text)
    return text.strip()

class ResumeMatcher:
    def __init__(self, ds_resume_path=None, da_resume_path=None):
        self.ds_resume_text = ""
        self.da_resume_text = ""
        
        # Load resumes if paths are provided
        if ds_resume_path:
            raw_text = extract_text_from_pdf(ds_resume_path) if ds_resume_path.lower().endswith('.pdf') else self._read_txt(ds_resume_path)
            self.ds_resume_text = clean_text(raw_text)
            
        if da_resume_path:
            raw_text = extract_text_from_pdf(da_resume_path) if da_resume_path.lower().endswith('.pdf') else self._read_txt(da_resume_path)
            self.da_resume_text = clean_text(raw_text)

    def _read_txt(self, path):
        if not os.path.exists(path):
            return ""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file {path}: {e}")
            return ""

    def calculate_match(self, job_desc_text):
        """
        Calculates similarity scores of a job description against both resumes.
        Returns a dict with scores, the best matching profile, and missing keywords.
        """
        cleaned_jd = clean_text(job_desc_text)
        if not cleaned_jd:
            return {"ds_score": 0, "da_score": 0, "best_match": "None", "score": 0, "missing_keywords": []}
            
        ds_score = 0
        da_score = 0
        
        # We calculate cosine similarity using TF-IDF
        if self.ds_resume_text:
            ds_score = self._compute_cosine_similarity(self.ds_resume_text, cleaned_jd)
        if self.da_resume_text:
            da_score = self._compute_cosine_similarity(self.da_resume_text, cleaned_jd)
            
        best_match = "Data Science" if ds_score >= da_score else "Data Analyst"
        best_score = max(ds_score, da_score)
        best_resume_text = self.ds_resume_text if ds_score >= da_score else self.da_resume_text
        
        # Find missing keywords from the best matching profile
        missing = self._find_missing_keywords(best_resume_text, cleaned_jd)
        
        return {
            "ds_score": int(ds_score * 100),
            "da_score": int(da_score * 100),
            "best_match": best_match if best_score > 0 else "None",
            "score": int(best_score * 100),
            "missing_keywords": missing
        }

    def _compute_cosine_similarity(self, resume_text, jd_text):
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf = vectorizer.fit_transform([resume_text, jd_text])
            similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])
            return float(similarity[0][0])
        except Exception as e:
            print(f"Similarity error: {e}")
            return 0.0

    def _find_missing_keywords(self, resume_text, jd_text):
        """Finds common data science/analyst skills present in the JD but not in the resume."""
        missing = []
        for skill in COMMON_SKILLS:
            # Check if skill exists in job description (using word boundary check)
            # Escaping skill for regex safety (e.g. c++, c#)
            escaped_skill = re.escape(skill)
            
            # Simple match in JD
            if re.search(r'\b' + escaped_skill + r'\b', jd_text):
                # Now check if it is missing in the resume
                if not re.search(r'\b' + escaped_skill + r'\b', resume_text):
                    missing.append(skill.title())
        return missing
