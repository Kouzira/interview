# Multimodal Receipt Extraction System

## 1. System Overview
This system acts as an end-to-end AI pipeline that automatically extracts structured data (Merchant, Address, Date, Total, Line Items, Tax) from receipt images.

It leverages the **Google Gemini 2.5 Flash** Vision-Language Model to interpret unstructured visual data and convert it into a strictly typed JSON format. The system features a **Hybrid Interface**, allowing the same `main.py` entry point to function as both a Command Line Interface (CLI) for automation and a Streamlit Web UI for interactive demonstration.

## 2. Key Design Decisions & Trade-offs

### Why Vision LLM (API) instead of Traditional CV (OCR)?
* **Decision:** I chose `Google Gemini 2.5 Flash` API over a traditional `OpenCV + Tesseract` pipeline.
* **Reasoning:**
    * **Robustness:** Vision LLMs handle unstructured layouts, varying fonts, and noisy backgrounds (wrinkles, shadows) significantly better than rule-based OCR regex.
    * **Development Speed:** Using a pre-trained multimodal model allows focusing on *system logic* and *evaluation* rather than tuning image thresholding parameters.
    * **JSON Enforcement:** The API's `Structured Output` feature guarantees valid JSON schema mapping to Pydantic models, eliminating parsing errors common in raw LLM text generation.
    * **Inference:** The model can infer the `Category` (e.g., "Food & Beverage", "Electronics") based on the line items, which is impossible with standard OCR.

### Evaluation Strategy (Heuristic Checks)
Since a ground-truth dataset is not available for this live test, I implemented **Logic Consistency Checks** in `eval.py`:
* **Mandatory Fields:** Verifying that critical fields like `Total Amount` and `Merchant Name` exist.
* **Math Check:** Comparing `Sum(Item Prices)` vs `Total Amount`. This acts as a strong proxy for extraction accuracy (allowing a small tolerance for tax/rounding differences).

### Hybrid Architecture (CLI + UI)
* **Decision:** Implemented a "Polyglot Script" where `main.py` detects the runtime environment.
* **Benefit:** Reduces code duplication. The core formatting logic (`generate_receipt_text`) is shared, ensuring that the Terminal output and the Web UI output are identical.

## 3. Project Structure
```text
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
