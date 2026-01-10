#!/usr/bin/env python
"""
Test script to validate PDF payload structure
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.resume import Resume, PersonalInfo, Experience, Education, Project
from services.pdf_client import PDFClientService
import json

# Create a minimal test resume matching the sample structure
resume = Resume(
    id='test-1',
    name='Test Resume',
    personalInfo=PersonalInfo(
        name='John Doe',
        email='john@example.com',
        phone='+1-555-0000',
        location='San Francisco, CA',
        linkedin='https://linkedin.com/in/johndoe',
        github='https://github.com/johndoe',
        website='https://johndoe.com',
        summary='Test software engineer'
    ),
    education=[
        Education(
            institution='Stanford University',
            degree='Bachelor of Science',
            field='Computer Science',
            startDate='2015-09',
            endDate='2019-06',
            gpa='3.8',
            achievements=['Dean\'s List', 'CS Award']
        )
    ],
    experience=[
        Experience(
            company='Tech Corp',
            position='Software Engineer',
            location='San Francisco',
            startDate='2019-07',
            endDate='Present',
            description=['Built features', 'Deployed systems']
        )
    ],
    skills=['Python', 'JavaScript', 'TypeScript', 'React', 'Node.js', 'Docker'],
    projects=[
        Project(
            name='Test Project',
            description='A cool project',
            technologies=['Python'],
            link='https://github.com/test',
            highlights=['Feature A', 'Feature B'],
            startDate='2024-01',
            endDate='2024-12'
        )
    ],
    certifications=[]
)

client = PDFClientService()
payload = client._to_open_resume_payload(resume)

# Print formatted JSON
print("=" * 80)
print("GENERATED PAYLOAD:")
print("=" * 80)
print(json.dumps(payload, indent=2))
print("=" * 80)

# Validate structure
print("\nVALIDATION:")
print(f"✓ Has 'resume' key: {'resume' in payload}")
print(f"✓ Has 'settings' key: {'settings' in payload}")

if 'resume' in payload:
    resume_data = payload['resume']
    print(f"✓ Has 'profile' key: {'profile' in resume_data}")
    print(f"✓ Has 'workExperiences' key: {'workExperiences' in resume_data}")
    print(f"✓ Has 'educations' key: {'educations' in resume_data}")
    print(f"✓ Has 'skills' key: {'skills' in resume_data}")
    print(f"✓ Has 'projects' key: {'projects' in resume_data}")
    print(f"✓ Has 'custom' key: {'custom' in resume_data}")

    if 'skills' in resume_data:
        skills = resume_data['skills']
        print(f"✓ Skills has 'featuredSkills': {'featuredSkills' in skills}")
        print(f"✓ Skills has 'descriptions': {'descriptions' in skills}")
        print(f"  - Featured skills count: {len(skills.get('featuredSkills', []))}")
        print(f"  - Skill descriptions count: {len(skills.get('descriptions', []))}")

print("\n" + "=" * 80)
