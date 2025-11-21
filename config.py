"""
Configuration file for AI Tax Return Agent
Contains tax brackets, deductions, and API settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/mistral-7b-instruct")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# 2024 Tax Brackets (Single Filer)
TAX_BRACKETS_SINGLE = [
    (11600, 0.10),
    (47150, 0.12),
    (100525, 0.22),
    (191950, 0.24),
    (243725, 0.32),
    (609350, 0.35),
    (float('inf'), 0.37)
]

# 2024 Tax Brackets (Married Filing Jointly)
TAX_BRACKETS_MARRIED = [
    (23200, 0.10),
    (94300, 0.12),
    (201050, 0.22),
    (383900, 0.24),
    (487450, 0.32),
    (731200, 0.35),
    (float('inf'), 0.37)
]

# 2024 Tax Brackets (Head of Household)
TAX_BRACKETS_HOH = [
    (16550, 0.10),
    (63100, 0.12),
    (100500, 0.22),
    (191950, 0.24),
    (243700, 0.32),
    (609350, 0.35),
    (float('inf'), 0.37)
]

# Standard Deductions for 2024
STANDARD_DEDUCTIONS = {
    "Single": 14600,
    "Married Filing Jointly": 29200,
    "Married Filing Separately": 14600,
    "Head of Household": 21900
}

# Supported Document Types
SUPPORTED_DOCUMENTS = ["W-2", "1099-INT", "1099-NEC"]

# File Upload Settings
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = ['.pdf']