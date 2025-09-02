# Language configuration routes
from flask import Blueprint, request, jsonify
from models.db import db
from models.user import User
from config import Config
from utils.auth import token_required

language_bp = Blueprint('language', __name__)

@language_bp.route('/supported', methods=['GET'])
def get_supported_languages():
    """Get list of supported languages"""
    try:
        languages = []
        for code, info in Config.SUPPORTED_LANGUAGES.items():
            languages.append({
                'code': code,
                'name': info['name'],
                'native_name': info['native_name']
            })
        
        return jsonify({
            'languages': languages,
            'default': Config.DEFAULT_LANGUAGE
        })
    except Exception as e:
        print(f"Error getting supported languages: {e}")
        return jsonify({'error': 'Failed to get supported languages'}), 500

@language_bp.route('/preference', methods=['GET'])
@token_required
def get_user_language_preference(current_user):
    """Get user's language preference"""
    try:
        return jsonify({
            'language': current_user.preferred_language or Config.DEFAULT_LANGUAGE,
            'language_info': Config.SUPPORTED_LANGUAGES.get(
                current_user.preferred_language or Config.DEFAULT_LANGUAGE
            )
        })
    except Exception as e:
        print(f"Error getting user language preference: {e}")
        return jsonify({'error': 'Failed to get language preference'}), 500

@language_bp.route('/preference', methods=['POST'])
@token_required
def set_user_language_preference(current_user):
    """Set user's language preference"""
    try:
        data = request.get_json()
        if not data or 'language' not in data:
            return jsonify({'error': 'Language code is required'}), 400
        
        language_code = data['language']
        
        # Validate language code
        if language_code not in Config.SUPPORTED_LANGUAGES:
            return jsonify({'error': 'Unsupported language'}), 400
        
        # Update user's language preference
        current_user.preferred_language = language_code
        db.session.commit()
        
        return jsonify({
            'message': 'Language preference updated successfully',
            'language': language_code,
            'language_info': Config.SUPPORTED_LANGUAGES[language_code]
        })
        
    except Exception as e:
        print(f"Error setting user language preference: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update language preference'}), 500
