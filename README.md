/
├── src/
│   ├── main.py        # Hybrid Entry Point (CLI & Streamlit)
│   ├── pipeline.py    # Core Logic (Gemini API & Pydantic Schema)
│   └── eval.py        # Evaluation & Validation Logic
├── .env               # Environment variables (API Key)
└── README.md          # Documentation

## 4. Usage

### Prerequisites
* Python 3.9+
* Google AI Studio API Key (Gemini)

### Configuration
Create a `.env` file in the root directory:
```ini
GOOGLE_API_KEY=your_api_key_here
