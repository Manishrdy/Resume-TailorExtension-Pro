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
3. Incorporate relevant keywords from the job description naturally, including soft skills (team player, cross-functional collaboration, etc.)
4. Maintain all factual information (dates, companies, titles, education)
5. Keep the original structure and organization
6. Return ONLY valid JSON - no markdown, no explanations, no preamble
7. For skills: ADD 70-80% of missing tech skills from JD that are related to existing skills. Include related keywords (e.g., if resume has React, add React Hooks, Redux, etc. from JD)
8. All bullet points MUST be between 16-30 words

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
        - Include soft skills from JD (e.g., "team player", "cross-functional collaboration", "leadership")
        - Keep it impactful and concise

        2. **Experiences** (For each company):
        - Enhance bullet points to include relevant keywords from JD
        - Emphasize achievements matching job requirements
        - CRITICAL: Each bullet point MUST be between 16-30 words
        - Incorporate 70-80% of missing tech skills from JD that are related to existing technologies
        - Include soft skills and team-related keywords from JD (e.g., "cross-functional teams", "collaborated", "mentored")
        - If resume mentions React and JD has React-related keywords missing from resume (e.g., "React Hooks", "Redux", "React Testing Library"), naturally include them where applicable
        - Return in SAME ORDER as input

        3. **Projects** (For each project):
        - Enhance highlights to match technical requirements
        - Include relevant technologies from JD
        - CRITICAL: Each highlight MUST be between 16-30 words
        - Incorporate 70-80% of missing tech skills from JD that are related to existing project technologies
        - If project uses a technology mentioned in JD, include related keywords/tools from JD naturally
        - Return in SAME ORDER as input

        4. **Skills**:
        - Reorder EXISTING skills by relevance to job description (most relevant first)
        - ADD skills that are:
          a) Mentioned in the job description AND
          b) Related to existing skills or technologies in the resume (e.g., if resume has React, can add Redux, React Hooks, Context API)
        - INCLUDE 70-80% of missing technical skills from JD that align with candidate's tech stack
        - Add soft skills mentioned in JD to appropriate category
        - Keep categorized format

        CRITICAL RULES:
        - Be concise and impactful
        - Only enhance existing content, don't fabricate
        - ALL bullet points and highlights MUST be 16-30 words (strict requirement)
        - Incorporate 70-80% of missing technical keywords from JD that relate to existing skills
        - Include soft skills and team-related terms from JD (team player, cross-functional, collaboration, etc.)
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
