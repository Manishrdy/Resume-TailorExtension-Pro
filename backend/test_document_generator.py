"""
Test script for document generator service.
Tests PDF and DOCX generation with sample resume data.
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.resume import (
    Resume,
    PersonalInfo,
    Experience,
    Education,
    Project,
    Certification,
)
from services.document_generator import get_document_generator


def create_sample_resume() -> Resume:
    """Create a sample resume for testing"""
    return Resume(
        id="test-resume-001",
        name="Software Engineer Resume - Gemini Tailored",
        personalInfo=PersonalInfo(
            name="John Doe",
            email="john.doe@email.com",
            phone="+1-555-123-4567",
            location="San Francisco, CA",
            linkedin="linkedin.com/in/johndoe",
            github="github.com/johndoe",
            website="johndoe.dev",
            summary=(
                "Senior Software Engineer with 8+ years of experience building scalable "
                "distributed systems and cloud-native applications. Expert in Python, "
                "microservices architecture, and AI/ML integration. Proven track record "
                "of leading cross-functional teams and delivering high-impact solutions "
                "that improve system performance by 300% and reduce operational costs by 40%."
            ),
        ),
        experience=[
            Experience(
                company="TechCorp Inc.",
                position="Senior Software Engineer",
                location="San Francisco, CA",
                startDate="2020-01",
                endDate="Present",
                description=[
                    "Architected and deployed microservices-based platform serving 10M+ daily users with 99.99% uptime using Python, FastAPI, and Kubernetes",
                    "Led migration from monolithic architecture to event-driven microservices, reducing deployment time by 75% and improving system scalability by 300%",
                    "Implemented AI-powered recommendation engine using LangChain and RAG, increasing user engagement by 45% and revenue by $2M annually",
                    "Mentored team of 6 engineers on best practices for cloud-native development, code reviews, and system design patterns",
                    "Optimized database queries and caching strategies, reducing API response time from 800ms to 120ms (85% improvement)",
                ],
            ),
            Experience(
                company="StartupXYZ",
                position="Software Engineer",
                location="Remote",
                startDate="2018-06",
                endDate="2019-12",
                description=[
                    "Developed RESTful APIs and backend services using Python, Django, and PostgreSQL for SaaS platform with 50K+ users",
                    "Built real-time data processing pipeline using Apache Kafka and Redis, handling 100K+ events per second",
                    "Implemented automated CI/CD pipeline with GitHub Actions, reducing deployment errors by 60% and deployment time by 50%",
                    "Collaborated with product team to design and launch 3 major features, resulting in 25% increase in user retention",
                ],
            ),
            Experience(
                company="FinTech Solutions",
                position="Junior Software Engineer",
                location="New York, NY",
                startDate="2016-07",
                endDate="2018-05",
                description=[
                    "Developed payment processing system handling $10M+ in daily transactions with PCI-DSS compliance",
                    "Created automated testing suite with pytest achieving 90%+ code coverage and reducing production bugs by 40%",
                    "Integrated third-party APIs (Stripe, PayPal, Plaid) for payment processing and bank account verification",
                ],
            ),
        ],
        education=[
            Education(
                institution="University of California, Berkeley",
                degree="Bachelor of Science",
                field="Computer Science",
                startDate="2012-09",
                endDate="2016-05",
                gpa="3.8/4.0",
                achievements=[
                    "Dean's List all semesters",
                    "Graduated with Honors in Computer Science",
                    "Relevant Coursework: Algorithms, Distributed Systems, Machine Learning, Database Systems",
                ],
            ),
        ],
        skills=[
            "Python",
            "FastAPI",
            "Django",
            "PostgreSQL",
            "MongoDB",
            "Redis",
            "Docker",
            "Kubernetes",
            "AWS",
            "GCP",
            "Microservices",
            "RESTful APIs",
            "GraphQL",
            "Apache Kafka",
            "RabbitMQ",
            "CI/CD",
            "GitHub Actions",
            "Jenkins",
            "Git",
            "LangChain",
            "RAG",
            "LLMs",
            "Machine Learning",
            "System Design",
            "Agile/Scrum",
        ],
        projects=[
            Project(
                name="AI Resume Tailoring Chrome Extension",
                description=(
                    "Built Chrome extension with AI-powered resume tailoring using Gemini API. "
                    "Features include job description parsing, keyword optimization, and ATS-friendly "
                    "PDF/DOCX generation. Reduced resume customization time by 90% for 1000+ users."
                ),
                technologies=["Python", "FastAPI", "Gemini AI", "Chrome Extension", "TypeScript"],
                link="github.com/johndoe/resume-extension",
                highlights=[
                    "Integrated Google Gemini 2.5 Flash for intelligent resume optimization",
                    "Achieved 95% ATS compatibility score using keyword matching algorithms",
                    "Generated 10,000+ tailored resumes with 99.9% success rate",
                ],
            ),
            Project(
                name="Real-Time Analytics Dashboard",
                description=(
                    "Developed real-time analytics platform processing 1M+ events per day using "
                    "event-driven architecture. Built with Python, Apache Kafka, and React."
                ),
                technologies=["Python", "Apache Kafka", "Redis", "React", "WebSockets"],
                highlights=[
                    "Processed streaming data with sub-100ms latency using Kafka consumers",
                    "Built interactive dashboards with live updates via WebSocket connections",
                    "Reduced infrastructure costs by 35% through optimized data pipeline",
                ],
            ),
        ],
        certifications=[
            Certification(
                name="AWS Certified Solutions Architect - Professional",
                issuer="Amazon Web Services",
                date="2023-06",
                credentialId="AWS-PSA-12345",
            ),
            Certification(
                name="Google Cloud Professional Cloud Architect",
                issuer="Google Cloud",
                date="2022-11",
            ),
        ],
    )


def test_pdf_generation():
    """Test PDF generation"""
    print("\n" + "=" * 80)
    print("Testing PDF Generation")
    print("=" * 80)

    try:
        # Create sample resume
        resume = create_sample_resume()
        print(f"✓ Created sample resume for: {resume.personalInfo.name}")

        # Get document generator
        generator = get_document_generator()
        print("✓ Initialized document generator")

        # Generate PDF
        print("\nGenerating PDF...")
        pdf_bytes = generator.generate_pdf(resume)

        # Verify PDF
        if pdf_bytes and len(pdf_bytes) > 0:
            print(f"✓ PDF generated successfully ({len(pdf_bytes):,} bytes)")

            # Save to file
            output_path = Path(__file__).parent / "test_output" / "test_resume.pdf"
            output_path.parent.mkdir(exist_ok=True)
            output_path.write_bytes(pdf_bytes)
            print(f"✓ PDF saved to: {output_path}")

            return True
        else:
            print("✗ PDF generation failed - empty result")
            return False

    except Exception as e:
        print(f"✗ PDF generation failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_docx_generation():
    """Test DOCX generation"""
    print("\n" + "=" * 80)
    print("Testing DOCX Generation")
    print("=" * 80)

    try:
        # Create sample resume
        resume = create_sample_resume()
        print(f"✓ Created sample resume for: {resume.personalInfo.name}")

        # Get document generator
        generator = get_document_generator()
        print("✓ Initialized document generator")

        # Generate DOCX
        print("\nGenerating DOCX...")
        docx_bytes = generator.generate_docx(resume)

        # Verify DOCX
        if docx_bytes and len(docx_bytes) > 0:
            print(f"✓ DOCX generated successfully ({len(docx_bytes):,} bytes)")

            # Save to file
            output_path = Path(__file__).parent / "test_output" / "test_resume.docx"
            output_path.parent.mkdir(exist_ok=True)
            output_path.write_bytes(docx_bytes)
            print(f"✓ DOCX saved to: {output_path}")

            return True
        else:
            print("✗ DOCX generation failed - empty result")
            return False

    except Exception as e:
        print(f"✗ DOCX generation failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Document Generator Test Suite")
    print("=" * 80)

    # Run tests
    pdf_success = test_pdf_generation()
    docx_success = test_docx_generation()

    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"PDF Generation:  {'✓ PASSED' if pdf_success else '✗ FAILED'}")
    print(f"DOCX Generation: {'✓ PASSED' if docx_success else '✗ FAILED'}")
    print("=" * 80)

    # Exit with appropriate code
    sys.exit(0 if (pdf_success and docx_success) else 1)
