"""
Form 1040 Generator Module
Generates a filled IRS Form 1040 PDF
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
from typing import Dict
import os

class Form1040Generator:
    def __init__(self):
        """Initialize the Form 1040 generator"""
        self.page_width, self.page_height = letter
    
    def generate_form_1040(self, tax_data: Dict, output_path: str) -> str:
        """
        Generate a completed Form 1040 PDF
        
        Args:
            tax_data: Complete tax return data
            output_path: Path to save the PDF
            
        Returns:
            Path to generated PDF
        """
        c = canvas.Canvas(output_path, pagesize=letter)
        
        # Draw the form
        self._draw_header(c)
        self._draw_personal_info(c, tax_data["personal_info"])
        self._draw_filing_status(c, tax_data["personal_info"])
        self._draw_income_section(c, tax_data["income"])
        self._draw_deductions(c, tax_data)
        self._draw_tax_section(c, tax_data["tax_calculation"])
        self._draw_payments_section(c, tax_data["payments"])
        self._draw_refund_section(c, tax_data["refund_or_owed"])
        self._draw_footer(c)
        
        c.save()
        return output_path
    
    def _draw_header(self, c: canvas.Canvas):
        """Draw form header"""
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, 10.5*inch, "Form 1040")
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, 10.2*inch, "U.S. Individual Income Tax Return")
        c.drawString(6*inch, 10.5*inch, "2024")
        
        c.setFont("Helvetica", 8)
        c.drawString(1*inch, 10*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(1*inch, 9.8*inch, "*** PROTOTYPE - FOR DEMONSTRATION PURPOSES ONLY ***")
    
    def _draw_personal_info(self, c: canvas.Canvas, personal_info: Dict):
        """Draw personal information section"""
        y_pos = 9.3*inch
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y_pos, "Personal Information")
        
        c.setFont("Helvetica", 9)
        y_pos -= 0.3*inch
        
        name = personal_info.get("name", "")
        ssn = personal_info.get("ssn", "")
        address = personal_info.get("address", "")
        
        c.drawString(1*inch, y_pos, f"Name: {name}")
        y_pos -= 0.2*inch
        c.drawString(1*inch, y_pos, f"SSN: {ssn}")
        y_pos -= 0.2*inch
        c.drawString(1*inch, y_pos, f"Address: {address}")
    
    def _draw_filing_status(self, c: canvas.Canvas, personal_info: Dict):
        """Draw filing status section"""
        y_pos = 8.4*inch
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y_pos, "Filing Status")
        
        c.setFont("Helvetica", 9)
        y_pos -= 0.3*inch
        
        filing_status = personal_info.get("filing_status", "Single")
        statuses = ["Single", "Married Filing Jointly", "Married Filing Separately", "Head of Household"]
        
        for status in statuses:
            checkbox = "[X]" if status == filing_status else "[ ]"
            c.drawString(1*inch, y_pos, f"{checkbox} {status}")
            y_pos -= 0.2*inch
    
    def _draw_income_section(self, c: canvas.Canvas, income_data: Dict):
        """Draw income section"""
        y_pos = 6.9*inch
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y_pos, "Income")
        c.line(1*inch, y_pos - 0.05*inch, 7.5*inch, y_pos - 0.05*inch)
        
        c.setFont("Helvetica", 9)
        y_pos -= 0.3*inch
        
        # Line 1: Wages
        c.drawString(1*inch, y_pos, f"1. Wages, salaries, tips, etc.")
        c.drawRightString(7*inch, y_pos, f"${income_data['total_wages']:,.2f}")
        
        y_pos -= 0.25*inch
        c.drawString(1*inch, y_pos, f"2. Interest income")
        c.drawRightString(7*inch, y_pos, f"${income_data['total_interest']:,.2f}")
        
        y_pos -= 0.25*inch
        c.drawString(1*inch, y_pos, f"3. Other income (1099-NEC)")
        c.drawRightString(7*inch, y_pos, f"${income_data['total_nonemployee_compensation']:,.2f}")
        
        y_pos -= 0.3*inch
        c.setFont("Helvetica-Bold", 9)
        c.drawString(1*inch, y_pos, f"Total Income")
        c.drawRightString(7*inch, y_pos, f"${income_data['total_income']:,.2f}")
    
    def _draw_deductions(self, c: canvas.Canvas, tax_data: Dict):
        """Draw deductions section"""
        y_pos = 5.5*inch
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y_pos, "Adjusted Gross Income & Deductions")
        c.line(1*inch, y_pos - 0.05*inch, 7.5*inch, y_pos - 0.05*inch)
        
        c.setFont("Helvetica", 9)
        y_pos -= 0.3*inch
        
        c.drawString(1*inch, y_pos, f"Adjusted Gross Income (AGI)")
        c.drawRightString(7*inch, y_pos, f"${tax_data['agi']:,.2f}")
        
        y_pos -= 0.25*inch
        c.drawString(1*inch, y_pos, f"Standard Deduction")
        c.drawRightString(7*inch, y_pos, f"${tax_data['deductions']['standard_deduction']:,.2f}")
        
        y_pos -= 0.3*inch
        c.setFont("Helvetica-Bold", 9)
        c.drawString(1*inch, y_pos, f"Taxable Income")
        c.drawRightString(7*inch, y_pos, f"${tax_data['taxable_income']:,.2f}")
    
    def _draw_tax_section(self, c: canvas.Canvas, tax_calculation: Dict):
        """Draw tax calculation section"""
        y_pos = 4.3*inch
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y_pos, "Tax Calculation")
        c.line(1*inch, y_pos - 0.05*inch, 7.5*inch, y_pos - 0.05*inch)
        
        c.setFont("Helvetica", 9)
        y_pos -= 0.3*inch
        
        c.drawString(1*inch, y_pos, f"Federal Income Tax")
        c.drawRightString(7*inch, y_pos, f"${tax_calculation['total_tax']:,.2f}")
        
        y_pos -= 0.25*inch
        c.drawString(1.2*inch, y_pos, f"(Effective Rate: {tax_calculation['effective_rate']:.2f}%)")
        
        y_pos -= 0.25*inch
        c.drawString(1.2*inch, y_pos, f"(Marginal Rate: {tax_calculation['marginal_rate']:.0f}%)")
    
    def _draw_payments_section(self, c: canvas.Canvas, payments: Dict):
        """Draw payments section"""
        y_pos = 3.3*inch
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y_pos, "Payments & Credits")
        c.line(1*inch, y_pos - 0.05*inch, 7.5*inch, y_pos - 0.05*inch)
        
        c.setFont("Helvetica", 9)
        y_pos -= 0.3*inch
        
        c.drawString(1*inch, y_pos, f"Federal Income Tax Withheld")
        c.drawRightString(7*inch, y_pos, f"${payments['federal_withheld']:,.2f}")
    
    def _draw_refund_section(self, c: canvas.Canvas, refund_data: Dict):
        """Draw refund or amount owed section"""
        y_pos = 2.4*inch
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y_pos, "Result")
        c.line(1*inch, y_pos - 0.05*inch, 7.5*inch, y_pos - 0.05*inch)
        
        y_pos -= 0.35*inch
        
        if refund_data["status"] == "REFUND":
            c.setFillColorRGB(0, 0.5, 0)  # Green
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1*inch, y_pos, f"REFUND AMOUNT: ${refund_data['amount']:,.2f}")
        elif refund_data["status"] == "OWED":
            c.setFillColorRGB(0.8, 0, 0)  # Red
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1*inch, y_pos, f"AMOUNT OWED: ${refund_data['amount']:,.2f}")
        else:
            c.setFillColorRGB(0, 0, 0)  # Black
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1*inch, y_pos, "Tax liability exactly matches withholding")
        
        c.setFillColorRGB(0, 0, 0)  # Reset to black
    
    def _draw_footer(self, c: canvas.Canvas):
        """Draw form footer"""
        y_pos = 1*inch
        
        c.setFont("Helvetica", 8)
        c.drawString(1*inch, y_pos, "This is a prototype form generated by AI Tax Return Agent.")
        y_pos -= 0.15*inch
        c.drawString(1*inch, y_pos, "DO NOT FILE THIS FORM WITH THE IRS.")
        y_pos -= 0.15*inch
        c.drawString(1*inch, y_pos, "For demonstration and educational purposes only.")
    
    def generate_summary_report(self, tax_data: Dict) -> str:
        """
        Generate a text summary of the tax return
        
        Args:
            tax_data: Complete tax return data
            
        Returns:
            Formatted text summary
        """
        summary = []
        summary.append("=" * 60)
        summary.append("TAX RETURN SUMMARY")
        summary.append("=" * 60)
        summary.append("")
        
        # Personal Info
        summary.append("TAXPAYER INFORMATION:")
        personal = tax_data["personal_info"]
        summary.append(f"  Name: {personal.get('name', 'N/A')}")
        summary.append(f"  Filing Status: {personal.get('filing_status', 'N/A')}")
        summary.append("")
        
        # Income
        summary.append("INCOME:")
        income = tax_data["income"]
        summary.append(f"  Wages (W-2): ${income['total_wages']:,.2f}")
        summary.append(f"  Interest Income (1099-INT): ${income['total_interest']:,.2f}")
        summary.append(f"  Other Income (1099-NEC): ${income['total_nonemployee_compensation']:,.2f}")
        summary.append(f"  TOTAL INCOME: ${income['total_income']:,.2f}")
        summary.append("")
        
        # Deductions
        summary.append("DEDUCTIONS:")
        summary.append(f"  Standard Deduction: ${tax_data['deductions']['standard_deduction']:,.2f}")
        summary.append(f"  Taxable Income: ${tax_data['taxable_income']:,.2f}")
        summary.append("")
        
        # Tax
        summary.append("TAX CALCULATION:")
        tax_calc = tax_data["tax_calculation"]
        summary.append(f"  Federal Income Tax: ${tax_calc['total_tax']:,.2f}")
        summary.append(f"  Effective Tax Rate: {tax_calc['effective_rate']:.2f}%")
        summary.append(f"  Marginal Tax Rate: {tax_calc['marginal_rate']:.0f}%")
        summary.append("")
        
        # Payments
        summary.append("PAYMENTS:")
        summary.append(f"  Federal Tax Withheld: ${tax_data['payments']['federal_withheld']:,.2f}")
        summary.append("")
        
        # Refund/Owed
        summary.append("RESULT:")
        refund = tax_data["refund_or_owed"]
        summary.append(f"  {refund['message']}")
        summary.append("")
        summary.append("=" * 60)
        
        return "\n".join(summary)