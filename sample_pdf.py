from fpdf import FPDF

def create_w2_pdf(filename="sample_w3.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Form W-2 Wage and Tax Statement", ln=True, align="C")
    pdf.cell(200, 10, txt="Employer: Acme Corp", ln=True)
    pdf.cell(200, 10, txt="Employee: John Doe", ln=True)
    pdf.cell(200, 10, txt="Wages (Box 1): $52,000", ln=True)
    pdf.cell(200, 10, txt="Federal Tax Withheld (Box 2): $6,500", ln=True)
    pdf.cell(200, 10, txt="Social Security Wages (Box 3): $52,000", ln=True)
    pdf.cell(200, 10, txt="Medicare Wages (Box 5): $52,000", ln=True)
    pdf.output(filename)

def create_1099_int_pdf(filename="sample_1099_int.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Form 1099-INT Interest Income", ln=True, align="C")
    pdf.cell(200, 10, txt="Payer: First National Bank", ln=True)
    pdf.cell(200, 10, txt="Recipient: Jane Smith", ln=True)
    pdf.cell(200, 10, txt="Interest Income (Box 1): $245.67", ln=True)
    pdf.cell(200, 10, txt="Early Withdrawal Penalty (Box 2): $0", ln=True)
    pdf.output(filename)

def create_1099_nec_pdf(filename="sample_1099_nec.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Form 1099-NEC Nonemployee Compensation", ln=True, align="C")
    pdf.cell(200, 10, txt="Payer: Bright Solutions LLC", ln=True)
    pdf.cell(200, 10, txt="Recipient: Alex Johnson", ln=True)
    pdf.cell(200, 10, txt="Nonemployee Compensation (Box 1): $12,500", ln=True)
    pdf.output(filename)

# Generate all three PDFs
create_w2_pdf()
create_1099_int_pdf()
create_1099_nec_pdf()
print("Generated sample PDFs: sample_w3.pdf, sample_1099_int.pdf, sample_1099_nec.pdf")
