"""
Prompt templates for Gemini AI resume tailoring
Separated for easy modification without touching code
"""
import json

# System instruction for Gemini
SYSTEM_INSTRUCTION = """You are an expert ATS (Applicant Tracking System) resume optimizer and career coach.

Your job is to tailor resumes to match specific job descriptions while maintaining complete authenticity.

CRITICAL RULES:
1. NEVER invent or fabricate experiences, skills, or achievements
2. ONLY enhance and rephrase existing content to match job requirements
3. Incorporate relevant keywords from the job description naturally
4. Maintain all factual information (dates, companies, titles, education)
5. Keep the original structure and organization
6. Return ONLY valid JSON - no markdown, no explanations, no preamble
7. You MAY add at most 1-2 adjacent technologies **only if** they are strongly implied by the job description and are a reasonable extension of existing skills (e.g., add Redis if already using caching + databases). Do not add unrelated technologies.

OUTPUT FORMAT:
You must return a valid JSON object matching this exact structure:
{
  "tailoredResume": { <complete resume object with enhanced content> },
  "matchedKeywords": ["keyword1", "keyword2", ...],
  "missingKeywords": ["keyword3", "keyword4", ...],
  "suggestions": ["suggestion1", "suggestion2", ...],
  "changes": ["change1", "change2", ...]
}
"""


def get_tailoring_prompt(minimal_resume: dict, job_description: str, candidate_name: str) -> str:
    """
    Generate the main tailoring prompt using minimal resume data
    
    Args:
        minimal_resume: Dict with only summary, experiences, projects, skills
        job_description: The job description text
        candidate_name: Candidate's name for logging
        
    Returns:
        Complete prompt for Gemini
    """
    return f"""
        TASK: Tailor this resume content for the job description below.

        CANDIDATE: {candidate_name}

        JOB DESCRIPTION:
        {job_description}

        RESUME CONTENT TO ENHANCE:
        {json.dumps(minimal_resume, indent=2)}

        INSTRUCTIONS:
        1. **Summary** (MAX 120 words):
        - Rewrite to align with target role
        - Incorporate key skills and requirements from JD
        - Keep it impactful and concise

        2. **Experiences** (For each company):
        - Enhance bullet points to include relevant keywords
        - Emphasize achievements matching job requirements
        - KEEP EACH BULLET UNDER 35 WORDS
        - Return in SAME ORDER as input

        3. **Projects** (For each project):
        - Enhance highlights to match technical requirements
        - Include relevant technologies from JD
        - KEEP EACH HIGHLIGHT UNDER 25 WORDS
        - Return in SAME ORDER as input

        4. **Skills**:
        - Reorder by relevance (most relevant first)
        - Add 1-2 missing adjacent technologies if strongly implied by JD
        - Keep categorized format

        CRITICAL RULES:
        - Be concise and impactful
        - Only enhance existing content, don't fabricate
        - Return content in SAME ORDER as input
        - Match companies/projects by their names exactly

        OUTPUT FORMAT (JSON ONLY):
        {{
        "summary": "Enhanced summary text",
        "experiences": [
            {{
            "company": "Company Name",
            "description": ["Enhanced bullet 1", "Enhanced bullet 2", ...]
            }}
        ],
        "projects": [
            {{
            "name": "Project Name",
            "highlights": ["Enhanced highlight 1", "Enhanced highlight 2", ...]
            }}
        ],
        "skills": {{
            "Category Name": ["skill1", "skill2", ...],
            ...
        }},
        "matchedKeywords": ["keyword1", "keyword2", ...],
        "missingKeywords": ["keyword3", "keyword4", ...],
        "suggestions": ["suggestion1", "suggestion2", ...],
        "changes": ["change1", "change2", ...]
        }}

        Return ONLY the JSON object. No markdown, no explanations.
        """


def get_keyword_extraction_prompt(job_description: str) -> str:
    """
    Generate prompt for extracting keywords from job description
    Used for initial analysis before full tailoring
    
    Args:
        job_description: The job description text
        
    Returns:
        Prompt for keyword extraction
    """
    return f"""
Extract key requirements from this job description.

JOB DESCRIPTION:
{job_description}

EXTRACT:
1. Technical skills (programming languages, frameworks, tools)
2. Soft skills (leadership, communication, etc.)
3. Required qualifications (education, certifications)
4. Experience requirements (years, domains)
5. Key responsibilities

Return ONLY a JSON object:
{{
  "technical_skills": ["skill1", "skill2", ...],
  "soft_skills": ["skill1", "skill2", ...],
  "qualifications": ["qual1", "qual2", ...],
  "experience_requirements": ["req1", "req2", ...],
  "key_responsibilities": ["resp1", "resp2", ...]
}}

No markdown, no explanations, ONLY the JSON object.
"""


# Validation prompt to ensure JSON output
JSON_ENFORCEMENT_SUFFIX = """

CRITICAL: Your response must be ONLY a valid JSON object. Do not include:
- Markdown code blocks (```json)
- Explanatory text before or after
- Any formatting except the raw JSON

Start your response with { and end with }
"""


def add_json_enforcement(prompt: str) -> str:
    """Add JSON enforcement to any prompt"""
    return prompt + JSON_ENFORCEMENT_SUFFIX
