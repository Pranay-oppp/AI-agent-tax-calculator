"""
Main Application - AI Tax Return Agent (Flask Version)
"""

from flask import Flask, render_template, request, jsonify, send_file, session
import os
import tempfile
from datetime import datetime
from werkzeug.utils import secure_filename
import secrets

from document_parser import DocumentParser
from tax_calculator import TaxCalculator
from form_generator import Form1040Generator

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Initialize components
parser = DocumentParser()
calculator = TaxCalculator()
form_generator = Form1040Generator()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_documents():
    """Handle document upload and parsing"""
    try:
        # Get form data
        name = request.form.get('name')
        ssn = request.form.get('ssn')
        address = request.form.get('address')
        filing_status = request.form.get('filing_status')
        
        # Validate personal information
        if not all([name, ssn, address, filing_status]):
            return jsonify({
                'success': False,
                'error': 'Please fill in all personal information fields.'
            })
        
        # Check if files were uploaded
        if 'files[]' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files uploaded.'
            })
        
        files = request.files.getlist('files[]')
        
        if not files or files[0].filename == '':
            return jsonify({
                'success': False,
                'error': 'No files selected.'
            })
        
        # Process each file
        parsed_documents = []
        results = []
        
        for idx, file in enumerate(files, 1):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Parse the document
                parsed_data = parser.parse_document(filepath)
                
                if "error" in parsed_data:
                    results.append({
                        'filename': filename,
                        'status': 'error',
                        'message': parsed_data['error']
                    })
                else:
                    parsed_documents.append(parsed_data)
                    
                    doc_type = parsed_data.get("document_type", "Unknown")
                    doc_info = {'filename': filename, 'type': doc_type, 'status': 'success'}
                    
                    if doc_type == "W-2":
                        doc_info['data'] = {
                            'employer': parsed_data.get('employer_name', 'N/A'),
                            'employee': parsed_data.get('employee_name', 'N/A'),
                            'wages': f"${parsed_data.get('wages', 0):,.2f}",
                            'federal_withheld': f"${parsed_data.get('federal_tax_withheld', 0):,.2f}",
                            'social_security_wages': f"${parsed_data.get('social_security_wages', 0):,.2f}",
                            'medicare_wages': f"${parsed_data.get('medicare_wages', 0):,.2f}"
                        }
                    elif doc_type == "1099-INT":
                        doc_info['data'] = {
                            'payer': parsed_data.get('payer_name', 'N/A'),
                            'recipient': parsed_data.get('recipient_name', 'N/A'),
                            'interest': f"${parsed_data.get('interest_income', 0):,.2f}",
                            'early_withdrawal_penalty': f"${parsed_data.get('early_withdrawal_penalty', 0):,.2f}"
                        }
                    elif doc_type == "1099-NEC":
                        doc_info['data'] = {
                            'payer': parsed_data.get('payer_name', 'N/A'),
                            'recipient': parsed_data.get('recipient_name', 'N/A'),
                            'compensation': f"${parsed_data.get('nonemployee_compensation', 0):,.2f}"
                        }
                    
                    results.append(doc_info)
                
                # Clean up uploaded file
                os.remove(filepath)
        
        if not parsed_documents:
            return jsonify({
                'success': False,
                'error': 'No documents were successfully parsed.',
                'results': results
            })
        
        # Store parsed documents in session
        session['parsed_documents'] = parsed_documents
        session['personal_info'] = {
            'name': name,
            'ssn': ssn,
            'address': address,
            'filing_status': filing_status
        }
        
        return jsonify({
            'success': True,
            'message': f'Successfully parsed {len(parsed_documents)} document(s)',
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing documents: {str(e)}'
        })

@app.route('/calculate', methods=['POST'])
def calculate_tax():
    """Calculate tax return"""
    try:
        # Get parsed documents from session
        parsed_documents = session.get('parsed_documents')
        personal_info = session.get('personal_info')
        
        if not parsed_documents or not personal_info:
            return jsonify({
                'success': False,
                'error': 'Please upload and process documents first.'
            })
        
        # Calculate tax return
        tax_data = calculator.calculate_complete_return(
            parsed_documents,
            personal_info
        )
        
        # Generate summary
        summary = form_generator.generate_summary_report(tax_data)
        
        # Generate Form 1040 PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"Form_1040_{timestamp}.pdf"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        
        form_generator.generate_form_1040(tax_data, pdf_path)
        
        # Store PDF path in session
        session['pdf_path'] = pdf_path
        session['pdf_filename'] = pdf_filename
        
        return jsonify({
            'success': True,
            'summary': summary,
            'tax_data': {
                'total_income': f"${tax_data['income']['total_income']:,.2f}",
                'agi': f"${tax_data['agi']:,.2f}",
                'taxable_income': f"${tax_data['taxable_income']:,.2f}",
                'total_tax': f"${tax_data['tax_calculation']['total_tax']:,.2f}",
                'federal_withheld': f"${tax_data['payments']['federal_withheld']:,.2f}",
                'refund_status': tax_data['refund_or_owed']['status'],
                'refund_amount': f"${tax_data['refund_or_owed']['amount']:,.2f}",
                'effective_rate': f"{tax_data['tax_calculation']['effective_rate']:.2f}%"
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error calculating return: {str(e)}'
        })

@app.route('/download')
def download_form():
    """Download the generated Form 1040"""
    try:
        pdf_path = session.get('pdf_path')
        pdf_filename = session.get('pdf_filename')
        
        if not pdf_path or not os.path.exists(pdf_path):
            return "Form not found. Please calculate your return first.", 404
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=pdf_filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return f"Error downloading form: {str(e)}", 500

@app.route('/reset', methods=['POST'])
def reset():
    """Reset the session"""
    session.clear()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)


