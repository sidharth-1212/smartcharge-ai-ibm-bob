# Contributing to SmartCharge AI

Thank you for your interest in contributing to SmartCharge AI! This document provides guidelines and instructions for contributing to the project.

## 🤝 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop
- Git
- IBM Bob API credentials (for testing AI features)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/smartcharge-ai.git
   cd smartcharge-ai
   ```

2. **Set Up Development Environment**
   ```bash
   # Start infrastructure services
   docker-compose -f docker-compose.dev.yml up -d
   
   # Backend setup
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Frontend setup
   cd ../frontend
   npm install
   ```

3. **Configure Environment Variables**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   # Edit .env files with your credentials
   ```

## 📝 Development Workflow

### Branch Naming Convention

- `feature/` - New features (e.g., `feature/add-battery-optimization`)
- `fix/` - Bug fixes (e.g., `fix/websocket-connection`)
- `docs/` - Documentation updates (e.g., `docs/update-api-guide`)
- `refactor/` - Code refactoring (e.g., `refactor/decision-engine`)
- `test/` - Test additions/updates (e.g., `test/add-integration-tests`)

### Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(backend): add IBM Bob decision caching
fix(frontend): resolve WebSocket reconnection issue
docs(readme): update installation instructions
```

### Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   pytest --cov=app
   
   # Frontend tests
   cd frontend
   npm test
   
   # Linting
   cd backend
   black . && flake8 . && mypy .
   
   cd frontend
   npm run lint
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat(scope): description of changes"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

6. **PR Requirements**
   - Clear description of changes
   - All tests passing
   - Code review approval
   - No merge conflicts
   - Documentation updated

## 🧪 Testing Guidelines

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_decision_engine.py -v

# Run with markers
pytest -m "not slow"
```

### Frontend Testing

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

### Integration Testing

```bash
# Start all services
docker-compose up -d

# Run integration tests
pytest tests/integration/ -v
```

## 📚 Code Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [Flake8](https://flake8.pycqa.org/) for linting
- Use [MyPy](http://mypy-lang.org/) for type checking
- Maximum line length: 100 characters
- Use type hints for all functions

**Example:**
```python
from typing import Dict, Optional

def calculate_cost(
    energy_kwh: float,
    price_per_kwh: float,
    discount: Optional[float] = None
) -> Dict[str, float]:
    """Calculate charging cost with optional discount.
    
    Args:
        energy_kwh: Energy consumed in kilowatt-hours
        price_per_kwh: Price per kilowatt-hour
        discount: Optional discount percentage (0-100)
    
    Returns:
        Dictionary with cost breakdown
    """
    base_cost = energy_kwh * price_per_kwh
    final_cost = base_cost * (1 - (discount or 0) / 100)
    
    return {
        "base_cost": base_cost,
        "final_cost": final_cost,
        "savings": base_cost - final_cost
    }
```

### JavaScript/React (Frontend)

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use [ESLint](https://eslint.org/) for linting
- Use [Prettier](https://prettier.io/) for formatting
- Use functional components with hooks
- Use TypeScript for type safety (if applicable)

**Example:**
```javascript
import { useState, useEffect } from 'react';

/**
 * Custom hook for fetching telemetry data
 * @param {number} interval - Refresh interval in milliseconds
 * @returns {Object} Telemetry data and loading state
 */
export const useTelemetry = (interval = 5000) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/telemetry/latest');
        const json = await response.json();
        setData(json);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, interval);

    return () => clearInterval(intervalId);
  }, [interval]);

  return { data, loading, error };
};
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description:** Clear description of the issue
2. **Steps to Reproduce:** Detailed steps to reproduce the bug
3. **Expected Behavior:** What should happen
4. **Actual Behavior:** What actually happens
5. **Environment:** OS, Python/Node version, Docker version
6. **Logs:** Relevant error messages or logs
7. **Screenshots:** If applicable

**Template:**
```markdown
## Bug Description
[Clear description of the bug]

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [e.g., Windows 11, macOS 13, Ubuntu 22.04]
- Python: [e.g., 3.11.5]
- Node: [e.g., 18.17.0]
- Docker: [e.g., 24.0.5]

## Logs
```
[Paste relevant logs here]
```

## Screenshots
[If applicable]
```

## 💡 Feature Requests

When requesting features, please include:

1. **Problem Statement:** What problem does this solve?
2. **Proposed Solution:** How should it work?
3. **Alternatives:** Other solutions you've considered
4. **Additional Context:** Any other relevant information

## 📖 Documentation

- Update README.md for user-facing changes
- Update API documentation for endpoint changes
- Add inline comments for complex logic
- Update architecture diagrams if needed
- Include examples in documentation

## 🔒 Security

If you discover a security vulnerability, please email security@smartcharge.ai instead of creating a public issue.

## 📄 License

By contributing to SmartCharge AI, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

## 📞 Questions?

- **GitHub Discussions:** For general questions
- **GitHub Issues:** For bug reports and feature requests
- **Email:** dev@smartcharge.ai

---

Thank you for contributing to SmartCharge AI! 🚀