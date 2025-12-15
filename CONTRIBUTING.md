# Contributing to Visual Debugger

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the Visual Debugger project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Install dependencies (see [README.md](./README.md))
4. Create a feature branch: `git checkout -b feature/your-feature`

## Development Workflow

### Frontend Development
```bash
npm run dev
```
Starts the Next.js development server with hot reload at `http://localhost:3000`

### Backend Development
```bash
cd backend
python app.py
```
Starts the Flask server at `http://localhost:5000`

## Code Style

### TypeScript/React
- Use 2-space indentation
- Follow existing naming conventions
- Use TypeScript for type safety
- Keep components focused and reusable

### Python
- Use 4-space indentation
- Follow PEP 8 style guidelines
- Add docstrings to functions
- Use type hints where applicable

## Making Changes

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/descriptive-name
   ```

2. **Make your changes** with clear, focused commits:
   ```bash
   git commit -m "feat: add specific feature description"
   ```

3. **Test your changes**:
   - Run the development servers
   - Test the feature manually
   - Check for console errors

4. **Push to your fork**:
   ```bash
   git push origin feature/descriptive-name
   ```

5. **Create a Pull Request** with a clear description

## Pull Request Process

- Describe what problem your PR solves
- Include relevant screenshots for UI changes
- Reference any related issues
- Keep PRs focused on a single feature/fix
- Ensure your code follows the project's style guidelines

## Commit Message Guidelines

Use clear, descriptive commit messages:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring

Example: `feat: add heap visualization component`

## Areas for Contribution

- Bug fixes
- Performance improvements
- New data structure visualizations
- Documentation improvements
- Testing
- Design improvements

## Questions?

Feel free to open an issue to discuss any changes or ask questions before starting work.

---

Thank you for helping make Visual Debugger better!
