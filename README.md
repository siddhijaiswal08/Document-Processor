# Document Processor# 

This project is an advanced AI pipeline to split, classify, extract, and validate information from mixed-document insurance claim packets.

The pipeline ingests a single, multi-page PDF, and then:
1.  **Splits** it into logical documents (e.g., "Claim Form", "Invoice") using semantic similarity.
2.  **Classifies** each logical document using multimodal AI.
3.  **Extracts** key-value data (like "policy_number" or "invoice_total") from each document.
4.  **Validates** the data using business logic rules (e.g., checking if the invoice total matches the inspection report).

## ⚙️ How to Run

1.  **Set up the Environment:**
    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate it (PowerShell)
    .\venv\Scripts\Activate.ps1
    
    # Activate it (Git Bash / Linux / macOS)
    # source venv/bin/activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit App:**
    ```bash
    streamlit run app.py
    ```

4.  **Upload a PDF**
    * Open the app in your browser (usually `http://localhost:8501`).
    * Upload a sample PDF to see the pipeline in action.

---

### ⚠️ IMPORTANT: ML Model Stubs

This repository provides the *full application scaffold* and pipeline logic, but the core Machine Learning models are **mocked**.

The files `src/pipeline/mod_02_classification.py` and `src/pipeline/mod_03_extraction.py` contain placeholder functions that return fake data.

**To make this project fully functional, you must:**
1.  **Collect & Annotate Data:** Create a dataset of labeled document images (e.g., "invoice", "claim_form") and annotated key-value pairs.
2.  **Fine-Tune Models:** Use a framework like Hugging Face `transformers` to fine-tune multimodal models (like **LayoutLMv3** or **Donut**) on your custom dataset.
3.  **Replace Mocks:** Save your trained models to the `/models` directory and update the functions in Module 2 and Module 3 to load and run inference with your real models.
