
# ExpensifyMe
### Automate Your Expense Reporting with AI-Powered Receipt Analysis

## Overview

ExpensifyMe is a Flask-based web application designed to streamline the process of expense reporting. Users can upload images of their receipts, and the application will automatically extract key-value pairs, such as items purchased, quantities, and total cost. The extracted data is then made available for download in CSV format, simplifying the task of logging expenses for work or personal use.

The application leverages the power of Microsoft's Azure Form Recognizer, a cognitive service that uses AI to extract structured data from receipts and other documents. This tool is particularly effective at handling various receipt formats, extracting essential details with high accuracy.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Code Structure](#code-structure)
- [Technologies Used](#technologies-used)
- [Future Improvements](#future-improvements)
- [License](#license)

## Features

- **User Authentication:** ExpensifyMe includes a simple user authentication system. Users can register, log in, and log out, ensuring that only authorised users can upload and process receipts.
  
- **Receipt Upload:** Users can upload receipt images in multiple formats including PNG, JPG, JPEG, PDF, and GIF.

- **AI-Powered Data Extraction:** Uploaded receipts are analysed using Azure Form Recognizer, which extracts relevant data such as items purchased, quantities, and total amounts.

- **CSV Download:** Once the data has been extracted, users can download the results in a CSV format, making it easy to import into spreadsheets or other accounting software.

- **Session Management:** Extracted data is stored in the user session, allowing users to download the CSV file without having to re-upload the receipt.

## Installation

To set up and run ExpensifyMe on your local machine, follow these steps:

### Prerequisites

- **Python 3.8 or higher**
- **Flask**
- **SQLite**
- **Microsoft Azure Account** (for using Azure Form Recognizer)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ExpensifyMe.git
cd ExpensifyMe
```

### Step 2: Set Up a Virtual Environment

Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
```

### Step 3: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Step 4: Configure Azure Form Recognizer

Set up an Azure Cognitive Services resource for Form Recognizer. Once your resource is created, obtain the endpoint and API key. Replace the placeholder values in `.env` with your actual Form Recognizer endpoint and API key:

```python
app.config.from_mapping(
    SECRET_KEY='*************************************************',
    DATABASE=os.path.join(app.instance_path, 'ExpensifyMe.sqlite'),
    UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
    ALLOWED_EXTENSIONS={'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'},
    FORM_RECOGNIZER_ENDPOINT=os.getenv('FORM_RECOGNIZER_ENDPOINT'),
    FORM_RECOGNIZER_API_KEY=os.getenv('FORM_RECOGNIZER_API_KEY')
)
```

### Step 5: Initialize the Database

Initialise the SQLite database:

```bash
flask init-db
```

### Step 6: Run the Application

Start the Flask development server:

```bash
flask run
```

The application should now be accessible at `http://127.0.0.1:5000`.

## Usage

1. **Register/Login:** Start by registering for an account or logging in if you already have one.
2. **Upload Receipt:** Navigate to the upload page, select your receipt file, and click 'Upload.'
3. **View Results:** Once the analysis is complete, you'll be presented with the extracted data.
4. **Download CSV:** If the data looks good, you can download it as a CSV file for your records.

## Code Structure

- **`__init__.py`:** Sets up the Flask application, including configurations and initialising the Azure Form Recognizer client.
- **`auth.py`:** Manages user authentication, including registration, login, and logout functionalities.
- **`db.py`:** Handles database interactions, including connecting to SQLite, initialising the database, and closing connections.
- **`routes.py`:** Contains the main routes for uploading files, processing receipts, and returning results.
- **`templates/`:** Contains HTML templates for rendering the UI, utilising Flask's Jinja templating engine.
- **`static/`:** Contains static files like CSS and JavaScript for styling and frontend functionality.
- **`schema.sql`:** SQL script for initialising the SQLite database.

## Technologies Used

- **Flask:** A lightweight WSGI web application framework in Python used for building the web application.
- **SQLite:** A relational database management system used for storing user data.
- **Azure Form Recognizer:** A cloud-based AI service that analyses receipts and extracts key-value pairs.
- **Jinja:** A templating engine for Python, used to render dynamic HTML content.
- **HTML/CSS/JavaScript:** For frontend development and user interface design.

## Future Improvements

### 1. **Multi-File Upload**
   Currently, ExpensifyMe allows users to upload and process a single receipt at a time. A significant enhancement would be to implement multi-file uploads, enabling users to upload multiple receipts simultaneously and receive a combined CSV file.

   **Challenges with Azure:**
   - The Azure Form Recognizer API processes documents one at a time. To implement multi-file processing, the app would need to asynchronously handle multiple API calls and then aggregate the results.

   **Possible Solutions:**
   - Implementing an asynchronous task queue using tools like Celery, paired with Redis or RabbitMQ, could allow the application to handle multiple uploads more efficiently.
   - Modifying the existing upload route to accept multiple files and loop through them, sending each to the Form Recognizer API, and collecting the results for a combined CSV output.

### 2. **Enhanced Data Handling**
   - Improve the accuracy and confidence level of extracted data by fine-tuning the Form Recognizer model with more training data, potentially using a custom model tailored for specific receipt formats.
   
### 3. **User Experience Enhancements**
   - Adding more robust error handling and user feedback during the file upload and processing stages.
   - Introducing a progress bar or notification system that informs the user about the status of their document processing, especially useful if multi-file upload is enabled.

### 4. **Security Enhancements**
   - Implementing more secure authentication methods, such as OAuth, and ensuring sensitive data (like API keys) are stored securely using environment variables.

## License

ExpensifyMe is open-source software. Feel free to use, modify, and distribute it as you see fit.
