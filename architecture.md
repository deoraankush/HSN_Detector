# HSN Code Predictor Architecture

This diagram illustrates the architecture of the HSN Code Predictor application, showing the flow of data from user interaction to backend processing and external API calls.

```mermaid
graph TD
    subgraph User Interaction
        User["<br/>User<br/>(Browser)"]
    end

    subgraph "Backend Application (hsn_generator)"
        WebApp["Flask Server<br/>(app.py)"]
        PredictionLogic{"HSN Prediction Logic"}
        CSVHandler["Bulk CSV Processor"]
    end

    subgraph "External Services"
        OpenAI["OpenAI API"]
        ClearTax["ClearTax API (Fallback)"]
    end

    User -- "1. Enters Product Info" --> WebApp
    User -- "2. Uploads Product CSV" --> WebApp

    WebApp -- "/predict (Single)" --> PredictionLogic
    WebApp -- "/bulk_predict (Bulk)" --> CSVHandler
    CSVHandler -- "For each product row" --> PredictionLogic

    PredictionLogic -- "Tries First" --> OpenAI
    OpenAI -- "Success (JSON Response)" ---> PredictionLogic
    PredictionLogic -- "On Failure" --> ClearTax
    ClearTax -- "Fallback (JSON Response)" --> PredictionLogic

    PredictionLogic -- "Returns Prediction" --> WebApp

    WebApp -- "Renders Result on Page" --> User
    WebApp -- "Generates and Downloads<br/>Result CSV" --> User
    
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style WebApp fill:#bbf,stroke:#333,stroke-width:2px
    style OpenAI fill:#9f9,stroke:#333,stroke-width:2px
    style ClearTax fill:#ff9,stroke:#333,stroke-width:2px
``` 