from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models.resume import Resume
from models.interview import Interview
from models.db import db
from services.ai_engine import InterviewEngine
from services.voice_processor import VoiceProcessor
from services.analytics import ReportGenerator
from services.pdf_parser import PDFParser
from routes.auth import token_required
import uuid
import os
from datetime import datetime
from config import Config

interview_bp = Blueprint("interview", __name__)

# Initialize services
voice_processor = VoiceProcessor()
report_gen = ReportGenerator()
pdf_parser = PDFParser()

# We'll create language-specific engines as needed


@interview_bp.route("/resume", methods=["POST"])
@token_required
def upload_resume(current_user):
    """Handle resume upload (file or text)"""
    try:
        text_content = ""
        filepath = None

        if "file" in request.files:
            # Handle file upload
            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "No selected file"}), 400

            if not file.filename.lower().endswith(".pdf"):
                return jsonify({"error": "Only PDF files are supported"}), 400

            # Secure filename and save
            original_filename = secure_filename(file.filename)
            filename = (
                f"resume_{current_user.id}_{uuid.uuid4().hex}_{original_filename}"
            )
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

            # Ensure upload directory exists
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)

            # Extract text from PDF
            text_content = pdf_parser.extract_text_from_pdf(filepath)

            if not text_content or text_content.startswith("Error"):
                return jsonify({"error": "Could not extract text from PDF file"}), 400

        elif request.json and "text" in request.json:
            # Handle text input
            text_content = request.json["text"].strip()
            if not text_content:
                return jsonify({"error": "Resume text cannot be empty"}), 400
        else:
            return (
                jsonify(
                    {
                        "error": "No resume data provided. Please upload a PDF file or provide text."
                    }
                ),
                400,
            )

        # Parse resume with AI (use user's preferred language or default)
        try:
            user_language = current_user.preferred_language or Config.DEFAULT_LANGUAGE
            engine = InterviewEngine(language=user_language)
            parsed_data = engine.parse_resume(text_content)
        except Exception as e:
            print(f"Resume parsing error: {e}")
            return (
                jsonify(
                    {
                        "error": "Failed to parse resume. Please check the content and try again."
                    }
                ),
                500,
            )

        # Save to database
        resume = Resume(
            user_id=current_user.id,
            text_content=text_content,
            file_path=filepath,
            parsed_data=parsed_data,
        )

        db.session.add(resume)
        db.session.commit()

        return jsonify(
            {
                "message": "Resume processed successfully",
                "resume_id": resume.id,
                "parsed_data": parsed_data,
                "skills_found": len(parsed_data.get("skills", [])),
                "experience_count": len(parsed_data.get("experience", [])),
            }
        )

    except Exception as e:
        print(f"Resume upload error: {e}")
        return jsonify({"error": "Failed to process resume. Please try again."}), 500


@interview_bp.route("/start", methods=["POST"])
@token_required
def start_interview(current_user):
    """Start a new interview session"""
    try:
        data = request.get_json()
        if not data or "resume_id" not in data:
            return jsonify({"error": "resume_id is required"}), 400

        resume_id = data["resume_id"]
        language = data.get(
            "language", current_user.preferred_language or Config.DEFAULT_LANGUAGE
        )
        resume = Resume.query.get(resume_id)

        if not resume or resume.user_id != current_user.id:
            return jsonify({"error": "Resume not found or access denied"}), 404

        if not resume.parsed_data:
            return (
                jsonify(
                    {
                        "error": "Resume data is incomplete. Please upload the resume again."
                    }
                ),
                400,
            )

        # Validate language
        if language not in Config.SUPPORTED_LANGUAGES:
            language = Config.DEFAULT_LANGUAGE

        # Create language-specific engine
        engine = InterviewEngine(language=language)

        # Generate questions based on resume
        try:
            questions = engine.generate_questions(resume.parsed_data, language=language)
        except Exception as e:
            print(f"Question generation error: {e}")
            return (
                jsonify(
                    {
                        "error": "Failed to generate interview questions. Please try again."
                    }
                ),
                500,
            )

        # Create interview record
        interview = Interview(
            user_id=current_user.id,
            language=language,
            start_time=datetime.utcnow(),
            transcript="",
            evaluation={},
        )

        db.session.add(interview)
        db.session.commit()

        return jsonify(
            {
                "interview_id": interview.id,
                "questions": questions,
                "message": f"Interview started successfully. {len(questions)} questions generated.",
                "candidate_name": resume.parsed_data.get("name", "Candidate"),
            }
        )

    except Exception as e:
        print(f"Start interview error: {e}")
        return jsonify({"error": "Failed to start interview. Please try again."}), 500


@interview_bp.route("/process", methods=["POST"])
@token_required
def process_answer(current_user):
    """Process an interview answer (audio or text)"""
    try:
        # Get form data
        interview_id = request.form.get("interview_id")
        question = request.form.get("question")
        text_answer = request.form.get("text_answer")
        audio_file = request.files.get("audio")

        if not interview_id or not question:
            return jsonify({"error": "interview_id and question are required"}), 400

        # Validate interview
        interview = Interview.query.get(interview_id)
        if not interview or interview.user_id != current_user.id:
            return jsonify({"error": "Interview not found or access denied"}), 404

        # Process answer based on input type
        answer_text = ""

        if audio_file and audio_file.filename:
            # Process audio file
            filename = f"answer_{interview_id}_{uuid.uuid4().hex}.wav"
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

            # Ensure upload directory exists
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            audio_file.save(filepath)

            # Transcribe audio using interview language
            try:
                # Get the language from the interview record
                interview_language = interview.language or Config.DEFAULT_LANGUAGE
                answer_text = voice_processor.speech_to_text(
                    filepath, language=interview_language
                )
                if (
                    not answer_text
                    or answer_text.startswith("Error")
                    or answer_text.startswith("Audio")
                ):
                    return (
                        jsonify(
                            {
                                "error": "Could not transcribe audio. Please try again or use text input."
                            }
                        ),
                        400,
                    )
            except Exception as e:
                print(f"Audio processing error: {e}")
                return (
                    jsonify(
                        {"error": "Failed to process audio. Please try text input."}
                    ),
                    500,
                )
            finally:
                # Clean up audio file
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        pass

        elif text_answer:
            answer_text = text_answer.strip()
        else:
            return (
                jsonify({"error": "Either audio file or text answer is required"}),
                400,
            )

        if not answer_text:
            return jsonify({"error": "No answer content received"}), 400

        # Evaluate answer using interview language
        try:
            interview_language = interview.language or Config.DEFAULT_LANGUAGE
            engine = InterviewEngine(language=interview_language)
            evaluation = engine.evaluate_answer(question, answer_text)
        except Exception as e:
            print(f"Answer evaluation error: {e}")
            return (
                jsonify({"error": "Failed to evaluate answer. Please try again."}),
                500,
            )

        # Update interview transcript and evaluation
        current_transcript = interview.transcript or ""
        new_transcript = f"{current_transcript}\n\nQ: {question}\nA: {answer_text}"

        # Store current evaluation in interview record
        current_evaluations = interview.evaluation or {}
        if "answers" not in current_evaluations:
            current_evaluations["answers"] = []

        current_evaluations["answers"].append(
            {
                "question": question,
                "answer": answer_text,
                "evaluation": evaluation,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        interview.transcript = new_transcript
        interview.evaluation = current_evaluations
        db.session.commit()

        # Generate follow-up question (engine already created above)
        try:
            follow_up = engine.generate_follow_up(question, answer_text)
        except Exception as e:
            print(f"Follow-up generation error: {e}")
            follow_up = "Thank you for your answer. Let's move to the next question."

        return jsonify(
            {
                "message": "Answer processed successfully",
                "transcript": answer_text,
                "evaluation": evaluation,
                "next_question": follow_up,
                "score": evaluation.get("score", 0),
            }
        )

    except Exception as e:
        print(f"Process answer error: {e}")
        return jsonify({"error": "Failed to process answer. Please try again."}), 500


@interview_bp.route("/complete/<int:interview_id>", methods=["POST"])
@token_required
def complete_interview(current_user, interview_id):
    """Complete an interview and generate final report"""
    try:
        interview = Interview.query.get(interview_id)
        if not interview or interview.user_id != current_user.id:
            return jsonify({"error": "Interview not found or access denied"}), 404

        if interview.end_time:
            return jsonify({"error": "Interview already completed"}), 400

        # Set end time
        interview.end_time = datetime.utcnow()

        # Get all answer evaluations
        evaluations = (
            interview.evaluation.get("answers", []) if interview.evaluation else []
        )

        if not evaluations:
            return jsonify({"error": "No answers found for this interview"}), 400

        # Generate overall evaluation using interview language
        try:
            interview_language = interview.language or Config.DEFAULT_LANGUAGE
            engine = InterviewEngine(language=interview_language)
            overall_eval = engine.generate_overall_evaluation(
                interview.transcript, evaluations
            )
        except Exception as e:
            print(f"Overall evaluation error: {e}")
            # Fallback evaluation
            scores = [
                eval_data.get("evaluation", {}).get("score", 0)
                for eval_data in evaluations
            ]
            avg_score = sum(scores) / len(scores) if scores else 0
            overall_eval = {
                "overall_score": round(avg_score, 1),
                "technical_skills": round(avg_score, 1),
                "communication": round(avg_score, 1),
                "problem_solving": round(avg_score, 1),
                "summary": f"Interview completed with an average score of {avg_score:.1f}/100.",
                "strengths": ["Completed the interview"],
                "areas_for_improvement": ["Provide more detailed answers"],
                "recommendations": ["Practice more interview questions"],
            }

        # Update interview evaluation with overall results
        interview.evaluation.update(overall_eval)

        # Generate comprehensive report
        report_data = {
            "user_name": current_user.full_name or "Candidate",
            "transcript": interview.transcript,
            "duration": (
                str(interview.end_time - interview.start_time)
                if interview.start_time
                else "Unknown"
            ),
            "overall_score": overall_eval.get("overall_score", 0),
            "skills": {
                "Technical Skills": overall_eval.get("technical_skills", 0),
                "Communication": overall_eval.get("communication", 0),
                "Problem Solving": overall_eval.get("problem_solving", 0),
            },
            "summary": overall_eval.get("summary", ""),
            "strengths": overall_eval.get("strengths", []),
            "areas_for_improvement": overall_eval.get("areas_for_improvement", []),
            "recommendations": overall_eval.get("recommendations", []),
        }

        try:
            # Generate PDF report
            report_bytes = report_gen.generate_report(report_data)
            report_filename = f"interview_report_{interview_id}_{uuid.uuid4().hex}.pdf"
            report_path = os.path.join(Config.UPLOAD_FOLDER, report_filename)

            # Ensure upload directory exists
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

            with open(report_path, "wb") as f:
                f.write(report_bytes)

            interview.report_path = report_path

        except Exception as e:
            print(f"Report generation error: {e}")
            interview.report_path = None

        db.session.commit()

        return jsonify(
            {
                "message": "Interview completed successfully",
                "interview_id": interview_id,
                "overall_score": overall_eval.get("overall_score", 0),
                "report_url": (
                    f"/static/uploads/{report_filename}"
                    if interview.report_path
                    else None
                ),
                "summary": overall_eval.get("summary", ""),
                "strengths": overall_eval.get("strengths", []),
                "areas_for_improvement": overall_eval.get("areas_for_improvement", []),
                "recommendations": overall_eval.get("recommendations", []),
                "skills_breakdown": report_data["skills"],
            }
        )

    except Exception as e:
        print(f"Complete interview error: {e}")
        return (
            jsonify({"error": "Failed to complete interview. Please try again."}),
            500,
        )


@interview_bp.route("/history", methods=["GET"])
@token_required
def get_interview_history(current_user):
    """Get user's interview history"""
    try:
        interviews = (
            Interview.query.filter_by(user_id=current_user.id)
            .order_by(Interview.created_at.desc())
            .all()
        )

        history = []
        for interview in interviews:
            history.append(
                {
                    "id": interview.id,
                    "start_time": (
                        interview.start_time.isoformat()
                        if interview.start_time
                        else None
                    ),
                    "end_time": (
                        interview.end_time.isoformat() if interview.end_time else None
                    ),
                    "duration": (
                        str(interview.end_time - interview.start_time)
                        if interview.start_time and interview.end_time
                        else None
                    ),
                    "overall_score": (
                        interview.evaluation.get("overall_score", 0)
                        if interview.evaluation
                        else 0
                    ),
                    "completed": interview.end_time is not None,
                    "report_available": interview.report_path is not None,
                }
            )

        return jsonify({"interviews": history, "total_count": len(history)})

    except Exception as e:
        print(f"Get history error: {e}")
        return jsonify({"error": "Failed to retrieve interview history"}), 500


@interview_bp.route("/report/<int:interview_id>", methods=["GET"])
@token_required
def get_interview_report(current_user, interview_id):
    """Get comprehensive interview report with detailed analysis"""
    try:
        interview = Interview.query.get(interview_id)
        if not interview or interview.user_id != current_user.id:
            return jsonify({"error": "Interview not found or access denied"}), 404

        if not interview.end_time:
            return jsonify({"error": "Interview not completed yet"}), 400

        # Extract evaluation data
        evaluation_data = interview.evaluation or {}
        answers_data = evaluation_data.get("answers", [])

        # Process individual answer evaluations
        detailed_answers = []
        total_score = 0
        answer_count = 0

        for answer_data in answers_data:
            eval_info = answer_data.get("evaluation", {})
            score = eval_info.get("score", 0)
            total_score += score
            answer_count += 1

            detailed_answers.append(
                {
                    "question": answer_data.get("question", ""),
                    "answer": answer_data.get("answer", ""),
                    "score": score,
                    "feedback": eval_info.get("feedback", ""),
                    "strengths": eval_info.get("strengths", []),
                    "improvements": eval_info.get("improvements", []),
                    "suggestions": eval_info.get("suggestions", []),
                    "ideal_answer": eval_info.get("ideal_answer", ""),
                    "timestamp": answer_data.get("timestamp", ""),
                }
            )

        # Calculate average score
        average_score = round(total_score / answer_count, 1) if answer_count > 0 else 0

        # Extract overall evaluation scores
        overall_score = evaluation_data.get("overall_score", average_score)
        technical_skills = evaluation_data.get("technical_skills", average_score)
        communication = evaluation_data.get("communication", average_score)
        problem_solving = evaluation_data.get("problem_solving", average_score)

        # Calculate duration
        duration_str = None
        duration_minutes = None
        if interview.start_time and interview.end_time:
            duration_delta = interview.end_time - interview.start_time
            duration_minutes = round(duration_delta.total_seconds() / 60, 1)
            duration_str = str(duration_delta)

        # Generate report URL if available
        report_url = None
        if interview.report_path and os.path.exists(interview.report_path):
            report_filename = os.path.basename(interview.report_path)
            report_url = f"/static/uploads/{report_filename}"

        # Prepare comprehensive report data
        report_data = {
            "interview_info": {
                "interview_id": interview.id,
                "candidate_name": current_user.full_name or current_user.email,
                "start_time": (
                    interview.start_time.isoformat() if interview.start_time else None
                ),
                "end_time": (
                    interview.end_time.isoformat() if interview.end_time else None
                ),
                "duration": duration_str,
                "duration_minutes": duration_minutes,
                "total_questions": answer_count,
                "completed": True,
            },
            "performance_summary": {
                "overall_score": overall_score,
                "average_score": average_score,
                "technical_skills": technical_skills,
                "communication": communication,
                "problem_solving": problem_solving,
                "performance_level": get_performance_level(overall_score),
            },
            "detailed_analysis": {
                "summary": evaluation_data.get(
                    "summary", "Interview completed successfully."
                ),
                "strengths": evaluation_data.get("strengths", []),
                "areas_for_improvement": evaluation_data.get(
                    "areas_for_improvement", []
                ),
                "recommendations": evaluation_data.get("recommendations", []),
            },
            "question_by_question": detailed_answers,
            "transcript": interview.transcript,
            "report_url": report_url,
            "statistics": {
                "highest_score": max(
                    [ans["score"] for ans in detailed_answers], default=0
                ),
                "lowest_score": min(
                    [ans["score"] for ans in detailed_answers], default=0
                ),
                "questions_above_70": len(
                    [ans for ans in detailed_answers if ans["score"] >= 70]
                ),
                "questions_below_50": len(
                    [ans for ans in detailed_answers if ans["score"] < 50]
                ),
            },
        }

        return jsonify(report_data)

    except Exception as e:
        print(f"Get report error: {e}")
        return jsonify({"error": "Failed to retrieve interview report"}), 500


def get_performance_level(score):
    """Get performance level based on score"""
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Very Good"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Fair"
    else:
        return "Needs Improvement"

