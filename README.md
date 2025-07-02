# AI-Powered Interview CRM Platform

## Overview

The AI-Powered Interview CRM is a comprehensive platform that revolutionizes the interview preparation process. It leverages Google's Gemini AI to conduct realistic, voice-to-voice mock interviews, analyze responses, and provide detailed feedback. The system helps candidates improve their interview skills through AI-powered practice sessions and personalized recommendations.

## Key Features

- **Resume Processing**: Accepts both text input and file uploads (PDF)
- **AI Interview Engine**: Conducts voice-to-voice interviews with natural conversation flow
- **Smart Evaluation**: Uses semantic analysis to evaluate answers (not just keyword matching)
- **Comprehensive Reporting**: Generates detailed PDF reports with performance metrics
- **Performance Analytics**: Tracks progress across multiple interviews
- **Personalized Recommendations**: Suggests areas for improvement and career opportunities

## Technology Stack

### Backend
- **Python Flask**: Lightweight and flexible web framework
- **SQLite**: Database for development (easily switchable to PostgreSQL for production)
- **Google Gemini API**: Powers the AI interview and evaluation system
- **OpenAI Whisper**: Handles speech-to-text conversion

### Frontend
- **HTML5/CSS3**: Responsive and accessible interface
- **JavaScript**: Interactive elements and API communication
- **MediaRecorder API**: Browser-based audio recording

### Additional Libraries
- **Transformers**: For semantic analysis of answers
- **FPDF2**: PDF report generation
- **Matplotlib**: Data visualization in reports

## Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Google Gemini API key
- (Optional) FFmpeg for audio processing

### Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-interview-crm.git
cd ai-interview-crm
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=sqlite:///interview.db
```

5. Initialize the database:
```bash
python
>>> from app import create_app
>>> app = create_app()
>>> app.app_context().push()
>>> from models.db import db
>>> db.create_all()
>>> exit()
```

6. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Configuration

The system can be configured via the `config.py` file or environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for session security | Required |
| `SQLALCHEMY_DATABASE_URI` | Database connection string | `sqlite:///interview.db` |
| `UPLOAD_FOLDER` | Path for storing uploaded files | `./static/uploads` |
| `GEMINI_API_KEY` | Google Generative AI API key | Required |
| `MAX_CONTENT_LENGTH` | Maximum upload size (bytes) | 16MB |

## API Documentation

The backend provides a RESTful API with these endpoints:

### Authentication

- `POST /api/auth/register`
  - Register a new user
  - Required fields: `email`, `password`, `full_name`

- `POST /api/auth/login`
  - Authenticate user and get JWT token
  - Required fields: `email`, `password`

### Resume Management

- `POST /api/interview/resume`
  - Submit resume (either file upload or text content)
  - Accepts form data with either `file` or `text`

### Interview Process

- `POST /api/interview/start`
  - Start new interview session
  - Requires `resume_id`

- `POST /api/interview/process`
  - Process interview answer (audio or text)
  - Requires `interview_id`, `question`, and either audio file or `text_answer`

- `POST /api/interview/complete/<int:interview_id>`
  - Finalize interview and generate report

### Dashboard

- `GET /api/dashboard/stats`
  - Get user statistics and interview history

## System Architecture

```
Frontend (Browser)
       ↑↓ HTTPS
Flask Application (Python)
       ↑↓
SQLite Database
       ↑↓
AI Services (Gemini API, Whisper)
       ↑↓
Analytics Engine
```

## Usage Guide

1. **Registration & Login**
   - Create an account or log in if you already have one

2. **Resume Submission**
   - Either upload a PDF resume or paste your resume text
   - The system will parse your skills and experience

3. **Start Interview**
   - Begin a mock interview session
   - Choose between voice or text responses

4. **Interview Process**
   - Answer AI-generated questions
   - Receive immediate feedback after each answer
   - The system adapts questions based on your responses

5. **Review Results**
   - View your performance dashboard
   - Download a detailed PDF report
   - See personalized recommendations

## Customization Options

1. **Question Styles**
   - Modify `services/ai_engine.py` to adjust question generation:
   ```python
   def generate_questions(self, resume_data):
       # Customize the prompt template
       prompt = f"""
       Generate interview questions focusing on:
       - 40% technical questions
       - 30% behavioral questions
       - 20% situational questions
       - 10% general questions
       
       Resume Data: {resume_data}
       """
   ```

2. **Evaluation Criteria**
   - Adjust the evaluation weights in `services/ai_engine.py`:
   ```python
   def evaluate_answer(self, question, answer):
       # Modify scoring logic
       technical_weight = 0.6
       communication_weight = 0.3
       completeness_weight = 0.1
   ```

3. **Report Formatting**
   - Customize the PDF template in `services/analytics.py`

## Deployment

For production deployment, consider:

1. **Web Server**
   - Use Gunicorn with Nginx:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
   ```

2. **Database**
   - Switch to PostgreSQL:
   ```python
   # In config.py
   SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/interview_db'
   ```

3. **Containerization**
   - Dockerize the application:
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   EXPOSE 5000
   CMD ["gunicorn", "-w 4", "-b 0.0.0.0:5000", "app:create_app()"]
   ```

## Troubleshooting

**Common Issues:**

1. **Audio Recording Not Working**
   - Ensure browser has microphone permissions
   - Check that the site is served over HTTPS (required for MediaRecorder in some browsers)

2. **Gemini API Errors**
   - Verify your API key is correct
   - Check Google Cloud quota limits

3. **Database Issues**
   - Ensure the `instance` folder has write permissions
   - For production, use a more robust database like PostgreSQL

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For support or inquiries, please contact:
- Project Maintainer: [Your Name]
- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)

---