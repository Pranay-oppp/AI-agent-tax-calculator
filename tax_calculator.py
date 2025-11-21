"""
Tax Calculator Module
Calculates federal tax liability based on income and filing status
"""

import config
from typing import Dict, List, Tuple

class TaxCalculator:
    def __init__(self):
        """Initialize the tax calculator"""
        self.tax_brackets = {
            "Single": config.TAX_BRACKETS_SINGLE,
            "Married Filing Jointly": config.TAX_BRACKETS_MARRIED,
            "Married Filing Separately": config.TAX_BRACKETS_SINGLE,
            "Head of Household": config.TAX_BRACKETS_HOH
        }
    
    def calculate_tax(self, taxable_income: float, filing_status: str) -> Dict:
        """
        Calculate federal income tax using progressive tax brackets
        
        Args:
            taxable_income: Income after deductions
            filing_status: Tax filing status
            
        Returns:
            Dictionary with tax calculation details
        """
        if taxable_income <= 0:
            return {
                "taxable_income": 0,
                "total_tax": 0,
                "effective_rate": 0,
                "marginal_rate": 0,
                "bracket_details": []
            }
        
        brackets = self.tax_brackets.get(filing_status, config.TAX_BRACKETS_SINGLE)
        
        total_tax = 0
        remaining_income = taxable_income
        previous_limit = 0
        bracket_details = []
        marginal_rate = 0
        
        for limit, rate in brackets:
            if remaining_income <= 0:
                break
            
            # Calculate income in this bracket
            bracket_income = min(remaining_income, limit - previous_limit)
            bracket_tax = bracket_income * rate
            total_tax += bracket_tax
            marginal_rate = rate
            
            bracket_details.append({
                "range": f"${previous_limit:,.2f} - ${limit:,.2f}" if limit != float('inf') else f"${previous_limit:,.2f}+",
                "rate": f"{rate * 100:.0f}%",
                "income_in_bracket": bracket_income,
                "tax_in_bracket": bracket_tax
            })
            
            remaining_income -= bracket_income
            previous_limit = limit
        
        effective_rate = (total_tax / taxable_income * 100) if taxable_income > 0 else 0
        
        return {
            "taxable_income": taxable_income,
            "total_tax": round(total_tax, 2),
            "effective_rate": round(effective_rate, 2),
            "marginal_rate": marginal_rate * 100,
            "bracket_details": bracket_details
        }
    
    def aggregate_income(self, documents: List[Dict]) -> Dict:
        """
        Aggregate income from all tax documents
        
        Args:
            documents: List of parsed tax documents
            
        Returns:
            Dictionary with aggregated income data
        """
        total_wages = 0
        total_interest = 0
        total_nonemployee_comp = 0
        total_federal_withheld = 0
        
        w2_count = 0
        int_count = 0
        nec_count = 0
        
        for doc in documents:
            if doc.get("document_type") == "W-2":
                total_wages += doc.get("wages", 0)
                total_federal_withheld += doc.get("federal_tax_withheld", 0)
                w2_count += 1
            
            elif doc.get("document_type") == "1099-INT":
                total_interest += doc.get("interest_income", 0)
                int_count += 1
            
            elif doc.get("document_type") == "1099-NEC":
                total_nonemployee_comp += doc.get("nonemployee_compensation", 0)
                nec_count += 1
        
        total_income = total_wages + total_interest + total_nonemployee_comp
        
        return {
            "total_income": round(total_income, 2),
            "total_wages": round(total_wages, 2),
            "total_interest": round(total_interest, 2),
            "total_nonemployee_compensation": round(total_nonemployee_comp, 2),
            "total_federal_withheld": round(total_federal_withheld, 2),
            "document_counts": {
                "W-2": w2_count,
                "1099-INT": int_count,
                "1099-NEC": nec_count
            }
        }
    
    def calculate_refund_or_owed(self, tax_liability: float, federal_withheld: float) -> Dict:
        """
        Calculate refund or amount owed
        
        Args:
            tax_liability: Total calculated tax
            federal_withheld: Total federal tax withheld
            
        Returns:
            Dictionary with refund/owed information
        """
        difference = federal_withheld - tax_liability
        
        if difference > 0:
            return {
                "status": "REFUND",
                "amount": round(difference, 2),
                "message": f"You are due a refund of ${difference:,.2f}"
            }
        elif difference < 0:
            return {
                "status": "OWED",
                "amount": round(abs(difference), 2),
                "message": f"You owe ${abs(difference):,.2f}"
            }
        else:
            return {
                "status": "EVEN",
                "amount": 0,
                "message": "Your withholding exactly matches your tax liability"
            }
    
    def calculate_complete_return(self, documents: List[Dict], personal_info: Dict) -> Dict:
        """
        Calculate complete tax return
        
        Args:
            documents: List of parsed tax documents
            personal_info: Dictionary with filing status, dependents, etc.
            
        Returns:
            Complete tax return calculation
        """
        # Aggregate all income
        income_data = self.aggregate_income(documents)
        
        # Get standard deduction
        filing_status = personal_info.get("filing_status", "Single")
        standard_deduction = config.STANDARD_DEDUCTIONS.get(filing_status, 14600)
        
        # Calculate AGI (simplified - just total income for this prototype)
        agi = income_data["total_income"]
        
        # Calculate taxable income
        taxable_income = max(0, agi - standard_deduction)
        
        # Calculate tax
        tax_calculation = self.calculate_tax(taxable_income, filing_status)
        
        # Calculate refund or owed
        refund_data = self.calculate_refund_or_owed(
            tax_calculation["total_tax"],
            income_data["total_federal_withheld"]
        )
        
        return {
            "personal_info": personal_info,
            "income": income_data,
            "deductions": {
                "standard_deduction": standard_deduction,
                "itemized_deduction": 0  # Not implemented in prototype
            },
            "agi": round(agi, 2),
            "taxable_income": round(taxable_income, 2),
            "tax_calculation": tax_calculation,
            "payments": {
                "federal_withheld": income_data["total_federal_withheld"]
            },
            "refund_or_owed": refund_data
        }