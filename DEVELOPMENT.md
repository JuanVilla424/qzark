# 🛠️ Development Guide

This guide provides step-by-step instructions for setting up and working on the **Qzark** project, a Python-based crontab-like task runner. It covers Poetry, pre-commit hooks, testing, and other development tools.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: Required for running Qzark.
- **Git**: For version control and cloning the repository.
- **Poetry**: For dependency management and virtual environment handling.
- **Node.js**: Required for formatting Markdown files.

---

## 🚀 **Development Setup**

### 1. **Clone the Repository**

```bash
git clone https://github.com/JuanVilla424/qzark.git
cd qzark
```

### 2. **Install Poetry**

Install Poetry using pip:

```bash
pip install poetry
```

### 3. **Update Poetry**

Ensure Poetry is up-to-date:

```bash
poetry self update
```

### 4. **Set Up the Virtual Environment**

Poetry automatically creates and manages a virtual environment. Install dependencies:

```bash
poetry install
```

### 5. **Activate the Virtual Environment**

Activate the virtual environment managed by Poetry:

```bash
poetry shell
```

---

## 🛠️ **Development Tools**

### 1. **Pre-Commit Hooks**

Pre-commit hooks ensure code quality and consistency before commits. Set them up as follows:

1. **Install Pre-Commit**

   Pre-commit is included in the project dependencies. If not installed, run:

   ```bash
   pip install pre-commit
   ```

2. **Install Hooks**

   Install the pre-commit hooks defined in `.pre-commit-config.yaml`:

   ```bash
   pre-commit install
   pre-commit install -t pre-push
   ```

3. **Run Hooks on All Files**

   To run the hooks on all files in the repository:

   ```bash
   pre-commit run --all-files
   ```

### 2. **Linting and Formatting**

The project uses the following tools for linting and formatting:

- **Black**: Code formatting.
- **Flake8**: Linting for Python code.
- **isort**: Sorting and organizing imports.

These tools are configured in `pyproject.toml` and `.flake8`.

### 3. **Testing**

Tests are written using **pytest**. To run tests:

```bash
poetry run pytest
```

---

## 🚀 **Development Workflow**

### 1. **Create a Feature Branch**

Always create a new branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

### 2. **Commit Your Changes**

Follow the commit message convention:

```bash
git commit -m "feat(<scope>): your commit message"
```

### 3. **Run Pre-Commit Hooks**

Ensure pre-commit hooks pass before pushing your changes:

```bash
pre-commit run --all-files
```

### 4. **Push Your Changes**

Push your branch to the remote repository:

```bash
git push origin feature/your-feature-name
```

### 5. **Open a Pull Request**

Open a pull request into the `dev` branch for review.

---

## 📦 **Dependency Management**

### 1. **Add a Dependency**

To add a new dependency:

```bash
poetry add <package-name>
```

### 2. **Add a Development Dependency**

To add a development-only dependency:

```bash
poetry add --group dev <package-name>
```

### 3. **Update Dependencies**

To update dependencies:

```bash
poetry update
```

### 4. **Export Requirements**

To export dependencies to `requirements.txt`:

```bash
poetry export -f requirements.txt --output requirements.txt
```

---

## 🧹 **Clean Up**

### 1. **Remove the Virtual Environment**

To remove the virtual environment created by Poetry:

```bash
poetry env remove <python-version>
```

### 2. **Uninstall Pre-Commit Hooks**

To uninstall pre-commit hooks:

```bash
pre-commit uninstall
```

---

## 📜 Code of Conduct

Please adhere to the [Code of Conduct](CODE_OF_CONDUCT.md) when contributing to this project.

---

## 🚀 **Versioning and Pre-Push Hooks**

To ensure versioning-related tasks are handled correctly, the following pre-push hooks are installed:

1. **Versioning Checks**: Ensures commit messages follow the [versioning guidelines](#-versioning-strategy).
2. **Changelog Generation**: Automatically updates `CHANGELOG.md` based on commit messages.

To install pre-push hooks:

```bash
pre-commit install -t pre-push
```

For more details on versioning, refer to the [VERSIONING.md](VERSIONING.md) file.

---

## 📫 Contact

For questions or support, open an issue or contact [r6ty5r296it6tl4eg5m.constant214@passinbox.com](mailto:r6ty5r296it6tl4eg5m.constant214@passinbox.com).

---

## 📜 License

2024 - This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). You are free to use, modify, and distribute this software under the terms of the GPL-3.0 license. For more details, please refer to the [LICENSE](LICENSE) file included in this repository.
