from src.models.resume import Resume
import json
import traceback

def test_fixes():
    print("--- Testing Fixes (Resume Model Only) ---")
    
    # Test Data
    skills_dict = {
        "Backend": ["Python", "Node.js"],
        "Database": ["PostgreSQL", "MongoDB"]
    }
    
    education_data = {
        "institution": "Test Univ",
        "degree": "BS CS",
        "startDate": "2020",
        "endDate": "2024",
        "achievements": "Dean's List\nGPA 4.0\nPresident's Award"
    }

    resume_data = {
        "id": "test-1",
        "name": "Test Resume",
        "personalInfo": {
            "name": "John Doe",
            "email": "john@example.com",
            "summary": "Test summary"
        },
        "education": [education_data],
        "experience": [{
            "company": "Tech Corp",
            "position": "Dev",
            "startDate": "2024",
            "endDate": "Present",
            "description": ["Worked hard"]
        }],
        "skills": skills_dict
    }

    try:
        # 1. Test Model Parsing
        resume = Resume(**resume_data)
        
        # Check Skills
        if isinstance(resume.skills, dict):
            print("[OK] Skills preserved as Dict")
            print(f"     Value: {resume.skills}")
        else:
            print(f"[FAIL] Skills flattened to {type(resume.skills)}")
            
        # Check Education
        edu = resume.education[0]
        if isinstance(edu.achievements, list) and len(edu.achievements) == 3:
             print("[OK] Achievements correctly split into List")
             print(f"     Value: {edu.achievements}")
        else:
             print(f"[FAIL] Achievements: {edu.achievements}")

    except Exception as e:
        print(f"[ERROR] Test failed with exception: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_fixes()
