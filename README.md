# Vibe Trader

An AI Assistant for Market Analysis & Trade Signal Generation

## Overview

Vibe Trader is an intelligent trading assistant that helps users make informed trading decisions through AI-driven market analysis and automated trade signal generation. The system monitors real-time market data, detects trends, and delivers actionable insights through a conversational UI.

## Team Members

- Anita Boatemaa Dogbatse
- Elijah Obi
- Precious Iweka
- Hong Quan Nguyen

## Key Features

- Real-time market data analysis
- AI-powered trend detection
- Automated trade signal generation
- Conversational user interface
- Personalized trading insights

## Technologies

- **AI Framework**: LangGraph / Haystack / LlamaIndex / Google ADK
- **Language Model**: Gemini 2.0 Flash
- **Market Data**: Alpha Vantage / Yahoo Finance APIs
- **Frontend**: Reflex
- **Backend**: Reflex
- **Database**: Postgres

## Environment Setup

This project uses **Python 3.12.10** and [uv](https://github.com/astral-sh/uv) for dependency management.

### Setting up uv with VS Code

1. **Install Python 3.12.10** (recommended: use pyenv or pyenv-win)

2. **Install uv**
   - macOS/Linux:
     ```sh
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   - Windows:
     ```powershell
     pip install uv
     ```

3a. **Clone the repository**
```
git clone https://github.com/yourusername/vibe-trader.git
```
After cloning the repository, it is necessary to change the directory to the cloned directory before executing step 3b and 4, 
If the .venv folder is created outside the repository folder, there will be an error message like "no pyproject.toml file found" when executing step 5 to install the dependencies.
The above error was encountered using a Windows PC. To change the directory, use: 
- cd "the directory path"
```
For Example: cd C:\Users\ray2g\vibe-trader
```

3b. **Create a virtual environment with uv**
   ```sh
   uv venv
   ```
   This will create a `.venv` folder in your project directory.
   
4. **Activate the virtual environment**
   - macOS/Linux:
     ```sh
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
     
5. **Install dependencies**
   ```sh
   uv sync
   ```
   
6. **Configure VS Code to use the uv virtual environment**
   - Open the Command Palette (`Cmd+Shift+P` on macOS, `Ctrl+Shift+P` on Windows/Linux)
   - Type and select `Python: Select Interpreter`
   - Choose the interpreter from `.venv` (e.g., `.venv/bin/python` or `.venv\Scripts\python.exe`)
   - VS Code will now use the uv-managed environment for running and debugging Python code.


## Project Status

This project is currently in development.

## License

[License information to be added]
