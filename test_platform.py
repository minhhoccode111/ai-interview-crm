#!/usr/bin/env python3
"""
Comprehensive test script for AI Interview CRM Platform
Tests all major functionality including API endpoints, database operations, and AI services
"""

import requests
import json
import time
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))


class InterviewCRMTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.resume_id = None
        self.interview_id = None

    def test_api_status(self):
        """Test if the API is running"""
        print("🔄 Testing API status...")
        try:
            response = requests.get(f"{self.base_url}/api/status")
            if response.status_code == 200:
                print("✅ API is running successfully")
                print(f"   Status: {response.json()}")
                return True
            else:
                print(f"❌ API status check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False

    def test_user_registration(self):
        """Test user registration"""
        print("\n🔄 Testing user registration...")
        try:
            user_data = {
                "email": f"test_{int(time.time())}@example.com",
                "password": "testpassword123",
                "full_name": "Test User",
            }

            response = requests.post(
                f"{self.base_url}/api/auth/register", json=user_data
            )
            if response.status_code == 201:
                data = response.json()
                self.user_id = data.get("user_id")
                print("✅ User registration successful")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"❌ User registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ User registration error: {e}")
            return False

    def test_user_login(self):
        """Test user login"""
        print("\n🔄 Testing user login...")
        try:
            login_data = {
                "email": f"test_{int(time.time() - 1)}@example.com",
                "password": "testpassword123",
            }

            # First register a user for login test
            requests.post(
                f"{self.base_url}/api/auth/register",
                json={**login_data, "full_name": "Login Test User"},
            )

            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.user_id = data.get("user_id")
                print("✅ User login successful")
                print(f"   Token received: {'Yes' if self.token else 'No'}")
                return True
            else:
                print(f"❌ User login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ User login error: {e}")
            return False

    def test_resume_upload_text(self):
        """Test resume upload with text content"""
        print("\n🔄 Testing resume upload (text)...")
        if not self.token:
            print("❌ No authentication token available")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resume_data = {
                "text": """
                John Doe
                Software Engineer
                Email: john.doe@example.com
                Phone: (555) 123-4567

                EXPERIENCE:
                - Senior Software Engineer at TechCorp (2020-2024)
                  • Developed full-stack web applications using React and Node.js
                  • Led a team of 5 developers
                  • Implemented CI/CD pipelines

                - Junior Developer at StartupInc (2018-2020)
                  • Built REST APIs using Python Flask
                  • Worked with PostgreSQL databases

                SKILLS:
                Python, JavaScript, React, Node.js, SQL, Git, AWS, Docker

                EDUCATION:
                Bachelor of Science in Computer Science - University of Tech (2018)

                PROJECTS:
                - E-commerce Platform: Built a full-stack e-commerce site
                - Task Management App: Created a React-based productivity tool

                CERTIFICATIONS:
                AWS Certified Developer Associate
                """
            }

            response = requests.post(
                f"{self.base_url}/api/interview/resume",
                json=resume_data,
                headers=headers,
            )
            if response.status_code == 200:
                data = response.json()
                self.resume_id = data.get("resume_id")
                print("✅ Resume upload successful")
                print(f"   Resume ID: {self.resume_id}")
                print(f"   Skills found: {data.get('skills_found', 0)}")
                print(f"   Experience count: {data.get('experience_count', 0)}")
                return True
            else:
                print(f"❌ Resume upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Resume upload error: {e}")
            return False

    def test_interview_start(self):
        """Test starting an interview"""
        print("\n🔄 Testing interview start...")
        if not self.token or not self.resume_id:
            print("❌ Missing token or resume_id")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            start_data = {"resume_id": self.resume_id}

            response = requests.post(
                f"{self.base_url}/api/interview/start", json=start_data, headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                self.interview_id = data.get("interview_id")
                questions = data.get("questions", [])
                print("✅ Interview started successfully")
                print(f"   Interview ID: {self.interview_id}")
                print(f"   Questions generated: {len(questions)}")
                if questions:
                    print(f"   First question: {questions[0][:100]}...")
                return True
            else:
                print(f"❌ Interview start failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Interview start error: {e}")
            return False

    def test_answer_processing(self):
        """Test processing an interview answer"""
        print("\n🔄 Testing answer processing...")
        if not self.token or not self.interview_id:
            print("❌ Missing token or interview_id")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.token}"}

            # Simulate answering a question
            form_data = {
                "interview_id": str(self.interview_id),
                "question": "Tell me about yourself and your background.",
                "text_answer": """I am a passionate software engineer with over 6 years of experience
                in full-stack development. I have worked extensively with Python, JavaScript, and modern
                web frameworks like React and Node.js. In my current role at TechCorp, I lead a team of
                5 developers and have successfully delivered multiple high-impact projects. I'm particularly
                interested in building scalable web applications and have experience with cloud technologies
                like AWS. I'm always eager to learn new technologies and take on challenging problems.""",
            }

            response = requests.post(
                f"{self.base_url}/api/interview/process",
                data=form_data,
                headers=headers,
            )
            if response.status_code == 200:
                data = response.json()
                evaluation = data.get("evaluation", {})
                print("✅ Answer processing successful")
                print(f"   Score: {evaluation.get('score', 0)}/100")
                print(f"   Next question: {data.get('next_question', 'N/A')[:100]}...")
                return True
            else:
                print(f"❌ Answer processing failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Answer processing error: {e}")
            return False

    def test_interview_completion(self):
        """Test completing an interview"""
        print("\n🔄 Testing interview completion...")
        if not self.token or not self.interview_id:
            print("❌ Missing token or interview_id")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.token}"}

            response = requests.post(
                f"{self.base_url}/api/interview/complete/{self.interview_id}",
                headers=headers,
            )
            if response.status_code == 200:
                data = response.json()
                print("✅ Interview completion successful")
                print(f"   Overall score: {data.get('overall_score', 0)}/100")
                print(f"   Report URL: {data.get('report_url', 'N/A')}")
                print(f"   Strengths: {len(data.get('strengths', []))}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                return True
            else:
                print(f"❌ Interview completion failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Interview completion error: {e}")
            return False

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        print("\n🔄 Testing dashboard statistics...")
        if not self.token:
            print("❌ No authentication token")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.token}"}

            response = requests.get(
                f"{self.base_url}/api/dashboard/stats", headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                print("✅ Dashboard stats retrieved successfully")
                print(f"   Total interviews: {data.get('total_interviews', 0)}")
                print(f"   Completed interviews: {data.get('completed_interviews', 0)}")
                print(
                    f"   Average overall score: {data.get('average_scores', {}).get('overall', 0)}"
                )
                return True
            else:
                print(f"❌ Dashboard stats failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Dashboard stats error: {e}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting AI Interview CRM Platform Tests")
        print("=" * 50)

        tests = [
            self.test_api_status,
            self.test_user_registration,
            self.test_user_login,
            self.test_resume_upload_text,
            self.test_interview_start,
            self.test_answer_processing,
            self.test_interview_completion,
            self.test_dashboard_stats,
        ]

        passed = 0
        failed = 0

        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                failed += 1

        print("\n" + "=" * 50)
        print("🏁 Test Results Summary")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")

        if failed == 0:
            print(
                "\n🎉 All tests passed! The AI Interview CRM Platform is fully functional."
            )
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")

        return failed == 0


if __name__ == "__main__":
    print("AI Interview CRM Platform - Comprehensive Test Suite")
    print("Make sure the Flask application is running on http://localhost:5000")

    # Wait a moment for user to ensure server is running
    input("Press Enter when the Flask server is running...")

    tester = InterviewCRMTester()
    success = tester.run_all_tests()

    if success:
        print("\n🎯 Platform is ready for use!")
        print("💡 You can now:")
        print("   • Open http://localhost:5000 in your browser")
        print("   • Register a new account")
        print("   • Upload your resume")
        print("   • Take practice interviews")
        print("   • View your progress in the dashboard")
    else:
        print("\n🔧 Some tests failed. Please check the logs and fix any issues.")
