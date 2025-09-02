#!/usr/bin/env python3
"""
Test that the import fix works correctly
"""


def test_language_routes_import():
    """Test that language routes can be imported without errors"""
    print("🔧 Testing language routes import...")

    try:
        # Test importing the language routes
        import sys
        import os

        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Mock the required modules that aren't available
        import types

        # Mock flask
        flask_mock = types.ModuleType("flask")
        flask_mock.Blueprint = lambda name, import_name: f"Blueprint({name})"
        flask_mock.request = types.ModuleType("request")
        flask_mock.jsonify = lambda x: f"jsonify({x})"
        sys.modules["flask"] = flask_mock

        # Mock models
        models_mock = types.ModuleType("models")
        models_db_mock = types.ModuleType("models.db")
        models_user_mock = types.ModuleType("models.user")
        models_db_mock.db = "mock_db"
        models_user_mock.User = "mock_user"
        sys.modules["models"] = models_mock
        sys.modules["models.db"] = models_db_mock
        sys.modules["models.user"] = models_user_mock

        # Mock config
        config_mock = types.ModuleType("config")
        config_mock.Config = types.ModuleType("Config")
        config_mock.Config.SUPPORTED_LANGUAGES = {
            "en": {
                "name": "English",
                "native_name": "English",
                "whisper_code": "en",
                "tfidf_stopwords": "english",
            },
            "vi": {
                "name": "Vietnamese",
                "native_name": "Tiếng Việt",
                "whisper_code": "vi",
                "tfidf_stopwords": None,
            },
        }
        config_mock.Config.DEFAULT_LANGUAGE = "en"
        sys.modules["config"] = config_mock

        # Mock routes.auth
        routes_mock = types.ModuleType("routes")
        routes_auth_mock = types.ModuleType("routes.auth")
        routes_auth_mock.token_required = lambda f: f  # Simple decorator mock
        sys.modules["routes"] = routes_mock
        sys.modules["routes.auth"] = routes_auth_mock

        # Now try to import the language routes
        from routes.language import language_bp

        print("✅ Language routes imported successfully!")
        print(f"📝 Blueprint created: {language_bp}")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_config_structure():
    """Test the configuration structure"""
    print("🔧 Testing configuration structure...")

    # Test the language configuration from config.py
    try:
        # Read the config file content
        with open("config.py", "r") as f:
            config_content = f.read()

        # Check for key elements
        checks = [
            ("SUPPORTED_LANGUAGES", "SUPPORTED_LANGUAGES" in config_content),
            (
                "Vietnamese config",
                '"vi"' in config_content and "Tiếng Việt" in config_content,
            ),
            (
                "English config",
                '"en"' in config_content and '"English"' in config_content,
            ),
            ("Whisper codes", "whisper_code" in config_content),
            ("Default language", "DEFAULT_LANGUAGE" in config_content),
        ]

        all_passed = True
        for check_name, result in checks:
            if result:
                print(f"✅ {check_name}: PASSED")
            else:
                print(f"❌ {check_name}: FAILED")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False


def main():
    """Run all tests"""
    print("🔧 AI Interview CRM - Import Fix Test")
    print("=" * 45)

    test1_result = test_config_structure()
    print()

    test2_result = test_language_routes_import()
    print()

    if test1_result and test2_result:
        print("🎉 All tests passed!")
        print("\n📋 Summary:")
        print("✅ Configuration structure: PASSED")
        print("✅ Language routes import: PASSED")
        print("\n🚀 The import fix is working correctly!")
        print("\n📝 To run the application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run: python3 app.py")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
