#!/usr/bin/env python3
"""
Test script for AI Interview CRM Platform
Tests all major functionality including authentication, interview flow, and analytics.
"""

import requests
import json
import os
import time
from io import BytesIO

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}

class TestAIInterviewCRM:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.interview_id = None
        
    def test_home_page(self):
        """Test if home page loads correctly"""
        print("🏠 Testing home page...")
        try:
            response = self.session.get(BASE_URL)
            assert response.status_code == 200
            assert "AI Interview CRM" in response.text
            print("✅ Home page loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Home page test failed: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        print("👤 Testing user registration...")
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/register",
                json=TEST_USER,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                print("✅ User registration successful")
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                print("ℹ️ User already exists, continuing with login...")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration test failed: {e}")
            return False
    
    def test_user_login(self):
        """Test user login"""
        print("🔑 Testing user login...")
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get('user_id')
                print(f"✅ Login successful - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login test failed: {e}")
            return False
    
    def test_dashboard_access(self):
        """Test dashboard access"""
        print("📊 Testing dashboard access...")
        try:
            response = self.session.get(f"{BASE_URL}/dashboard")
            
            if response.status_code == 200:
                print("✅ Dashboard accessible")
                return True
            else:
                print(f"❌ Dashboard access failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Dashboard test failed: {e}")
            return False
    
    def test_interview_creation(self):
        """Test interview creation with resume upload"""
        print("📝 Testing interview creation...")
        try:
            # Create a simple test PDF content
            test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test Resume Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000193 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n285\n%%EOF"
            
            files = {
                'resume': ('test_resume.pdf', BytesIO(test_pdf_content), 'application/pdf')
            }
            data = {
                'job_role': 'Software Engineer',
                'experience_level': 'Mid-level',
                'skills': 'Python, JavaScript, React'
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/interview/start",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.interview_id = result.get('interview_id')
                print(f"✅ Interview created successfully - Interview ID: {self.interview_id}")
                print(f"📋 Generated {len(result.get('questions', []))} questions")
                return True
            else:
                print(f"❌ Interview creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Interview creation test failed: {e}")
            return False
    
    def test_answer_submission(self):
        """Test answer submission"""
        print("💬 Testing answer submission...")
        try:
            if not self.interview_id:
                print("❌ No interview ID available")
                return False
            
            # Submit a test answer
            answer_data = {
                'question_index': 0,
                'answer': 'This is a test answer demonstrating my experience with Python programming and software development.',
                'time_taken': 45
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/interview/{self.interview_id}/answer",
                json=answer_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Answer submitted successfully")
                print(f"📊 Score: {result.get('score', 'N/A')}")
                return True
            else:
                print(f"❌ Answer submission failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Answer submission test failed: {e}")
            return False
    
    def test_interview_completion(self):
        """Test interview completion"""
        print("🏁 Testing interview completion...")
        try:
            if not self.interview_id:
                print("❌ No interview ID available")
                return False
            
            response = self.session.post(
                f"{BASE_URL}/api/interview/{self.interview_id}/complete",
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Interview completed successfully")
                print(f"📊 Overall Score: {result.get('overall_score', 'N/A')}")
                return True
            else:
                print(f"❌ Interview completion failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Interview completion test failed: {e}")
            return False
    
    def test_analytics(self):
        """Test analytics functionality"""
        print("📈 Testing analytics...")
        try:
            response = self.session.get(f"{BASE_URL}/api/dashboard/stats")
            
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Analytics retrieved successfully")
                print(f"📊 Total Interviews: {stats.get('total_interviews', 0)}")
                print(f"📊 Average Score: {stats.get('average_score', 0)}")
                return True
            else:
                print(f"❌ Analytics test failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Analytics test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting AI Interview CRM Platform Tests")
        print("=" * 50)
        
        tests = [
            self.test_home_page,
            self.test_user_registration,
            self.test_user_login,
            self.test_dashboard_access,
            self.test_interview_creation,
            self.test_answer_submission,
            self.test_interview_completion,
            self.test_analytics
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                print("-" * 30)
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                print("-" * 30)
        
        print("\n🎯 Test Results Summary")
        print("=" * 50)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed! The AI Interview CRM Platform is fully functional.")
        else:
            print(f"⚠️ {total - passed} test(s) failed. Please check the issues above.")
        
        return passed == total

if __name__ == "__main__":
    # Wait for the server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    tester = TestAIInterviewCRM()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 CONGRATULATIONS! The AI Interview CRM Platform is fully functional and ready for use!")
    else:
        print("\n⚠️ Some tests failed. Please review the output above for details.")
