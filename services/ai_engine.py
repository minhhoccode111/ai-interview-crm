import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import Config
import json
import re
import numpy as np

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)


class InterviewEngine:
    def __init__(self, language="en"):
        """Initialize the interview engine with language support

        Args:
            language (str): Language code (e.g., 'en', 'vi')
        """
        self.language = language

        # Configure TF-IDF vectorizer based on language
        language_config = Config.SUPPORTED_LANGUAGES.get(
            language, Config.SUPPORTED_LANGUAGES["en"]
        )
        stopwords = language_config.get("tfidf_stopwords")

        if stopwords:
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words=stopwords)
        else:
            # For languages without built-in stopwords, use no stopwords
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)

        self.model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")

    def parse_resume(self, text_content):
        """Parse resume text into structured data using Gemini AI"""
        prompt = f"""
        Parse this resume text into structured JSON format. Return ONLY valid JSON with these exact fields:
        {{
            "name": "Full Name",
            "email": "email@example.com",
            "phone": "phone number",
            "skills": ["skill1", "skill2", "skill3"],
            "education": [
                {{
                    "degree": "degree name",
                    "institution": "school name",
                    "year": "graduation year"
                }}
            ],
            "experience": [
                {{
                    "title": "job title",
                    "company": "company name",
                    "duration": "duration",
                    "description": "job description"
                }}
            ],
            "projects": [
                {{
                    "name": "project name",
                    "description": "project description",
                    "technologies": ["tech1", "tech2"]
                }}
            ],
            "certifications": ["cert1", "cert2"]
        }}

        Resume Text:
        {text_content}
        """

        try:
            response = self.model.generate_content(prompt)
            # Clean the response to extract only JSON
            response_text = response.text.strip()
            # Remove any markdown formatting
            response_text = re.sub(r"```json\s*", "", response_text)
            response_text = re.sub(r"```\s*", "", response_text)

            parsed_data = json.loads(response_text)
            return parsed_data
        except Exception as e:
            print(f"Error parsing resume: {e}")
            # Return basic structure if parsing fails
            return {
                "name": "Unknown",
                "email": "",
                "phone": "",
                "skills": [],
                "education": [],
                "experience": [],
                "projects": [],
                "certifications": [],
            }

    def generate_questions(self, resume_data, language="en"):
        """Generate interview questions based on resume data in specified language"""
        skills = ", ".join(resume_data.get("skills", []))
        experience = resume_data.get("experience", [])
        projects = resume_data.get("projects", [])
        num_questions = Config.NUM_INTERVIEW_QUESTIONS

        # Get language-specific instructions
        language_info = Config.SUPPORTED_LANGUAGES.get(
            language, Config.SUPPORTED_LANGUAGES["en"]
        )
        language_name = language_info["name"]

        if language == "vi":
            prompt = f"""
            Dựa trên hồ sơ của ứng viên này, hãy tạo chính xác {num_questions} câu hỏi phỏng vấn bằng tiếng Việt.

            Hồ sơ ứng viên:
            - Kỹ năng: {skills}
            - Kinh nghiệm: {len(experience)} vị trí
            - Dự án: {len(projects)} dự án

            Tạo câu hỏi theo các danh mục sau:
            1. 3 câu hỏi kỹ thuật về kỹ năng của họ
            2. 2 câu hỏi hành vi về làm việc nhóm và giải quyết vấn đề
            3. 2 câu hỏi về kinh nghiệm và dự án của họ
            4. 2 câu hỏi tình huống
            5. 1 câu hỏi về mục tiêu nghề nghiệp

            Trả về mỗi câu hỏi trên một dòng mới, đánh số từ 1-{num_questions}.
            """
        else:
            prompt = f"""
            Based on this candidate's profile, generate exactly {num_questions} interview questions in {language_name}.

            Candidate Profile:
            - Skills: {skills}
            - Experience: {len(experience)} positions
            - Projects: {len(projects)} projects

            Generate questions in these categories:
            1. 3 Technical questions about their skills
            2. 2 Behavioral questions about teamwork and problem-solving
            3. 2 Questions about their experience and projects
            4. 2 Situational questions
            5. 1 Question about career goals

            Return each question on a new line, numbered 1-{num_questions}.
            """

        try:
            response = self.model.generate_content(prompt)
            questions = []
            for line in response.text.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    # Remove numbering and clean up
                    question = re.sub(r"^\d+\.?\s*", "", line)
                    question = re.sub(r"^-\s*", "", question)
                    if question:
                        questions.append(question.strip())
            # Ensure we return exactly the configured number of questions
            return questions[:num_questions]
        except Exception as e:
            print(f"Error generating questions: {e}")
            # Return fallback questions in the appropriate language
            if language == "vi":
                return [
                    "Hãy kể về bản thân và nền tảng của bạn.",
                    "Điểm mạnh lớn nhất của bạn là gì?",
                    "Mô tả một dự án thử thách mà bạn đã làm.",
                    "Bạn xử lý deadline gấp như thế nào?",
                    "Điều gì khiến bạn quan tâm đến vị trí này?",
                    "Kể về một lần bạn làm việc trong nhóm.",
                    "Bạn cập nhật công nghệ mới như thế nào?",
                    "Mục tiêu nghề nghiệp của bạn là gì?",
                    "Mô tả một vấn đề bạn đã giải quyết một cách sáng tạo.",
                    "Tại sao chúng tôi nên tuyển bạn?",
                ]
            else:
                return [
                    "Tell me about yourself and your background.",
                    "What are your greatest strengths?",
                    "Describe a challenging project you worked on.",
                    "How do you handle tight deadlines?",
                    "What interests you about this role?",
                    "Tell me about a time you worked in a team.",
                    "How do you stay updated with new technologies?",
                    "What are your career goals?",
                    "Describe a problem you solved creatively.",
                    "Why should we hire you?",
                ]

    def evaluate_answer(self, question, answer):
        """Evaluate interview answer using AI and similarity scoring"""
        if not answer.strip():
            return {
                "score": 0,
                "feedback": "No answer provided.",
                "strengths": [],
                "improvements": ["Provide a complete answer to the question."],
                "suggestions": [
                    "Take time to think about your response before answering."
                ],
            }

        # Generate ideal answer for comparison
        ideal_prompt = f"""
        Provide a concise, professional answer (100-150 words) to this interview question:
        "{question}"

        Focus on being specific, relevant, and showing competence.
        """

        try:
            ideal_response = self.model.generate_content(ideal_prompt)
            ideal_answer = ideal_response.text.strip()

            # Calculate similarity using TF-IDF
            similarity_score = self._calculate_similarity(ideal_answer, answer)

            # Generate detailed feedback
            feedback_prompt = f"""
            Evaluate this interview answer and provide constructive feedback:

            Question: "{question}"

            Candidate's Answer: "{answer}"

            Ideal Answer: "{ideal_answer}"

            Provide feedback in this exact format:
            SCORE: [number from 0-100]
            STRENGTHS: [list 2-3 positive aspects]
            IMPROVEMENTS: [list 2-3 areas to improve]
            SUGGESTIONS: [list 2-3 specific suggestions]

            Be constructive and specific in your feedback.
            """

            feedback_response = self.model.generate_content(feedback_prompt)
            feedback_text = feedback_response.text.strip()

            # Parse feedback
            parsed_feedback = self._parse_feedback(feedback_text)

            # Combine AI score with similarity score
            ai_score = parsed_feedback.get("score", similarity_score)
            final_score = round((ai_score + similarity_score) / 2, 1)

            return {
                "score": final_score,
                "feedback": feedback_text,
                "strengths": parsed_feedback.get("strengths", []),
                "improvements": parsed_feedback.get("improvements", []),
                "suggestions": parsed_feedback.get("suggestions", []),
                "ideal_answer": ideal_answer,
            }

        except Exception as e:
            print(f"Error evaluating answer: {e}")
            # Fallback evaluation
            word_count = len(answer.split())
            basic_score = min(word_count * 2, 100) if word_count > 0 else 0

            return {
                "score": basic_score,
                "feedback": "Answer evaluated. Provide more specific examples and details.",
                "strengths": ["Attempted to answer the question"],
                "improvements": [
                    "Provide more specific examples",
                    "Elaborate on key points",
                ],
                "suggestions": [
                    "Use the STAR method for behavioral questions",
                    "Include concrete examples",
                ],
                "ideal_answer": "A comprehensive answer with specific examples and clear explanations.",
            }

    def _calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts using TF-IDF"""
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(similarity * 100, 1)
        except:
            return 50.0  # Default similarity if calculation fails

    def _parse_feedback(self, feedback_text):
        """Parse structured feedback from AI response"""
        result = {"score": 70, "strengths": [], "improvements": [], "suggestions": []}

        # Extract score
        score_match = re.search(r"SCORE:\s*(\d+)", feedback_text, re.IGNORECASE)
        if score_match:
            result["score"] = int(score_match.group(1))

        # Extract strengths
        strengths_match = re.search(
            r"STRENGTHS:\s*(.+?)(?=IMPROVEMENTS:|$)",
            feedback_text,
            re.IGNORECASE | re.DOTALL,
        )
        if strengths_match:
            strengths_text = strengths_match.group(1).strip()
            result["strengths"] = [
                s.strip() for s in re.split(r"[•\-*\n]", strengths_text) if s.strip()
            ]

        # Extract improvements
        improvements_match = re.search(
            r"IMPROVEMENTS:\s*(.+?)(?=SUGGESTIONS:|$)",
            feedback_text,
            re.IGNORECASE | re.DOTALL,
        )
        if improvements_match:
            improvements_text = improvements_match.group(1).strip()
            result["improvements"] = [
                s.strip() for s in re.split(r"[•\-*\n]", improvements_text) if s.strip()
            ]

        # Extract suggestions
        suggestions_match = re.search(
            r"SUGGESTIONS:\s*(.+?)$", feedback_text, re.IGNORECASE | re.DOTALL
        )
        if suggestions_match:
            suggestions_text = suggestions_match.group(1).strip()
            result["suggestions"] = [
                s.strip() for s in re.split(r"[•\-*\n]", suggestions_text) if s.strip()
            ]

        return result

    def generate_follow_up(self, question, answer):
        """Generate follow-up question based on the answer"""
        prompt = f"""
        Based on this interview exchange, generate a relevant follow-up question:

        Original Question: "{question}"
        Candidate's Answer: "{answer}"

        Generate a follow-up question that:
        1. Builds on their answer
        2. Seeks more specific details
        3. Is appropriate for an interview setting

        Return only the follow-up question.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating follow-up: {e}")
            return "Can you provide a specific example to illustrate your point?"

    def generate_overall_evaluation(self, transcript, evaluations):
        """Generate overall interview evaluation"""
        avg_score = (
            np.mean([eval_data.get("score", 0) for eval_data in evaluations])
            if evaluations
            else 0
        )

        prompt = f"""
        Based on this complete interview transcript and performance, provide an overall evaluation:

        Average Score: {avg_score:.1f}/100

        Transcript:
        {transcript}

        Provide evaluation in this format:
        OVERALL_SCORE: [0-100]
        TECHNICAL_SKILLS: [0-100]
        COMMUNICATION: [0-100]
        PROBLEM_SOLVING: [0-100]
        SUMMARY: [2-3 sentence summary]
        STRENGTHS: [top 3 strengths]
        AREAS_FOR_IMPROVEMENT: [top 3 areas]
        RECOMMENDATIONS: [3-4 specific recommendations]
        """

        try:
            response = self.model.generate_content(prompt)
            return self._parse_overall_evaluation(response.text)
        except Exception as e:
            print(f"Error generating overall evaluation: {e}")
            return {
                "overall_score": avg_score,
                "technical_skills": avg_score,
                "communication": avg_score,
                "problem_solving": avg_score,
                "summary": "Interview completed with average performance.",
                "strengths": ["Attempted all questions"],
                "areas_for_improvement": ["Provide more specific examples"],
                "recommendations": ["Practice common interview questions"],
            }

    def _parse_overall_evaluation(self, evaluation_text):
        """Parse overall evaluation response"""
        result = {}

        # Extract numerical scores
        for field in [
            "overall_score",
            "technical_skills",
            "communication",
            "problem_solving",
        ]:
            pattern = field.replace("_", "_").upper() + r":\s*(\d+)"
            match = re.search(pattern, evaluation_text, re.IGNORECASE)
            if match:
                result[field] = int(match.group(1))
            else:
                result[field] = 70  # Default score

        # Extract text fields
        for field in [
            "summary",
            "strengths",
            "areas_for_improvement",
            "recommendations",
        ]:
            pattern = field.replace("_", "_").upper() + r":\s*(.+?)(?=[A-Z_]+:|$)"
            match = re.search(pattern, evaluation_text, re.IGNORECASE | re.DOTALL)
            if match:
                text = match.group(1).strip()
                if field in ["strengths", "areas_for_improvement", "recommendations"]:
                    result[field] = [
                        s.strip() for s in re.split(r"[•\-*\n]", text) if s.strip()
                    ]
                else:
                    result[field] = text
            else:
                result[field] = f"No {field.replace('_', ' ')} provided."

        return result
