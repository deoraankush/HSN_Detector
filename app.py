import os
import openai
import requests
from flask import Flask, render_template, request, Response, send_from_directory
import csv
import io
import json
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)

# Configure the OpenAI API key
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# TODO: Add your ClearTax API key and URL here
CLEARTAX_API_KEY = os.getenv("CLEARTAX_API_KEY")
CLEARTAX_API_URL = os.getenv("CLEARTAX_API_URL")

def get_hsn_from_cleartax(product_name, description, region="International"):
    """
    Fallback function to get HSN code from ClearTax API.
    """
    if not CLEARTAX_API_KEY or not CLEARTAX_API_URL:
        return json.dumps({
            "hsn_code": "N/A",
            "confidence_score": "N/A",
            "explanation": "ClearTax API not configured.",
            "similar_products": []
        })

    headers = {
        "x-api-key": CLEARTAX_API_KEY,
        "Content-Type": "application/json"
    }
    params = {
        "query": description
    }

    try:
        response = requests.get(CLEARTAX_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # TODO: Adapt this mapping based on the actual response from the ClearTax API
        # This is a hypothetical structure
        if data and data.get('results'):
            hsn_code = data['results'][0].get('hsn_code')
            explanation = data['results'][0].get('description')
            return json.dumps({
                "hsn_code": hsn_code,
                "confidence_score": "N/A", # ClearTax might not provide this
                "explanation": f"Provided by ClearTax: {explanation}",
                "similar_products": []
            })
        else:
            return json.dumps({
                "hsn_code": "Not Found",
                "confidence_score": "N/A",
                "explanation": "No HSN code found by ClearTax for the given description.",
                "similar_products": []
            })
    except requests.exceptions.RequestException as e:
        print(f"ClearTax API request failed: {e}")
        return json.dumps({
            "hsn_code": "Error",
            "confidence_score": "N/A",
            "explanation": f"ClearTax API request failed: {e}",
            "similar_products": []
        })

def get_hsn_prediction(product_name, description, region="International"):
    region_specific_instruction = (
        "Provide the 8-digit HSN code applicable in India."
        if region == "India"
        else "Provide the internationally recognized 6-digit HSN code."
    )

    prompt = f"""
    You are an expert in international trade and logistics, with a specialization in HSN codes for different regions.

    Product Name: "{product_name}"
    Description: "{description}"
    Target Region: "{region}"

    Based on the product information, provide the following:
    1.  {region_specific_instruction}
    2.  A confidence score for your prediction (from 0 to 1).
    3.  A brief explanation for your choice, mentioning the target region.
    4.  A list of 3 similar products and their relevant HSN codes.

    Format your response as a JSON object with the following keys: "hsn_code", "confidence_score", "explanation", and "similar_products" (which should be a list of objects, each with "name" and "hsn" keys).
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API failed: {e}. Falling back to ClearTax API.")
        return get_hsn_from_cleartax(product_name, description, region)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    product_name = request.form['product_name']
    description = request.form['description']
    region = request.form['region']

    prediction_json = get_hsn_prediction(product_name, description, region)

    try:
        import json
        result = json.loads(prediction_json)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error decoding JSON: {e}")
        print(f"Received from OpenAI: {prediction_json}")
        result = {
            "hsn_code": "Error",
            "confidence_score": "N/A",
            "explanation": "Could not parse the prediction from the model. Please try again.",
            "similar_products": []
        }

    return render_template('index.html', result=result)

@app.route('/download_sample')
def download_sample():
    return send_from_directory(directory='.', path='sample_products.csv', as_attachment=True)

@app.route('/bulk_predict', methods=['POST'])
def bulk_predict():
    if 'csv_file' not in request.files:
        return "No file part"
    file = request.files['csv_file']
    if file.filename == '':
        return "No selected file"

    if file and file.filename.endswith('.csv'):
        # Read the CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        # Skip header row
        header = next(csv_input)
        
        results = []
        for row in csv_input:
            product_name = row[0]
            description = row[1]
            region = row[2] if len(row) > 2 else "International"
            
            prediction_json = get_hsn_prediction(product_name, description, region)
            try:
                prediction_data = json.loads(prediction_json)
                results.append([
                    product_name,
                    description,
                    region,
                    prediction_data.get('hsn_code', 'Error'),
                    prediction_data.get('confidence_score', 'N/A'),
                    prediction_data.get('explanation', 'Error parsing response.')
                ])
            except (json.JSONDecodeError, TypeError):
                results.append([
                    product_name,
                    description,
                    region,
                    "Error",
                    "N/A",
                    "Could not parse the prediction from the model."
                ])

        # Create a new CSV in memory
        output_stream = io.StringIO()
        csv_writer = csv.writer(output_stream)
        
        # Write header and results
        csv_writer.writerow(['product_name', 'description', 'region', 'hsn_code', 'confidence_score', 'explanation'])
        csv_writer.writerows(results)
        
        output_stream.seek(0)
        
        return Response(
            output_stream.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=hsn_predictions.csv"})

    return "Invalid file type"

if __name__ == '__main__':
    app.run(debug=True)
