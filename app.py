# Main Flask application
from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from models.db import db, init_db
from routes.auth import auth_bp
from routes.interview import interview_bp
from routes.dashboard import dashboard_bp
from routes.language import language_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize config (create directories)
    Config.init_app(app)

    # Enable CORS for all routes
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5000"])

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize database
    init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(interview_bp, url_prefix='/api/interview')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(language_bp, url_prefix='/api/language')

    # Frontend routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/interview')
    def interview():
        return render_template('interview.html')

    @app.route('/report')
    def report():
        return render_template('report.html')

    # API status endpoint
    @app.route('/api/status')
    def api_status():
        return jsonify({
            'status': 'online',
            'message': 'AI Interview CRM API is running',
            'version': '1.0.0'
        })

    # Serve uploaded files
    @app.route('/static/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting AI Interview CRM Platform...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)