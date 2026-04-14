# Python Projects for CV — AT&S Digital & AI Enablement Role

A collection of Python projects demonstrating data processing, automation,
AI integration, and visualization skills.

---

## 📁 Project Structure

```
Python projects for CV/
│
├── 1_csv_cleaner/
│   └── clean_csv.py           # CSV cleaning pipeline + Excel/PDF report
│
├── 2_file_organizer/
│   └── file_organizer.py      # Automated folder organizer with live monitoring
│
├── 3_pdf_qa_tool/
│   └── pdf_qa_app.py          # AI-powered PDF Q&A chatbot (Streamlit)
│
├── 4_dashboard/
│   └── dashboard_app.py       # Interactive engineering data dashboard (Streamlit)
│
├── 5_training_generator/
│   └── training_generator.py  # AI training material generator → PowerPoint
│
├── requirements.txt            # All dependencies
└── README.md
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your API key (for Projects 3 and 5)
Create a `.env` file in the root folder:
```
ANTHROPIC_API_KEY=your_api_key_here
```
Get a free API key at: https://console.anthropic.com

---

## 🚀 How to Run Each Project

### Project 1 — CSV Data Cleaner
```bash
cd 1_csv_cleaner
python clean_csv.py --input your_data.csv --output cleaned_output
```
Outputs: `cleaned_output.xlsx` + `cleaned_output_summary.pdf`

---

### Project 2 — File & Folder Organizer Bot
```bash
cd 2_file_organizer

# Watch a folder for new files:
python file_organizer.py --watch "C:/Users/YourName/Downloads"

# Organize existing files AND watch for new ones:
python file_organizer.py --watch "C:/Users/YourName/Downloads" --existing
```

---

### Project 3 — AI PDF Q&A Tool
```bash
cd 3_pdf_qa_tool
streamlit run pdf_qa_app.py
```
Then open http://localhost:8501 in your browser.

---

### Project 4 — Engineering Data Dashboard
```bash
cd 4_dashboard
streamlit run dashboard_app.py
```
Then open http://localhost:8501 — works with sample data out of the box.

---

### Project 5 — AI Training Material Generator

**CLI mode:**
```bash
cd 5_training_generator
python training_generator.py --topic "Python for Data Analysis" --output my_training.pptx
```

**Web UI mode:**
```bash
streamlit run training_generator.py
```

---

## 🛠️ Tech Stack

| Technology | Used in |
|---|---|
| Python 3.10+ | All projects |
| pandas | Projects 1, 4 |
| openpyxl | Projects 1, 4 |
| reportlab | Project 1 |
| watchdog | Project 2 |
| streamlit | Projects 3, 4, 5 |
| PyPDF2 | Project 3 |
| anthropic (Claude API) | Projects 3, 5 |
| plotly | Project 4 |
| python-pptx | Project 5 |
| python-dotenv | Projects 3, 5 |

---

## 👤 Author
**Ifeanyi Izuegbunam**
- GitHub: [github.com/YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- LinkedIn: [linkedin.com/in/ifeanyi-izuegbunam-042741331](https://linkedin.com/in/ifeanyi-izuegbunam-042741331)
