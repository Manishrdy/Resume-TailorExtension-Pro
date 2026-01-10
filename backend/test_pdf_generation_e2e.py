#!/usr/bin/env python
"""
End-to-end test for PDF generation
Tests the complete flow: Backend → Open Resume Service → PDF
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import httpx
from models.resume import Resume, PersonalInfo, Experience, Education, Project
from services.pdf_client import PDFClientService

async def test_pdf_generation():
    """Test PDF generation end-to-end"""

    # Create a test resume
    resume = Resume(
        id='test-e2e-1',
        name='E2E Test Resume',
        personalInfo=PersonalInfo(
            name='Jane Smith',
            email='jane.smith@example.com',
            phone='+1-555-1234',
            location='New York, NY',
            linkedin='https://linkedin.com/in/janesmith',
            github='https://github.com/janesmith',
            website='https://janesmith.dev',
            summary='Senior Full Stack Engineer with 8 years of experience building scalable web applications'
        ),
        education=[
            Education(
                institution='MIT',
                degree='Master of Science',
                field='Computer Science',
                startDate='2013-09',
                endDate='2015-06',
                gpa='3.9',
                achievements=[
                    'Research in Distributed Systems',
                    'Teaching Assistant for Advanced Algorithms',
                    'Dean\'s List all semesters'
                ]
            ),
            Education(
                institution='UC Berkeley',
                degree='Bachelor of Science',
                field='Computer Science',
                startDate='2009-09',
                endDate='2013-06',
                gpa='3.8',
                achievements=['Graduated with High Honors']
            )
        ],
        experience=[
            Experience(
                company='Tech Giant Inc',
                position='Senior Software Engineer',
                location='San Francisco, CA',
                startDate='2019-01',
                endDate='Present',
                description=[
                    'Led development of microservices architecture serving 10M+ users',
                    'Reduced API latency by 60% through database optimization and caching',
                    'Mentored team of 5 junior engineers',
                    'Implemented CI/CD pipeline reducing deployment time by 80%'
                ]
            ),
            Experience(
                company='Startup Ventures',
                position='Full Stack Engineer',
                location='New York, NY',
                startDate='2015-07',
                endDate='2018-12',
                description=[
                    'Built RESTful APIs using Python FastAPI and Node.js Express',
                    'Developed responsive web applications with React and TypeScript',
                    'Designed and implemented PostgreSQL database schemas',
                    'Deployed applications on AWS using Docker and Kubernetes'
                ]
            )
        ],
        skills=[
            'Python', 'JavaScript', 'TypeScript', 'React', 'Node.js', 'FastAPI',
            'PostgreSQL', 'MongoDB', 'Redis', 'AWS', 'Docker', 'Kubernetes',
            'LangChain', 'OpenAI GPT', 'REST APIs', 'GraphQL', 'Git', 'CI/CD'
        ],
        projects=[
            Project(
                name='AI Resume Analyzer',
                description='ML-powered resume analysis tool',
                technologies=['Python', 'LangChain', 'FastAPI', 'React'],
                link='https://github.com/janesmith/ai-resume',
                highlights=[
                    'Built LLM-based resume parsing and analysis engine',
                    'Integrated with OpenAI GPT for intelligent recommendations',
                    'Processed 10,000+ resumes with 95% accuracy'
                ],
                startDate='2024-01',
                endDate='2024-12'
            ),
            Project(
                name='Real-time Chat Platform',
                description='Scalable WebSocket-based chat application',
                technologies=['Node.js', 'Socket.io', 'Redis', 'MongoDB'],
                link='https://github.com/janesmith/chat-platform',
                highlights=[
                    'Supported 5,000+ concurrent users',
                    'Implemented message persistence and search',
                    'Built moderation and spam detection features'
                ],
                startDate='2023-03',
                endDate='2023-09'
            )
        ],
        certifications=[]
    )

    # Initialize PDF client
    client = PDFClientService()

    print("=" * 80)
    print("END-TO-END PDF GENERATION TEST")
    print("=" * 80)
    print(f"\nTest Resume: {resume.personalInfo.name}")
    print(f"Resume ID: {resume.id}")

    # Check if Open Resume service is available
    print("\n[1/3] Checking Open Resume service health...")
    is_healthy = await client.check_service_health()

    if not is_healthy:
        print("❌ Open Resume service is not available")
        print(f"   Make sure the service is running at: {client.base_url}")
        return False

    print(f"✅ Open Resume service is healthy at {client.base_url}")

    # Generate the payload
    print("\n[2/3] Generating payload...")
    payload = client._to_open_resume_payload(resume)

    print(f"✅ Payload generated successfully")
    print(f"   Profile fields: {len(payload['resume']['profile'])}")
    print(f"   Work experiences: {len(payload['resume']['workExperiences'])}")
    print(f"   Educations: {len(payload['resume']['educations'])}")
    print(f"   Projects: {len(payload['resume']['projects'])}")
    print(f"   Featured skills: {len(payload['resume']['skills']['featuredSkills'])}")
    print(f"   Skill categories: {len(payload['resume']['skills']['descriptions'])}")

    # Generate PDF
    print("\n[3/3] Generating PDF...")
    pdf_bytes = await client.generate_pdf(resume)

    if pdf_bytes is None:
        print("❌ PDF generation failed")
        return False

    pdf_size_kb = len(pdf_bytes) / 1024
    print(f"✅ PDF generated successfully")
    print(f"   Size: {pdf_size_kb:.2f} KB")

    # Save PDF to file
    output_path = os.path.join(os.path.dirname(__file__), 'test_output.pdf')
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)

    print(f"\n📄 PDF saved to: {output_path}")
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - PDF GENERATION WORKING!")
    print("=" * 80)

    return True

async def main():
    """Main test runner"""
    try:
        success = await test_pdf_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
