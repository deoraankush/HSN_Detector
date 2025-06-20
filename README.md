# AI-Powered HSN Code Predictor

This project is an AI-powered system that intelligently predicts the correct Harmonized System of Nomenclature (HSN) code for a product based on its name and description. It's designed to streamline cross-border logistics and ensure compliance.

## Core Functionalities

*   **🔍 HSN Code Prediction:** Predicts the most likely HSN code from a product name and/or detailed description.
*   **💡 Reasoning and Confidence:** Provides a natural language explanation for the prediction and a confidence score.
*   **🧾 Similar Product Suggestions:** Shows similar products and their HSN codes for reference.
*   **📁 Bulk CSV Upload:** Supports uploading a CSV file for processing multiple products at once.

## Setup and Installation

Follow these steps to get the application running on your local machine.

### Prerequisites

*   Python 3.8 or higher
*   A virtual environment tool (like `venv`)

### Installation Steps

1.  **Clone the repository or download the project files.**

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys:**
    *   This project uses the OpenAI API as the primary service. It is currently hardcoded in `app.py`.
    *   **For better security, it is highly recommended to use environment variables.** You can create a `.env` file in the project root:
        ```
        OPENAI_API_KEY="your_openai_api_key_here"
        ```
        And then modify `app.py` to load the key using `os.getenv("OPENAI_API_KEY")`.

    *   The application is also configured to use the **ClearTax API** as a fallback. To enable this, you need to set the following environment variables in your `.env` file and update the placeholder implementation in `app.py`:
        ```
        CLEARTAX_API_KEY="your_cleartax_api_key_here"
        CLEARTAX_API_URL="your_cleartax_api_endpoint_here"
        ```

## How to Run the Application

1.  **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```

2.  **Start the Flask development server:**
    ```bash
    python3 app.py
    ```

3.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

## How to Use the Tool

### Single Product Prediction

1.  Enter the **Product Name** and **Product Description** into the respective fields on the main page.
2.  Click the "Predict HSN Code" button.
3.  The predicted HSN code, confidence score, explanation, and similar products will appear below the form.

### Bulk Prediction with CSV

1.  **Prepare your CSV file.** The file must have two columns: `product_name` and `description`.
2.  You can download a pre-formatted sample file by clicking the "sample file" link on the web interface.
3.  Use the "Bulk HSN Code Prediction" section to choose and upload your CSV file.
4.  Click the "Predict HSN for CSV" button.
5.  A new CSV file named `hsn_predictions.csv` containing the results will be automatically downloaded by your browser. 