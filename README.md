# AI Tax Return Agent - Prototype

An end-to-end AI-powered prototype for automating personal tax return preparation.

## ⚠️ DISCLAIMER
**This is a prototype for educational purposes only. DO NOT use for actual tax filing.**

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file:
```env
# OPENROUTER_API_KEY=your_api_key_here
# MODEL_NAME=mistralai/mistral-7b-instruct
```

# Get your API key from: https://openrouter.ai/

### 3. Run the Application
```bash
python app.py
```

Open your browser to: `http://localhost:7860`

## 📋 Features

- PDF document upload (W-2, 1099-INT, 1099-NEC)
- AI-powered data extraction using Mistral
- 2024 IRS tax calculations
- Form 1040 PDF generation
- Clean Gradio web interface

## 🛠️ Project Structure
```
tax-return-agent/
├── app.py                  # Main application
├── config.py              # Configuration
├── document_parser.py     # PDF parsing
├── tax_calculator.py      # Tax calculations
├── form_generator.py      # PDF generation
├── requirements.txt       # Dependencies
├── .env                   # Your API key (create this)
└── README.md             # This file
```

## 📖 How to Use

1. Enter personal information
2. Upload tax document PDFs
3. Click "Process Documents"
4. Review parsed data
5. Click "Calculate Tax Return"
6. Download Form 1040 PDF

## 🔐 Security Note

This prototype is for educational purposes only. Production systems require:
- Encryption
- Authentication
- Secure storage
- IRS compliance
- Professional tax validation

## 📝 License

Educational prototype only. No warranty provided.
