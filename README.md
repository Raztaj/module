# Family Data Orchestrator (FDO) - Project "Fast-Entry"

The Family Data Orchestrator is a robust system designed to ingest unstructured Arabic messages (from WhatsApp or other text sources), parse them into structured family records, and manage them through a web-based interface. This project is the first module (The Heuristic Parser) of a larger system intended for automated data entry.

## 🌟 Features

- **Heuristic Arabic Parser:** Intelligently splits multi-person messages and extracts names, IDs, phones, and dates using advanced regex and positional logic.
- **Multi-Step Normalization:** Standardizes Arabic characters (Hamzas, Ya, Tashkeel) and converts Eastern Arabic numerals to Western digits.
- **Egyptian Phone Filter:** Automatically filters and accepts only Egyptian phone numbers, prioritizing them for the automation layer.
- **Relational Law Validation:** Verifies consistency between primary family members and their children using heuristic naming checks.
- **Web User Interface:**
  - **Entry Portal:** Paste raw text directly into the browser.
  - **Results Management:** View, Edit, and Delete parsed records in real-time.
  - **Historical Dashboard:** Access and manage all previously processed family groups.
- **Excel Export:** Download all structured data into a professional Excel spreadsheet with one click.
- **SQLite Persistence:** Reliable storage of raw messages and processed records with status tracking.

## 🏗️ System Architecture

1.  **Module 1: The Heuristic Parser (Current)**
    - Ingestion layer that transforms unstructured text into clean JSON/SQL.
    - Handles data validation and logical consistency checks.
2.  **The Persistence Layer**
    - SQLite database acting as the "Source of Truth" and state machine.
3.  **Module 2: The Data Injector (Future)**
    - Automation layer using Playwright to inject validated data into web systems.

## 🚀 Detailed Setup Guide (Linux Mint / Ubuntu)

### 1. Prerequisites
Ensure you have Python 3.11 or higher installed:
```bash
python3 --version
```

### 2. Prepare the Environment
It is recommended to use a virtual environment to manage dependencies:
```bash
# Install venv if not present
sudo apt update
sudo apt install python3-venv -y

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Initialize and Run
Launch the Family Data Orchestrator:
```bash
python3 main.py
```

### 5. Access the Web UI
Open your favorite web browser (Firefox/Chrome) and go to:
**`http://localhost:5000`**

- Use the **Dashboard** link to see historical data.
- Use the **New Entry** page to paste and parse new messages.
- Use **Export to Excel** to download your validated records.

## 📂 Project Structure

- `src/parser/`: Core logic for splitting, normalization, and extraction.
- `src/database/`: SQLite connection and CRUD management.
- `src/ui/`: Flask application, routes, and HTML templates.
- `src/utils/`: Helper functions.
- `tests/`: Unit tests for parsing logic.
- `main.py`: The entry point that launches the web server.

## 🧪 Testing

To run the unit tests and verify the parser logic:
```bash
PYTHONPATH=. pytest tests/
```

## 📜 Business Rules (Logical Officer)

1.  **Deduplication:** Records with duplicate IDs are flagged and skipped from automatic insertion.
2.  **Mandatory Fields:** A record is only marked as "Validated" if it contains both a full name and a valid ID.
3.  **Relational Check:** Children are flagged if their names do not contain the first name of the primary family member.
4.  **Egyptian Phone Law:** Only numbers starting with `+20`, `20`, or `01` are accepted.

---
*Developed as a "Master Blueprint" for high-level AI execution.*
