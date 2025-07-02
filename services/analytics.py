from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from io import BytesIO
import base64
import numpy as np
import os
import tempfile

class ReportGenerator:
    def __init__(self):
        """Initialize the report generator"""
        self.pdf = None
    
    def generate_report(self, interview_data):
        """Generate a comprehensive PDF report for the interview"""
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font('Arial', 'B', 20)
            pdf.set_text_color(0, 100, 200)
            pdf.cell(0, 15, 'AI Interview Assessment Report', 0, 1, 'C')
            pdf.ln(5)
            
            # Add a line
            pdf.set_draw_color(0, 100, 200)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(10)
            
            # Candidate Information
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, 'Candidate Information', 0, 1)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f"Name: {interview_data.get('user_name', 'N/A')}", 0, 1)
            pdf.cell(0, 8, f"Date: {datetime.now().strftime('%B %d, %Y at %H:%M')}", 0, 1)
            pdf.cell(0, 8, f"Interview Duration: {interview_data.get('duration', 'N/A')}", 0, 1)
            pdf.ln(10)
            
            # Overall Score
            overall_score = interview_data.get('overall_score', 0)
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, f'Overall Score: {overall_score}/100', 0, 1)
            
            # Score interpretation
            pdf.set_font('Arial', '', 12)
            if overall_score >= 85:
                interpretation = "Excellent performance"
                pdf.set_text_color(0, 150, 0)
            elif overall_score >= 70:
                interpretation = "Good performance"
                pdf.set_text_color(0, 100, 0)
            elif overall_score >= 50:
                interpretation = "Average performance"
                pdf.set_text_color(200, 100, 0)
            else:
                interpretation = "Needs improvement"
                pdf.set_text_color(200, 0, 0)
            
            pdf.cell(0, 8, f"Assessment: {interpretation}", 0, 1)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(10)
            
            # Skills Breakdown
            if 'skills' in interview_data and interview_data['skills']:
                self._add_skills_section(pdf, interview_data['skills'])
            
            # Performance Summary
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Performance Summary', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            summary = interview_data.get('summary', 'Performance summary not available.')
            pdf.multi_cell(0, 6, summary)
            pdf.ln(5)
            
            # Strengths
            if 'strengths' in interview_data and interview_data['strengths']:
                pdf.set_font('Arial', 'B', 14)
                pdf.set_text_color(0, 150, 0)
                pdf.cell(0, 10, 'Key Strengths', 0, 1)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 12)
                
                for i, strength in enumerate(interview_data['strengths'][:5], 1):
                    pdf.cell(0, 6, f"{i}. {strength}", 0, 1)
                pdf.ln(5)
            
            # Areas for Improvement
            if 'areas_for_improvement' in interview_data and interview_data['areas_for_improvement']:
                pdf.set_font('Arial', 'B', 14)
                pdf.set_text_color(200, 100, 0)
                pdf.cell(0, 10, 'Areas for Improvement', 0, 1)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 12)
                
                for i, area in enumerate(interview_data['areas_for_improvement'][:5], 1):
                    pdf.cell(0, 6, f"{i}. {area}", 0, 1)
                pdf.ln(5)
            
            # Recommendations
            if 'recommendations' in interview_data and interview_data['recommendations']:
                pdf.set_font('Arial', 'B', 14)
                pdf.set_text_color(0, 100, 200)
                pdf.cell(0, 10, 'Recommendations', 0, 1)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 12)
                
                if isinstance(interview_data['recommendations'], list):
                    for i, rec in enumerate(interview_data['recommendations'][:5], 1):
                        pdf.multi_cell(0, 6, f"{i}. {rec}")
                        pdf.ln(2)
                else:
                    pdf.multi_cell(0, 6, interview_data['recommendations'])
                pdf.ln(5)
            
            # Interview Transcript (if available and not too long)
            if 'transcript' in interview_data and interview_data['transcript']:
                transcript = interview_data['transcript']
                if len(transcript) < 2000:  # Only include if not too long
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 14)
                    pdf.cell(0, 10, 'Interview Transcript', 0, 1)
                    pdf.set_font('Arial', '', 10)
                    pdf.multi_cell(0, 5, transcript[:1500] + "..." if len(transcript) > 1500 else transcript)
            
            # Footer
            pdf.ln(10)
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 10, 'Generated by AI Interview CRM Platform', 0, 1, 'C')
            
            return pdf.output(dest='S').encode('latin1')
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return self._generate_basic_report(interview_data)
    
    def _add_skills_section(self, pdf, skills_data):
        """Add skills breakdown section to the PDF"""
        try:
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Skills Assessment', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            # Display skills as text (simpler approach)
            for skill_name, score in skills_data.items():
                pdf.cell(0, 8, f"{skill_name}: {score}/100", 0, 1)
                
                # Add a simple progress bar using characters
                progress = int(score / 10)  # Convert to 0-10 scale
                bar = "█" * progress + "░" * (10 - progress)
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 6, f"  {bar} {score}%", 0, 1)
                pdf.set_font('Arial', '', 12)
            
            pdf.ln(10)
            
        except Exception as e:
            print(f"Error adding skills section: {e}")
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, "Skills assessment data unavailable", 0, 1)
            pdf.ln(5)
    
    def _generate_basic_report(self, interview_data):
        """Generate a basic report if the main report generation fails"""
        try:
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Interview Report', 0, 1, 'C')
            pdf.ln(10)
            
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f"Candidate: {interview_data.get('user_name', 'N/A')}", 0, 1)
            pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
            pdf.cell(0, 8, f"Overall Score: {interview_data.get('overall_score', 'N/A')}/100", 0, 1)
            pdf.ln(10)
            
            if 'summary' in interview_data:
                pdf.cell(0, 8, 'Summary:', 0, 1)
                pdf.multi_cell(0, 6, interview_data['summary'])
            
            return pdf.output(dest='S').encode('latin1')
            
        except Exception as e:
            print(f"Error generating basic report: {e}")
            # Return minimal report
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, 'Report generation failed', 0, 1)
            return pdf.output(dest='S').encode('latin1')
    
    def generate_analytics_summary(self, user_interviews):
        """Generate analytics summary for multiple interviews"""
        if not user_interviews:
            return {
                'total_interviews': 0,
                'average_score': 0,
                'improvement_trend': 'No data available',
                'top_skills': [],
                'areas_to_focus': []
            }
        
        try:
            total_interviews = len(user_interviews)
            scores = [interview.get('evaluation', {}).get('overall_score', 0) for interview in user_interviews]
            average_score = sum(scores) / len(scores) if scores else 0
            
            # Calculate improvement trend
            if len(scores) >= 2:
                recent_avg = sum(scores[-3:]) / min(3, len(scores))
                early_avg = sum(scores[:3]) / min(3, len(scores))
                trend = "Improving" if recent_avg > early_avg else "Declining" if recent_avg < early_avg else "Stable"
            else:
                trend = "Insufficient data"
            
            return {
                'total_interviews': total_interviews,
                'average_score': round(average_score, 1),
                'improvement_trend': trend,
                'highest_score': max(scores) if scores else 0,
                'lowest_score': min(scores) if scores else 0,
                'score_trend': scores[-10:]  # Last 10 scores for trending
            }
            
        except Exception as e:
            print(f"Error generating analytics: {e}")
            return {
                'total_interviews': 0,
                'average_score': 0,
                'improvement_trend': 'Error calculating trend',
                'top_skills': [],
                'areas_to_focus': []
            }