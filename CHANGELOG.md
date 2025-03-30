# 🚀 v0.2.8 – Auto .env + API Key Check

## ✨ Features

- Automatically copies `.env.example` → `.env` on first run
- Warns if `SCRAPERAPI_KEY` is missing or still a placeholder
- Moves all env setup logic into `if __name__ == "__main__"` for cleaner imports

## 🔧 Improvements

- Prepped for modular package structure and future PyPI support
