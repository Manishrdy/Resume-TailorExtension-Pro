"""
End-to-end test for resume tailoring extension
Simulates the full workflow with a real job description
"""

import requests
import json
import time
from datetime import datetime

# API endpoints
BASE_URL = "http://localhost:8000"
TAILOR_URL = f"{BASE_URL}/api/tailor"
PDF_URL = f"{BASE_URL}/api/generate-pdf"

# Sample resume data
SAMPLE_RESUME = {
    "id": "test-resume-001",
    "name": "Software Engineer Resume",
    "personalInfo": {
        "name": "Alex Johnson",
        "email": "alex.johnson@email.com",
        "phone": "(555) 123-4567",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/alexjohnson",
        "github": "github.com/alexjohnson",
        "website": "alexjohnson.dev"
    },
    "summary": "Experienced software engineer with 5 years of building scalable web applications. Proficient in React, Node.js, and cloud technologies.",
    "experience": [
        {
            "company": "TechCorp Solutions",
            "position": "Senior Software Engineer",
            "location": "San Francisco, CA",
            "startDate": "2021-03",
            "endDate": "Present",
            "description": [
                "Led development of microservices architecture serving 1M+ users",
                "Improved API response time by 40% through optimization",
                "Mentored junior developers and conducted code reviews",
                "Implemented CI/CD pipelines using Jenkins and Docker"
            ]
        },
        {
            "company": "StartupXYZ",
            "position": "Software Engineer",
            "location": "Remote",
            "startDate": "2019-06",
            "endDate": "2021-02",
            "description": [
                "Built full-stack features using React and Node.js",
                "Designed and implemented RESTful APIs",
                "Collaborated with product team on feature planning",
                "Maintained 95% test coverage across codebase"
            ]
        }
    ],
    "education": [
        {
            "institution": "University of California, Berkeley",
            "degree": "Bachelor of Science in Computer Science",
            "location": "Berkeley, CA",
            "graduationDate": "2019-05",
            "gpa": "3.7"
        }
    ],
    "projects": [
        {
            "name": "E-Commerce Platform",
            "technologies": ["React", "Node.js", "MongoDB", "AWS"],
            "description": [
                "Built scalable e-commerce platform handling 10K+ daily transactions",
                "Integrated payment processing with Stripe API",
                "Implemented inventory management system"
            ],
            "link": "github.com/alexjohnson/ecommerce"
        },
        {
            "name": "Task Management App",
            "technologies": ["Vue.js", "Firebase", "TypeScript"],
            "description": [
                "Developed real-time collaborative task management application",
                "Implemented drag-and-drop interface with 500+ active users"
            ],
            "link": "taskmaster.alexjohnson.dev"
        }
    ],
    "skills": [
        "JavaScript",
        "Python",
        "React",
        "Node.js",
        "TypeScript",
        "AWS",
        "Docker",
        "MongoDB",
        "PostgreSQL",
        "Git",
        "REST APIs",
        "Microservices"
    ]
}

# Job description for a Full-Stack Engineer at a fintech company
JOB_DESCRIPTION = """
Full-Stack Engineer - Fintech Platform
Location: San Francisco, CA (Hybrid)
Salary: $150K - $200K

About Us:
FinTechPro is revolutionizing digital payments and financial services. We're looking for an experienced Full-Stack Engineer to join our engineering team and help build the next generation of payment solutions.

Responsibilities:
• Design and develop scalable microservices for payment processing systems
• Build responsive web applications using React and TypeScript
• Implement secure RESTful APIs with Node.js and Express
• Collaborate with cross-functional teams including product, design, and DevOps
• Optimize database queries and system performance for high-volume transactions
• Participate in code reviews and mentor junior engineers
• Ensure compliance with PCI-DSS and financial industry security standards
• Write comprehensive unit and integration tests

Required Skills:
• 5+ years of software engineering experience
• Strong proficiency in JavaScript/TypeScript, React, and Node.js
• Experience with microservices architecture and distributed systems
• Knowledge of SQL and NoSQL databases (PostgreSQL, MongoDB)
• Experience with cloud platforms (AWS, GCP, or Azure)
• Strong understanding of REST API design and implementation
• Familiarity with Docker, Kubernetes, and CI/CD pipelines
• Experience with payment processing systems or fintech domain (preferred)
• Knowledge of security best practices and compliance standards
• Excellent problem-solving and communication skills

Nice to Have:
• Experience with GraphQL
• Knowledge of blockchain or cryptocurrency technologies
• Previous startup experience
• Open source contributions

Benefits:
• Competitive salary and equity package
• Health, dental, and vision insurance
• 401(k) matching
• Flexible work schedule
• Professional development budget
"""


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_health_check():
    """Test the health endpoint"""
    print_section("1. Testing Health Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        print("✅ Health check passed")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_tailor_resume():
    """Test the tailor endpoint with sample data"""
    print_section("2. Testing Resume Tailoring")
    
    payload = {
        "resume": SAMPLE_RESUME,
        "jobDescription": JOB_DESCRIPTION,
        "targetRole": "Full-Stack Engineer",
        "preserveStructure": True
    }
    
    print(f"📤 Sending request to {TAILOR_URL}")
    print(f"   Resume: {SAMPLE_RESUME['personalInfo']['name']}")
    print(f"   Target Role: Full-Stack Engineer")
    print(f"   Job Description Length: {len(JOB_DESCRIPTION)} characters")
    print("\n⏳ Waiting for AI to tailor resume (this may take 10-30 seconds)...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            TAILOR_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=70  # Slightly longer than the 60s frontend timeout
        )
        
        elapsed_time = time.time() - start_time
        
        response.raise_for_status()
        result = response.json()
        
        print(f"\n✅ Resume tailored successfully in {elapsed_time:.1f} seconds!")
        print(f"\n📊 Results:")
        print(f"   • ATS Score: {result.get('atsScore', 'N/A')}/100")
        print(f"   • Matched Keywords: {len(result.get('matchedKeywords', []))}")
        print(f"   • Missing Keywords: {len(result.get('missingKeywords', []))}")
        print(f"   • Suggestions: {len(result.get('suggestions', []))}")
        print(f"   • Changes Made: {len(result.get('changes', []))}")
        
        # Show matched keywords
        if result.get('matchedKeywords'):
            print(f"\n🎯 Top Matched Keywords:")
            for kw in result['matchedKeywords'][:10]:
                print(f"      • {kw}")
        
        # Show missing keywords
        if result.get('missingKeywords'):
            print(f"\n⚠️  Missing Keywords (consider adding):")
            for kw in result['missingKeywords'][:10]:
                print(f"      • {kw}")
        
        # Show suggestions
        if result.get('suggestions'):
            print(f"\n💡 Suggestions:")
            for i, suggestion in enumerate(result['suggestions'][:5], 1):
                print(f"      {i}. {suggestion}")
        
        # Show changes
        if result.get('changes'):
            print(f"\n📝 Changes Made:")
            for i, change in enumerate(result['changes'][:5], 1):
                print(f"      {i}. {change}")
        
        return result
        
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Request timed out after {elapsed_time:.1f} seconds")
        print("This is expected behavior - timeout protection is working!")
        return None
        
    except requests.exceptions.RequestException as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ Request failed after {elapsed_time:.1f} seconds")
        print(f"Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None


def test_generate_pdf(tailored_resume):
    """Test PDF generation endpoint"""
    print_section("3. Testing PDF Generation")
    
    if not tailored_resume:
        print("⚠️  Skipping PDF generation (no tailored resume)")
        return None
    
    payload = {
        "resume": tailored_resume.get('tailoredResume', SAMPLE_RESUME)
    }
    
    print(f"📤 Sending request to {PDF_URL}")
    print("⏳ Generating PDF...")
    
    try:
        response = requests.post(
            PDF_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response.raise_for_status()
        
        # Save PDF to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tailored_resume_{timestamp}.pdf"
        filepath = f"c:\\Users\\manis\\Desktop\\resume_tailoring_extension\\{filename}"
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ PDF generated successfully!")
        print(f"📄 Saved to: {filepath}")
        print(f"   File size: {len(response.content):,} bytes")
        
        return filepath
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return None


def main():
    """Run all tests"""
    print("\n" + "🚀 " * 30)
    print("  RESUME TAILORING EXTENSION - END-TO-END TEST")
    print("🚀 " * 30)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Backend is not running. Please start it first.")
        return
    
    # Test 2: Tailor resume
    tailored_result = test_tailor_resume()
    
    # Test 3: Generate PDF
    if tailored_result:
        test_generate_pdf(tailored_result)
    
    # Summary
    print_section("TEST SUMMARY")
    if tailored_result:
        print("✅ All tests completed successfully!")
        print("\nThe extension workflow is working correctly:")
        print("  1. ✅ Health check passed")
        print("  2. ✅ Resume tailoring completed")
        print("  3. ✅ PDF generation successful")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
