#!/usr/bin/env python3
"""
Test script to verify the enhanced interview report endpoint
"""

import requests
import json
import sys
import os

# Test configuration
BASE_URL = "http://localhost:5000"

def test_report_endpoint():
    """Test the enhanced report endpoint with a completed interview"""
    print("🧪 Testing Enhanced Interview Report Endpoint")
    print("=" * 50)
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "password": "Test123!",
        "full_name": "Test User"
    }
    
    try:
        # Step 1: Register or login user
        print("1. Logging in user...")
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        if login_response.status_code == 401:
            print("   User not found, registering...")
            reg_response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
            if reg_response.status_code != 201:
                print(f"   ❌ Registration failed: {reg_response.text}")
                return False
            
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": test_user["email"],
                "password": test_user["password"]
            })
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.text}")
            return False
        
        token = login_response.json().get('token')
        headers = {'Authorization': f'Bearer {token}'}
        print("   ✅ User logged in successfully")
        
        # Step 2: Check for existing completed interviews
        print("2. Checking for completed interviews...")
        history_response = requests.get(f"{BASE_URL}/api/interview/history", headers=headers)
        
        if history_response.status_code != 200:
            print(f"   ❌ Failed to get interview history: {history_response.text}")
            return False
        
        interviews = history_response.json().get('interviews', [])
        completed_interviews = [i for i in interviews if i.get('completed')]
        
        if not completed_interviews:
            print("   No completed interviews found. Creating a test interview...")
            interview_id = create_test_interview(headers)
            if not interview_id:
                return False
        else:
            interview_id = completed_interviews[0]['id']
            print(f"   ✅ Found completed interview ID: {interview_id}")
        
        # Step 3: Test the enhanced report endpoint
        print(f"3. Testing enhanced report endpoint for interview {interview_id}...")
        report_response = requests.get(f"{BASE_URL}/api/interview/report/{interview_id}", headers=headers)
        
        if report_response.status_code != 200:
            print(f"   ❌ Report request failed: {report_response.text}")
            return False
        
        report_data = report_response.json()
        
        # Step 4: Validate report structure
        print("4. Validating report data structure...")
        expected_keys = [
            'interview_info', 'performance_summary', 'detailed_analysis',
            'question_by_question', 'transcript', 'statistics'
        ]
        
        for key in expected_keys:
            if key not in report_data:
                print(f"   ❌ Missing key in report: {key}")
                return False
        
        print("   ✅ All expected keys present in report")
        
        # Step 5: Validate nested structures
        interview_info = report_data['interview_info']
        performance_summary = report_data['performance_summary']
        detailed_analysis = report_data['detailed_analysis']
        question_by_question = report_data['question_by_question']
        statistics = report_data['statistics']
        
        # Validate interview_info
        if not all(k in interview_info for k in ['interview_id', 'start_time', 'end_time', 'total_questions']):
            print("   ❌ Missing keys in interview_info")
            return False
        
        # Validate performance_summary
        if not all(k in performance_summary for k in ['overall_score', 'technical_skills', 'communication', 'problem_solving']):
            print("   ❌ Missing keys in performance_summary")
            return False
        
        # Validate detailed_analysis
        if not all(k in detailed_analysis for k in ['summary', 'strengths', 'areas_for_improvement', 'recommendations']):
            print("   ❌ Missing keys in detailed_analysis")
            return False
        
        # Validate question_by_question structure
        if question_by_question and isinstance(question_by_question, list):
            first_answer = question_by_question[0]
            expected_answer_keys = ['question', 'answer', 'score', 'feedback', 'strengths', 'improvements']
            if not all(k in first_answer for k in expected_answer_keys):
                print("   ❌ Missing keys in question_by_question items")
                return False
        
        print("   ✅ All nested structures validated")
        
        # Step 6: Display sample results
        print("\n📊 Sample Report Data:")
        print(f"   Interview ID: {interview_info['interview_id']}")
        print(f"   Candidate: {interview_info.get('candidate_name', 'N/A')}")
        print(f"   Duration: {interview_info.get('duration_minutes', 'N/A')} minutes")
        print(f"   Total Questions: {interview_info['total_questions']}")
        print(f"   Overall Score: {performance_summary['overall_score']}/100")
        print(f"   Performance Level: {performance_summary.get('performance_level', 'N/A')}")
        print(f"   Technical Skills: {performance_summary['technical_skills']}/100")
        print(f"   Communication: {performance_summary['communication']}/100")
        print(f"   Problem Solving: {performance_summary['problem_solving']}/100")
        
        if detailed_analysis['strengths']:
            print(f"   Top Strengths: {', '.join(detailed_analysis['strengths'][:2])}")
        
        print(f"   Questions scored 70+: {statistics.get('questions_above_70', 0)}")
        print(f"   Questions scored <50: {statistics.get('questions_below_50', 0)}")
        
        print("\n✅ Enhanced Report Endpoint Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def create_test_interview(headers):
    """Create a minimal test interview with answers for testing"""
    try:
        print("   Creating test interview...")
        
        # Create interview
        start_response = requests.post(f"{BASE_URL}/api/interview/start", headers=headers)
        if start_response.status_code != 201:
            print(f"   ❌ Failed to start interview: {start_response.text}")
            return None
        
        interview_id = start_response.json()['interview_id']
        
        # Submit a few test answers
        test_answers = [
            {
                "question": "Tell me about yourself",
                "answer": "I am a software developer with 3 years of experience in Python and web development. I enjoy solving complex problems and building scalable applications."
            },
            {
                "question": "What are your strengths?",
                "answer": "My main strengths are problem-solving, attention to detail, and the ability to work well in team environments. I also have strong communication skills."
            }
        ]
        
        for qa in test_answers:
            answer_response = requests.post(
                f"{BASE_URL}/api/interview/{interview_id}/answer",
                headers=headers,
                json={"answer": qa["answer"], "question": qa["question"]}
            )
            if answer_response.status_code != 200:
                print(f"   ❌ Failed to submit answer: {answer_response.text}")
                return None
        
        # Complete interview
        complete_response = requests.post(f"{BASE_URL}/api/interview/complete/{interview_id}", headers=headers)
        if complete_response.status_code != 200:
            print(f"   ❌ Failed to complete interview: {complete_response.text}")
            return None
        
        print(f"   ✅ Test interview {interview_id} created and completed")
        return interview_id
        
    except Exception as e:
        print(f"   ❌ Error creating test interview: {e}")
        return None

if __name__ == "__main__":
    success = test_report_endpoint()
    sys.exit(0 if success else 1)
