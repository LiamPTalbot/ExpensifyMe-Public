import os
import csv
from io import StringIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, Response, session
from werkzeug.utils import secure_filename
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

# Blueprint for main routes
main = Blueprint('main', __name__)

# Route to render the index page
@main.route('/')
def index():
    return render_template('uploader/index.html')

# Route to render the upload form page
@main.route('/upload')
def upload_form():
    return render_template('uploader/upload.html')

# Route to handle file uploads and processing
@main.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file part exists in the request
        if 'file' not in request.files:
            flash('No file part')
            current_app.logger.info("No file part in the request.")
            return redirect(request.url)

        file = request.files['file']
        # Check if a file has been selected
        if file.filename == '':
            flash('No selected file')
            current_app.logger.info("No file selected.")
            return redirect(request.url)

        # Process the file if it is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            
            # Create upload folder if it does not exist
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            current_app.logger.info(f"File saved at {file_path}")

            try:
                # Analyze the document using Azure Form Recognizer
                with open(file_path, "rb") as f:
                    poller = current_app.document_analysis_client.begin_analyze_document(
                        model_id="prebuilt-receipt",
                        document=f,
                        locale="en-US"
                    )
                    result = poller.result()

                # Log the structure and content of the result object
                current_app.logger.info(f"Result type: {type(result)}")
                current_app.logger.info(f"Result content: {result}")

                # Extract and process data from the result
                extracted_data = {}
                if hasattr(result, 'documents') and result.documents:
                    for document in result.documents:
                        if hasattr(document, 'fields'):
                            for field_name, field in document.fields.items():
                                current_app.logger.info(f"Field name: {field_name}")

                                if hasattr(field, 'value') and hasattr(field, 'confidence'):
                                    field_value = field.value
                                    field_confidence = field.confidence

                                    if field_name == 'Items' and isinstance(field_value, list):
                                        item_list = []
                                        for item in field_value:
                                            item_dict = item.value if hasattr(item, 'value') else {}
                                            item_list.append({
                                                'description': str(item_dict.get('Description', {}).value if hasattr(item_dict.get('Description', {}), 'value') else 'Not Available'),
                                                'quantity': str(item_dict.get('Quantity', {}).value if hasattr(item_dict.get('Quantity', {}), 'value') else 'Not Available'),
                                                'total_price': str(item_dict.get('TotalPrice', {}).value if hasattr(item_dict.get('TotalPrice', {}), 'value') else 'Not Available'),
                                                'confidence': str(item_dict.get('confidence', 'Not Available'))
                                            })
                                        extracted_data['Items'] = item_list
                                    else:
                                        extracted_data[field_name] = {
                                            'value': str(field_value or 'Not Available'),
                                            'confidence': str(field_confidence or 'Not Available')
                                        }

                # Extract summary fields
                for field_name in ['Subtotal', 'TotalTax', 'Tip', 'Total']:
                    field = result.fields.get(field_name, None) if hasattr(result, 'fields') else None
                    if field and hasattr(field, 'value') and hasattr(field, 'confidence'):
                        extracted_data[field_name] = {
                            'value': str(field.value or 'Not Available'),
                            'confidence': str(field.confidence or 'Not Available')
                        }

                current_app.logger.info(f"Extracted data: {extracted_data}")

                # Save extracted data to session and render results page
                session['extracted_data'] = extracted_data
                return render_template('uploader/results.html', extracted_data=extracted_data, image_url=url_for('main.uploaded_file', filename=filename))

            except Exception as e:
                # Handle any errors during processing
                current_app.logger.error(f"An error occurred: {e}")
                flash('An error occurred while processing the file.')
                return redirect(url_for('main.upload_form'))

    # Redirect to upload form if not POST request
    return redirect(url_for('main.upload_form'))

# Route to serve the uploaded file
@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Route to download extracted results as a CSV file
@main.route('/download_results')
def download_results():
    extracted_data = session.get('extracted_data', {})
    
    items = extracted_data.get('Items', [])
    data = []
    
    # Add headers to the CSV data
    data.append(['Date', 'Transaction Type', 'Item', 'Cost'])
    
    # Extract data for CSV
    date = extracted_data.get('TransactionDate', {}).get('value', 'Not Available')
    transaction_type = extracted_data.get('MerchantName', {}).get('value', 'Not Available')
    
    for item in items:
        data.append([
            date,
            transaction_type,
            item['description'],
            item['total_price']
        ])
    
    # Add summary fields to the CSV data
    data.append([])
    data.append(['Subtotal', extracted_data.get('Subtotal', {}).get('value', 'Not Available')])
    data.append(['Tax', extracted_data.get('Tax', {}).get('value', 'Not Available')])
    data.append(['Tip', extracted_data.get('Tip', {}).get('value', 'Not Available')])
    data.append(['Total', extracted_data.get('Total', {}).get('value', 'Not Available')])

    # Convert list to CSV and send as response
    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(data)
    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=results.csv"}
    )

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
