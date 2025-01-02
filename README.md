# ⌛ Qzark

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![Build Status](https://github.com/JuanVilla424/qzark/actions/workflows/ci.yml/badge.svg?branch=main)
![Status](https://img.shields.io/badge/Status-Development-blue.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

Welcome to **Qzark**, a lightweight, Python-based crontab-like task runner designed to manage and execute scheduled
tasks without relying on external cron services. Qzark reads tasks from a YAML configuration file, schedules them
internally, and sends notifications on task failures via Telegram, Discord, or SMTP.

## 📚 Table of Contents

- [Features](#-features)
- [Getting Started](#-getting-started)
  - [Prerequisites](#-prerequisites)
  - [Installation](#-installation)
  - [Configuration](#-configuration)
- [Usage](#-usage)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

## 🌟 Features

- **Task Scheduling:** Schedule tasks internally without relying on external cron services.
- **YAML Configuration:** Define tasks in a simple `tasks.yaml` file.
- **Notifications:** Receive alerts on task failures via Telegram, Discord, or SMTP.
- **Queue-Based Execution:** Tasks are managed using a queue-based mechanism for efficient execution.
- **Customizable Timeout:** Set task execution timeouts via command-line arguments.

## 🚀 Getting Started

### 📋 Prerequisites

**Before you begin, ensure you have met the following requirements**:

- **Python 3.11+:** Ensure Python is installed on your local machine.
- **Git:** Install [Git](https://git-scm.com/) to clone the repository.

### 🔨 Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/JuanVilla424/qzark.git
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd qzark
   ```

3. **Set Up a Python Virtual Environment**

   ```bash
   python -m venv venv
   ```

4. **Activate the Virtual Environment**

   On Unix or MacOS:

   ```bash
   source venv/bin/activate
   ```

   On Windows:

   ```bash
   .\venv\Scripts\activate
   ```

5. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### 🔧 Configuration

1. **Define Tasks in `tasks.yaml`**

   Create a `tasks.yaml` file in the root directory with the following structure:

   ```yaml
   tasks:
     - name: "Example Task"
       interval_seconds: 60
       shell_command: "echo 'Hello, Qzark!'"
   ```

2. **Configure Notifications in `config.py`**

   Update `config.py` with your notification settings (e.g., Telegram bot token, Discord webhook URL, SMTP credentials).

## 🛠️ Usage

1. **Run Qzark**

   ```bash
   python qzark.py
   ```

2. **Command-Line Arguments**

   - `--timeout`: Set task execution timeout (default: 50 seconds).
   - `--log-level`: Set logging level (`INFO` or `DEBUG`).

   Example:

   ```bash
   python qzark.py --timeout 100 --log-level DEBUG
   ```

3. **Stopping Qzark**

   Press `Ctrl+C` to stop the application gracefully.

## 🤝 Contributing

**Contributions are welcome! To contribute to this repository, please follow these steps**:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "feat(<scope>): your feature commit message - lower case"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request into** `dev` **branch**

Please ensure your contributions adhere to the Code of Conduct and Contribution Guidelines.

### 🛠️ Adding a New Workflow

1. **Create a New Workflow File**

   ```bash
   touch .github/workflows/new-workflow.yml
   ```

2. **Define the Workflow**

   Customize the workflow according to your needs, using existing workflows as references.

3. **Commit and Push**
   ```bash
   git add .github/workflows/new-workflow.yml
   git commit -m "chore(core): added new workflow - lower case"
   git push origin feature/your-feature-name
   ```

## 📫 Contact

For any inquiries or support, please open an issue or contact [r6ty5r296it6tl4eg5m.constant214@passinbox.com](mailto:r6ty5r296it6tl4eg5m.constant214@passinbox.com).

---

## 📜 License

2025 - This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). You are free to use, modify, and distribute this software under the terms of the GPL-3.0 license. For more details, please refer to the [LICENSE](LICENSE) file included in this repository.
