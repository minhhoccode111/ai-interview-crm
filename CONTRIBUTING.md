# 🤝 Contributing to AI Interview CRM Platform

We love your input! We want to make contributing to the AI Interview CRM Platform as easy and transparent as possible, whether it's:

- 🐛 Reporting a bug
- 🎯 Discussing the current state of the code
- 📝 Submitting a fix
- 🚀 Proposing new features
- 👥 Becoming a maintainer

## 📋 Table of Contents

- [Development Process](#-development-process)
- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Making Changes](#-making-changes)
- [Submitting Changes](#-submitting-changes)
- [Code Style Guidelines](#-code-style-guidelines)
- [Testing Guidelines](#-testing-guidelines)
- [Documentation Guidelines](#-documentation-guidelines)
- [Community](#-community)

---

## 🔄 Development Process

We use GitHub to host code, track issues and feature requests, as well as accept pull requests.

### 🌟 We Use [GitHub Flow](https://guides.github.com/introduction/flow/index.html)

All code changes happen through pull requests. Pull requests are the best way to propose changes to the codebase:

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

---

## 📖 Code of Conduct

### 🌟 Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of:
- Age, body size, disability, ethnicity
- Gender identity and expression
- Level of experience, nationality
- Personal appearance, race, religion
- Sexual identity and orientation

### ✅ Expected Behavior

- 🤝 Be welcoming and inclusive
- 🎯 Focus on what is best for the community
- 💬 Show empathy towards other community members
- 🧠 Be respectful of differing viewpoints and experiences
- 🙏 Accept constructive criticism gracefully

### ❌ Unacceptable Behavior

- 💬 Trolling, insulting/derogatory comments, personal attacks
- 📢 Public or private harassment
- 🔒 Publishing others' private information without permission
- 🚫 Other conduct inappropriate in a professional setting

---

## 🚀 Getting Started

### 📋 Prerequisites

- 🐍 Python 3.8+
- 🔧 Git
- 📝 Code editor (VS Code recommended)
- 🔑 Google Gemini API Key (for AI features)

### ⚡ Setup Development Environment

```bash
# 1️⃣ Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/ai-interview-crm.git
cd ai-interview-crm

# 2️⃣ Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/ai-interview-crm.git

# 3️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4️⃣ Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# 5️⃣ Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 6️⃣ Initialize database
python -c "from models.db import init_db; from app import create_app; init_db(create_app())"

# 7️⃣ Run tests to ensure everything works
python test_platform.py

# 8️⃣ Start development server
python app.py
```

---

## 🛠️ Making Changes

### 🌿 Branch Naming Convention

Use descriptive branch names that indicate the type of change:

```bash
feature/add-voice-recognition      # New features
bugfix/fix-authentication-error   # Bug fixes
docs/update-api-documentation     # Documentation updates
refactor/optimize-ai-engine       # Code refactoring
test/add-unit-tests               # Test additions
```

### 📝 Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
# Format
<type>[optional scope]: <description>

# Examples
feat(auth): add OAuth2 integration
fix(ai-engine): resolve memory leak in question generation
docs(readme): update installation instructions
test(interview): add unit tests for answer evaluation
refactor(database): optimize query performance
```

### 🎯 Types of Changes

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Changes to build process or auxiliary tools

---

## 📤 Submitting Changes

### 🔍 Before Submitting

1. **✅ Run Tests**
   ```bash
   python test_platform.py
   ```

2. **🧹 Code Linting**
   ```bash
   # Python
   flake8 .
   black .
   
   # JavaScript (if applicable)
   eslint static/js/
   ```

3. **📚 Update Documentation**
   - Update README.md if needed
   - Add docstrings to new functions
   - Update API documentation

### 🎯 Pull Request Process

1. **📋 Fill out the PR template completely**
2. **🏷️ Use descriptive titles**
3. **📝 Reference related issues** (`Fixes #123`, `Closes #456`)
4. **🖼️ Include screenshots** for UI changes
5. **📊 Add performance benchmarks** for optimization PRs

### 📋 Pull Request Template

```markdown
## 🎯 Description
Brief description of changes and motivation.

## 🔗 Related Issues
- Fixes #123
- Related to #456

## 🧪 Testing
- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Manual testing completed

## 📋 Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

## 🖼️ Screenshots (if applicable)
Add screenshots for UI changes.
```

---

## 🎨 Code Style Guidelines

### 🐍 Python Style

- **PEP 8**: Follow Python style guide
- **Black**: Use for automatic formatting
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Use where appropriate

```python
def evaluate_answer(question: str, answer: str) -> Dict[str, Any]:
    """Evaluate an interview answer using AI analysis.
    
    Args:
        question: The interview question asked
        answer: The candidate's response
        
    Returns:
        Dictionary containing evaluation results with score and feedback
        
    Raises:
        ValueError: If question or answer is empty
    """
    pass
```

### 📱 JavaScript Style

- **ES6+**: Use modern JavaScript features
- **ESLint**: Follow ESLint configuration
- **JSDoc**: Document functions properly

```javascript
/**
 * Record audio from user's microphone
 * @param {number} maxDuration - Maximum recording duration in seconds
 * @returns {Promise<Blob>} Promise resolving to audio blob
 */
async function recordAudio(maxDuration = 60) {
    // Implementation
}
```

### 🎨 CSS Style

- **BEM Methodology**: Block Element Modifier naming
- **Mobile-first**: Responsive design approach
- **CSS Variables**: Use for theming

```css
/* BEM Example */
.interview-card {
    /* Block */
}

.interview-card__title {
    /* Element */
}

.interview-card--active {
    /* Modifier */
}
```

---

## 🧪 Testing Guidelines

### 🎯 Test Types

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Test response times and resource usage

### 📝 Test Structure

```python
import unittest
from unittest.mock import patch, MagicMock

class TestInterviewEngine(unittest.TestCase):
    """Test cases for the AI interview engine."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.engine = InterviewEngine()
    
    def test_question_generation(self):
        """Test that questions are generated correctly."""
        # Given
        resume_data = {"skills": ["Python", "Flask"]}
        
        # When
        questions = self.engine.generate_questions(resume_data)
        
        # Then
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)
    
    @patch('services.ai_engine.requests.post')
    def test_api_error_handling(self, mock_post):
        """Test API error handling."""
        # Given
        mock_post.side_effect = ConnectionError("API unavailable")
        
        # When & Then
        with self.assertRaises(ServiceUnavailableError):
            self.engine.evaluate_answer("question", "answer")
```

### 🎯 Test Coverage

- Maintain **80%+ test coverage**
- Test both happy path and error cases
- Mock external dependencies (APIs, databases)
- Use descriptive test names

---

## 📚 Documentation Guidelines

### 📖 Types of Documentation

1. **Code Comments**: Explain complex logic
2. **Docstrings**: Document functions and classes
3. **API Documentation**: REST endpoint documentation
4. **User Guides**: How to use features
5. **Architecture Docs**: System design decisions

### ✍️ Writing Style

- **Clear and Concise**: Use simple language
- **Examples**: Provide code examples
- **Structure**: Use headings and bullet points
- **Visual**: Include diagrams where helpful

### 🎯 Documentation Updates

- Update docs with code changes
- Keep README.md current
- Add examples for new features
- Update API documentation

---

## 👥 Community

### 💬 Getting Help

- **🐛 GitHub Issues**: Bug reports and feature requests
- **💬 Discussions**: General questions and ideas
- **📧 Email**: Direct contact for sensitive issues

### 🎯 Ways to Contribute

#### 👨‍💻 Code Contributions
- 🐛 Fix bugs
- ✨ Add new features
- ⚡ Improve performance
- 🧹 Refactor code

#### 📚 Documentation
- 📝 Improve existing docs
- 🎥 Create tutorials
- 🌍 Translate documentation
- 📖 Write blog posts

#### 🧪 Testing
- 🔍 Write test cases
- 🐛 Find and report bugs
- 📊 Performance testing
- 🔒 Security testing

#### 🎨 Design
- 🖼️ UI/UX improvements
- 🎨 Create graphics/icons
- 📱 Mobile optimization
- ♿ Accessibility improvements

### 🏷️ Issue Labels

We use labels to categorize issues:

- `bug` 🐛: Something isn't working
- `enhancement` ✨: New feature or request
- `documentation` 📚: Improvements or additions to documentation
- `good first issue` 🌟: Good for newcomers
- `help wanted` 🙋: Extra attention is needed
- `priority: high` 🔥: High priority
- `priority: low` 📋: Low priority

---

## 🎉 Recognition

### 🌟 Contributors

All contributors will be recognized in:
- 📋 README.md contributors section
- 🏆 GitHub contributors graph
- 🎯 Release notes for significant contributions
- 🌟 Special mentions in documentation

### 🚀 Becoming a Maintainer

Active contributors may be invited to become maintainers. Maintainers:
- 🔍 Review pull requests
- 🏷️ Manage issues and labels
- 🚀 Make releases
- 🎯 Guide project direction

---

## 📞 Questions?

Don't hesitate to ask questions! We're here to help:

- 💬 Open a [GitHub Discussion](https://github.com/yourusername/ai-interview-crm/discussions)
- 🐛 Create an [Issue](https://github.com/yourusername/ai-interview-crm/issues) for bugs
- 📧 Email us at contribute@ai-interview-crm.com

---

## 🙏 Thank You!

Your contributions make this project better for everyone. Whether you're fixing a typo or adding a major feature, every contribution is valued and appreciated.

**Happy Contributing! 🚀**

---

*This contributing guide is inspired by open source best practices and the community-driven development model.*
