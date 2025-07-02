# Dashboard routes
from flask import Blueprint, jsonify
from models.interview import Interview
from models.resume import Resume
from models.user import User
from routes.auth import token_required
from services.analytics import ReportGenerator
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)
report_gen = ReportGenerator()

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    """Get user dashboard statistics"""
    try:
        # Get user's interviews and resumes
        interviews = Interview.query.filter_by(user_id=current_user.id).order_by(Interview.created_at.desc()).all()
        resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
        
        # Calculate statistics
        total_interviews = len(interviews)
        completed_interviews = [i for i in interviews if i.end_time is not None]
        
        # Calculate average scores
        avg_scores = {
            'technical': 0,
            'communication': 0,
            'problem_solving': 0,
            'overall': 0
        }
        
        if completed_interviews:
            for interview in completed_interviews:
                if interview.evaluation and isinstance(interview.evaluation, dict):
                    avg_scores['technical'] += interview.evaluation.get('technical_skills', 0)
                    avg_scores['communication'] += interview.evaluation.get('communication', 0)
                    avg_scores['problem_solving'] += interview.evaluation.get('problem_solving', 0)
                    avg_scores['overall'] += interview.evaluation.get('overall_score', 0)
            
            # Calculate averages
            for key in avg_scores:
                avg_scores[key] = round(avg_scores[key] / len(completed_interviews), 1)
        
        # Get recent interview performance (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_interviews = [i for i in interviews if i.created_at >= thirty_days_ago]
        
        # Calculate improvement trend
        improvement_trend = "stable"
        if len(completed_interviews) >= 2:
            recent_scores = [i.evaluation.get('overall_score', 0) for i in completed_interviews[:3] if i.evaluation]
            older_scores = [i.evaluation.get('overall_score', 0) for i in completed_interviews[-3:] if i.evaluation]
            
            if recent_scores and older_scores:
                recent_avg = sum(recent_scores) / len(recent_scores)
                older_avg = sum(older_scores) / len(older_scores)
                
                if recent_avg > older_avg + 5:
                    improvement_trend = "improving"
                elif recent_avg < older_avg - 5:
                    improvement_trend = "declining"
        
        # Prepare recent interviews data
        recent_interviews_data = []
        for interview in interviews[:5]:  # Last 5 interviews
            interview_data = {
                'id': interview.id,
                'date': interview.created_at.strftime('%Y-%m-%d'),
                'completed': interview.end_time is not None,
                'score': interview.evaluation.get('overall_score', 0) if interview.evaluation else 0,
                'duration': str(interview.end_time - interview.start_time) if interview.start_time and interview.end_time else None
            }
            recent_interviews_data.append(interview_data)
        
        # Skills analysis
        skills_analysis = {}
        if resumes:
            latest_resume = resumes[0]
            if latest_resume.parsed_data and 'skills' in latest_resume.parsed_data:
                skills_analysis = {
                    'total_skills': len(latest_resume.parsed_data['skills']),
                    'top_skills': latest_resume.parsed_data['skills'][:5],
                    'experience_years': len(latest_resume.parsed_data.get('experience', []))
                }
        
        return jsonify({
            'user_name': current_user.full_name or 'User',
            'total_interviews': total_interviews,
            'completed_interviews': len(completed_interviews),
            'total_resumes': len(resumes),
            'average_scores': avg_scores,
            'improvement_trend': improvement_trend,
            'recent_interviews': recent_interviews_data,
            'skills_analysis': skills_analysis,
            'last_interview_date': interviews[0].created_at.strftime('%Y-%m-%d') if interviews else None,
            'member_since': current_user.created_at.strftime('%Y-%m-%d') if current_user.created_at else None
        })
        
    except Exception as e:
        print(f"Dashboard stats error: {e}")
        return jsonify({'error': 'Failed to load dashboard statistics'}), 500

@dashboard_bp.route('/analytics', methods=['GET'])
@token_required
def get_analytics(current_user):
    """Get detailed analytics for the user"""
    try:
        interviews = Interview.query.filter_by(user_id=current_user.id).order_by(Interview.created_at.desc()).all()
        completed_interviews = [i for i in interviews if i.end_time is not None]
        
        if not completed_interviews:
            return jsonify({
                'message': 'No completed interviews found',
                'performance_over_time': [],
                'skills_breakdown': {},
                'recommendations': []
            })
        
        # Generate analytics summary
        analytics_summary = report_gen.generate_analytics_summary([
            {
                'evaluation': interview.evaluation,
                'date': interview.created_at,
                'transcript': interview.transcript
            }
            for interview in completed_interviews
        ])
        
        # Performance over time
        performance_data = []
        for interview in completed_interviews:
            if interview.evaluation:
                performance_data.append({
                    'date': interview.created_at.strftime('%Y-%m-%d'),
                    'overall_score': interview.evaluation.get('overall_score', 0),
                    'technical_skills': interview.evaluation.get('technical_skills', 0),
                    'communication': interview.evaluation.get('communication', 0),
                    'problem_solving': interview.evaluation.get('problem_solving', 0)
                })
        
        # Skills breakdown across all interviews
        skills_breakdown = {
            'Technical Skills': sum([i.evaluation.get('technical_skills', 0) for i in completed_interviews]) / len(completed_interviews),
            'Communication': sum([i.evaluation.get('communication', 0) for i in completed_interviews]) / len(completed_interviews),
            'Problem Solving': sum([i.evaluation.get('problem_solving', 0) for i in completed_interviews]) / len(completed_interviews)
        }
        
        # Generate recommendations based on performance
        weak_areas = []
        if skills_breakdown['Technical Skills'] < 70:
            weak_areas.append("Focus on technical skill development")
        if skills_breakdown['Communication'] < 70:
            weak_areas.append("Practice communication and presentation skills")
        if skills_breakdown['Problem Solving'] < 70:
            weak_areas.append("Work on problem-solving methodologies")
        
        return jsonify({
            'analytics_summary': analytics_summary,
            'performance_over_time': performance_data,
            'skills_breakdown': skills_breakdown,
            'recommendations': weak_areas,
            'total_practice_time': len(completed_interviews) * 30,  # Estimate 30 mins per interview
            'strongest_skill': max(skills_breakdown, key=skills_breakdown.get),
            'weakest_skill': min(skills_breakdown, key=skills_breakdown.get)
        })
        
    except Exception as e:
        print(f"Analytics error: {e}")
        return jsonify({'error': 'Failed to generate analytics'}), 500

@dashboard_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get user profile information"""
    try:
        # Get latest resume info
        latest_resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).first()
        
        profile_data = {
            'user_id': current_user.id,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'member_since': current_user.created_at.strftime('%Y-%m-%d') if current_user.created_at else None,
            'has_resume': latest_resume is not None
        }
        
        if latest_resume and latest_resume.parsed_data:
            profile_data.update({
                'resume_name': latest_resume.parsed_data.get('name', ''),
                'skills_count': len(latest_resume.parsed_data.get('skills', [])),
                'experience_count': len(latest_resume.parsed_data.get('experience', [])),
                'projects_count': len(latest_resume.parsed_data.get('projects', [])),
                'last_resume_update': latest_resume.created_at.strftime('%Y-%m-%d')
            })
        
        return jsonify(profile_data)
        
    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({'error': 'Failed to load profile information'}), 500