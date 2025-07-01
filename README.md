# Vibe Trader

<div align="center">

![Vibe Trader Logo](https://img.shields.io/badge/Vibe-Trader-blue?style=for-the-badge&logo=trading&logoColor=white)

**An AI-Powered Trading Assistant for Market Analysis & Signal Generation**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/package%20manager-uv-blue)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-green)](https://github.com/features/actions)

</div>

## Overview

Vibe Trader is an intelligent trading assistant that helps users make informed trading decisions through AI-driven market analysis and automated trade signal generation. The system monitors real-time market data, detects trends, and delivers actionable insights through a conversational interface.

## ✨ Key Features

- 🔄 **Real-time Market Data Analysis** - Live data feeds from Alpha Vantage and Yahoo Finance
- 🤖 **AI-Powered Trend Detection** - Advanced pattern recognition using Gemini 2.0 Flash
- 📈 **Automated Trade Signal Generation** - Smart alerts for buy/sell opportunities
- 💬 **Conversational User Interface** - Natural language interactions with the AI assistant
- 📊 **Personalized Trading Insights** - Customized analysis based on user preferences
- 🔗 **Alpaca Integration** - Direct trading execution through Alpaca Markets API
- 📋 **Portfolio Management** - Track positions, orders, and account information
- 📰 **News Integration** - Real-time financial news analysis for informed decisions

## 🏗️ Architecture

```
vibe-trader/
├── vibe_trader_agent/          # Core AI agent module
│   ├── agent.py               # Main AI agent implementation
│   ├── alpaca_tools.py        # Alpaca API integration tools
│   └── __init__.py
└── pyproject.toml             # Project configuration
```

## 🛠️ Technologies

| Component                  | Technology                               |
| -------------------------- | ---------------------------------------- |
| **AI Framework**           | Google ADK (Application Development Kit) |
| **Language Model**         | Gemini                                   |
| **Market Data**            | Alpaca Markets Data API                  |
| **Trading Execution**      | Alpaca Trading API                       |
| **Data Visualization**     | Plotly, Kaleido                          |
| **Environment Management** | uv (Python package manager)              |

## 🚀 Quick Start

### Prerequisites

- Python 3.12.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/vibe-trader.git
   cd vibe-trader
   ```

2. **Create and activate virtual environment**

   ```bash
   # Create virtual environment
   uv venv

   # Activate virtual environment
   # macOS/Linux:
   source .venv/bin/activate

   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**

   ```bash
   uv sync
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Environment Setup

#### macOS

```bash
# Install Python 3.12.10 (recommended: use pyenv)
brew install pyenv
pyenv install 3.12.10
pyenv local 3.12.10

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv sync
```

#### Windows

```powershell
# Install Python 3.12.10 (recommended: use pyenv-win)
# See: https://github.com/pyenv-win/pyenv-win
pyenv install 3.12.10
pyenv local 3.12.10

# Install uv
pip install uv

# Create virtual environment and install dependencies
uv venv
.venv\Scripts\Activate.ps1
uv sync
```

### VS Code Setup

1. **Configure Python interpreter**

   - Open Command Palette (`Cmd+Shift+P` on macOS, `Ctrl+Shift+P` on Windows/Linux)
   - Type and select `Python: Select Interpreter`
   - Choose the interpreter from `.venv` (e.g., `.venv/bin/python` or `.venv\Scripts\python.exe`)

2. **Install recommended extensions**
   - Python
   - Jupyter
   - Pylance

## 📋 API Keys Required

Create a `.env` file in the project root with the following keys:

```env
# Alpaca Trading API
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
ALPACA_PAPER=True  # Set to False for live trading

# Google AI (Gemini)
GOOGLE_API_KEY=your_google_api_key

# Optional: Chart artifacts (for development)
SAVE_CHART_ARTIFACT=True
```

## 🔧 Usage

### Running the AI Agent

```bash
cd vibe-trader
adk web --reload
```

### Available Trading Functions

- **Account Management**: Get account info, buying power, positions
- **Order Management**: Place market orders, cancel orders, view order history
- **Market Data**: Fetch real-time prices, candlestick data, news
- **Portfolio Analysis**: View open positions, P&L analysis
- **Risk Management**: Emergency exit functions, position sizing

## 🧪 Development

### Running Tests

```bash
# Run individual tool tests
cd vibe_trader_agent
python alpaca_tools.py
```

## 👥 Team

- **Anita Boatemaa Dogbatse** - Trading Logic & API Integration
- **Elijah Obi** - AI Agent Development
- **Precious Iweka** - Trading Logic & API Integration
- **Hong Quan Nguyen** - System Architecture

## 📈 Features in Detail

### AI-Powered Analysis

- Natural language processing for market sentiment
- Pattern recognition in price movements
- Risk assessment and position sizing recommendations

### Real-Time Data Integration

- Live market data streaming
- News sentiment analysis
- Economic calendar integration

### Trading Automation

- Algorithmic signal generation
- Automated order placement
- Portfolio rebalancing

### Risk Management

- Stop-loss and take-profit automation
- Position sizing based on risk tolerance
- Emergency exit functions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading financial instruments involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. Please consult with a financial advisor before making any investment decisions.

## 📞 Support

- 📧 Email: quannguyen2281995@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/qng95/vibe-trader/issues)

---

<div align="center">
Made with ❤️ by the Vibe Trader Team
</div>
