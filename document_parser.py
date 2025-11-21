"""
Document Parser Module
Extracts tax data from W-2, 1099-INT, and 1099-NEC forms
"""

import pdfplumber
import re
from typing import Dict, Optional
from openai import OpenAI
import config

class DocumentParser:
    def __init__(self):
        """Initialize the document parser with OpenRouter API"""
        self.client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=config.OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": "http://localhost:7860",
                "X-Title": "AI Tax Return Agent"
            }
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return ""
    
    def identify_document_type(self, text: str) -> str:
        """Identify the type of tax document using regex first, then AI as fallback"""
        # Try regex-based identification first
        if re.search(r'Form\s+W-?2', text, re.IGNORECASE):
            return "W-2"
        elif re.search(r'Form\s+1099-?INT', text, re.IGNORECASE):
            return "1099-INT"
        elif re.search(r'Form\s+1099-?NEC', text, re.IGNORECASE):
            return "1099-NEC"
        
        # Fallback to AI if regex doesn't find anything
        prompt = f"""
        Analyze this tax document text and identify if it's a W-2, 1099-INT, or 1099-NEC form.
        Return ONLY the form type (W-2, 1099-INT, or 1099-NEC) with no additional text.
        
        Document text:
        {text[:1000]}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50
            )
            doc_type = response.choices[0].message.content.strip()
            
            # Validate response
            for valid_type in config.SUPPORTED_DOCUMENTS:
                if valid_type in doc_type:
                    return valid_type
            
            return "Unknown"
        except Exception as e:
            print(f"Error identifying document with AI: {str(e)}")
            return "Unknown"
    
    def parse_w2_regex(self, text: str) -> Dict:
        """Parse W-2 form data using regex patterns"""
        data = self._default_w2()
        
        # Clean text: remove line breaks within numbers (e.g., "$6\n,500" -> "$6,500")
        text = re.sub(r'\$(\d+)\s*\n\s*,(\d+)', r'$\1,\2', text)
        
        # Extract employer name
        employer_patterns = [
            r'Employer:\s*([^\n]+)',
            r'Employer Name:\s*([^\n]+)',
            r'(?:c\s+)?Employer[\s\']*s name[^:]*:\s*([^\n]+)'
        ]
        for pattern in employer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['employer_name'] = match.group(1).strip()
                break
        
        # Extract employee name
        employee_patterns = [
            r'Employee:\s*([^\n]+)',
            r'Employee Name:\s*([^\n]+)',
            r'(?:e\s+)?Employee[\s\']*s name[^:]*:\s*([^\n]+)'
        ]
        for pattern in employee_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['employee_name'] = match.group(1).strip()
                break
        
        # Extract wages (Box 1)
        wage_patterns = [
            r'Wages\s*\(?Box\s*1\)?[:\s]*\$?([\d,]+(?:\.\d{2})?)',
            r'Box\s*1[^\$]*\$?([\d,]+(?:\.\d{2})?)',
            r'(?:Wages|wages)[^\$]*\$([\d,]+(?:\.\d{2})?)'
        ]
        for pattern in wage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                wages_str = match.group(1).replace(',', '')
                data['wages'] = float(wages_str)
                break
        
        # Extract federal tax withheld (Box 2)
        fed_tax_patterns = [
            r'Federal\s+Tax\s+Withheld\s*\(?Box\s*2\)?[:\s]*\$?([\d,]+(?:\.\d{2})?)',
            r'Box\s*2[^\$]*\$?([\d,]+(?:\.\d{2})?)',
            r'Federal.*withheld[^\$]*\$([\d,]+(?:\.\d{2})?)'
        ]
        for pattern in fed_tax_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tax_str = match.group(1).replace(',', '')
                data['federal_tax_withheld'] = float(tax_str)
                break
        
        # Extract social security wages (Box 3)
        ss_patterns = [
            r'Social\s+Security\s+Wages\s*\(?Box\s*3\)?[:\s]*\$?([\d,]+(?:\.\d{2})?)',
            r'Box\s*3[^\$]*\$?([\d,]+(?:\.\d{2})?)',
            r'Social\s+Security[^\$]*\$([\d,]+(?:\.\d{2})?)'
        ]
        for pattern in ss_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ss_str = match.group(1).replace(',', '')
                data['social_security_wages'] = float(ss_str)
                break
        
        # Extract medicare wages (Box 5)
        medicare_patterns = [
            r'Medicare\s+Wages\s*\(?Box\s*5\)?[:\s]*\$?([\d,]+(?:\.\d{2})?)',
            r'Box\s*5[^\$]*\$?([\d,]+(?:\.\d{2})?)',
            r'Medicare[^\$]*\$([\d,]+(?:\.\d{2})?)'
        ]
        for pattern in medicare_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                medicare_str = match.group(1).replace(',', '')
                data['medicare_wages'] = float(medicare_str)
                break
        
        return data
    
    def parse_w2(self, text: str) -> Dict:
        """Parse W-2 form data using regex first, then AI as fallback"""
        # Try regex-based extraction first
        data = self.parse_w2_regex(text)
        
        # If we got useful data from regex, return it
        if data['wages'] > 0 or data['employer_name'] != "Not found":
            return data
        
        # Otherwise, try AI extraction
        prompt = f"""
        Extract the following information from this W-2 form. Return ONLY a valid JSON object with these exact keys:
        - wages (Box 1: Wages, tips, other compensation)
        - federal_tax_withheld (Box 2: Federal income tax withheld)
        - social_security_wages (Box 3: Social security wages)
        - medicare_wages (Box 5: Medicare wages and tips)
        - employer_name
        - employee_name
        
        If a value is not found, use 0 for numbers or "Not found" for text.
        
        W-2 Document:
        {text}
        
        Return format example:
        {{"wages": 50000.00, "federal_tax_withheld": 5000.00, "social_security_wages": 50000.00, "medicare_wages": 50000.00, "employer_name": "ABC Corp", "employee_name": "John Doe"}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            # Extract JSON from response
            import json
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return data  # Return regex results as fallback
        except Exception as e:
            print(f"Error parsing W-2 with AI: {str(e)}")
            return data  # Return regex results as fallback
    
    def parse_1099_int_regex(self, text: str) -> Dict:
        """Parse 1099-INT form data using regex patterns"""
        data = self._default_1099_int()
        
        # Clean text: remove line breaks within numbers
        text = re.sub(r'\$(\d+)\s*\n\s*,(\d+)', r'$\1,\2', text)
        
        # Extract payer name
        payer_patterns = [
            r'Payer:\s*([^\n]+)',
            r'Payer Name:\s*([^\n]+)',
            r'PAYER[\s\']*S name[^:]*:\s*([^\n]+)'
        ]
        for pattern in payer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['payer_name'] = match.group(1).strip()
                break
        
        # Extract recipient name
        recipient_patterns = [
            r'Recipient:\s*([^\n]+)',
            r'Recipient Name:\s*([^\n]+)',
            r'RECIPIENT[\s\']*S name[^:]*:\s*([^\n]+)'
        ]
        for pattern in recipient_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['recipient_name'] = match.group(1).strip()
                break
        
        # Extract interest income (Box 1)
        interest_patterns = [
            r'Interest\s+Income\s*\(?Box\s*1\)?[:\s]*\$?([\d,]+(?:\.\d{2})?)',
            r'Box\s*1[^\$]*\$?([\d,]+(?:\.\d{2})?)',
            r'Interest[^\$]*\$([\d,]+(?:\.\d{2})?)'
        ]
        for pattern in interest_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                interest_str = match.group(1).replace(',', '')
                data['interest_income'] = float(interest_str)
                break
        
        # Extract early withdrawal penalty (Box 2)
        penalty_patterns = [
            r'Early\s+Withdrawal\s+Penalty\s*\(?Box\s*2\)?[:\s]*\$?([\d,]+(?:\.\d{2})?)',
            r'Box\s*2[^\$]*\$?([\d,]+(?:\.\d{2})?)',
            r'Penalty[^\$]*\$([\d,]+(?:\.\d{2})?)'
        ]
        for pattern in penalty_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                penalty_str = match.group(1).replace(',', '')
                data['early_withdrawal_penalty'] = float(penalty_str)
                break
        
        return data
    
    def parse_1099_int(self, text: str) -> Dict:
        """Parse 1099-INT form data using regex first, then AI as fallback"""
        # Try regex-based extraction first
        data = self.parse_1099_int_regex(text)
        
        # If we got useful data from regex, return it
        if data['interest_income'] > 0 or data['payer_name'] != "Not found":
            return data
        
        # Otherwise, try AI extraction
        prompt = f"""
        Extract the following information from this 1099-INT form. Return ONLY a valid JSON object with these exact keys:
        - interest_income (Box 1: Interest income)
        - early_withdrawal_penalty (Box 2: Early withdrawal penalty)
        - payer_name
        - recipient_name
        
        If a value is not found, use 0 for numbers or "Not found" for text.
        
        1099-INT Document:
        {text}
        
        Return format example:
        {{"interest_income": 125.50, "early_withdrawal_penalty": 0, "payer_name": "Bank of America", "recipient_name": "Jane Smith"}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            import json
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return data  # Return regex results as fallback
        except Exception as e:
            print(f"Error parsing 1099-INT with AI: {str(e)}")
            return data  # Return regex results as fallback
    
    def parse_1099_nec_regex(self, text: str) -> Dict:
        """Parse 1099-NEC form data using regex patterns"""
        data = self._default_1099_nec()
        
        # Clean text: remove line breaks within numbers
        text = re.sub(r'\$(\d+)\s*\n\s*,(\d+)', r'$\1,\2', text)
        
        # Extract payer name
        payer_patterns = [
            r'Payer:\s*([^\n]+)',
            r'Payer Name:\s*([^\n]+)',
            r'PAYER[\s\']*S name[^:]*:\s*([^\n]+)'
        ]
        for pattern in payer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['payer_name'] = match.group(1).strip()
                break
        
        # Extract recipient name
        recipient_patterns = [
            r'Recipient:\s*([^\n]+)',
            r'Recipient Name:\s*([^\n]+)',
            r'RECIPIENT[\s\']*S name[^:]*:\s*([^\n]+)'
        ]
        for pattern in recipient_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['recipient_name'] = match.group(1).strip()
                break
        
        # Extract nonemployee compensation (Box 1)
        compensation_patterns = [
            r'Nonemployee\s+Compensation\s*\(?Box\s*1\)?[:\s]*\$?([\d,]+(?:\.\d{2})?)',
            r'Box\s*1[^\$]*\$?([\d,]+(?:\.\d{2})?)',
            r'Compensation[^\$]*\$([\d,]+(?:\.\d{2})?)'
        ]
        for pattern in compensation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                comp_str = match.group(1).replace(',', '')
                data['nonemployee_compensation'] = float(comp_str)
                break
        
        return data
    
    def parse_1099_nec(self, text: str) -> Dict:
        """Parse 1099-NEC form data using regex first, then AI as fallback"""
        # Try regex-based extraction first
        data = self.parse_1099_nec_regex(text)
        
        # If we got useful data from regex, return it
        if data['nonemployee_compensation'] > 0 or data['payer_name'] != "Not found":
            return data
        
        # Otherwise, try AI extraction
        prompt = f"""
        Extract the following information from this 1099-NEC form. Return ONLY a valid JSON object with these exact keys:
        - nonemployee_compensation (Box 1: Nonemployee compensation)
        - payer_name
        - recipient_name
        
        If a value is not found, use 0 for numbers or "Not found" for text.
        
        1099-NEC Document:
        {text}
        
        Return format example:
        {{"nonemployee_compensation": 15000.00, "payer_name": "XYZ Services", "recipient_name": "Mike Johnson"}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            import json
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return data  # Return regex results as fallback
        except Exception as e:
            print(f"Error parsing 1099-NEC with AI: {str(e)}")
            return data  # Return regex results as fallback
    
    def parse_document(self, pdf_path: str) -> Dict:
        """Main method to parse any supported tax document"""
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return {"error": "Could not extract text from PDF"}
        
        doc_type = self.identify_document_type(text)
        
        if doc_type == "W-2":
            data = self.parse_w2(text)
            data["document_type"] = "W-2"
        elif doc_type == "1099-INT":
            data = self.parse_1099_int(text)
            data["document_type"] = "1099-INT"
        elif doc_type == "1099-NEC":
            data = self.parse_1099_nec(text)
            data["document_type"] = "1099-NEC"
        else:
            return {"error": f"Unsupported document type: {doc_type}"}
        
        return data
    
    def _default_w2(self) -> Dict:
        """Default W-2 structure"""
        return {
            "wages": 0,
            "federal_tax_withheld": 0,
            "social_security_wages": 0,
            "medicare_wages": 0,
            "employer_name": "Not found",
            "employee_name": "Not found"
        }
    
    def _default_1099_int(self) -> Dict:
        """Default 1099-INT structure"""
        return {
            "interest_income": 0,
            "early_withdrawal_penalty": 0,
            "payer_name": "Not found",
            "recipient_name": "Not found"
        }
    
    def _default_1099_nec(self) -> Dict:
        """Default 1099-NEC structure"""
        return {
            "nonemployee_compensation": 0,
            "payer_name": "Not found",
            "recipient_name": "Not found"
        }