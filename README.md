# Fake News 

<Strong>This tool is trained on publicly available datasets that may carry labeling bias based on political or cultural context. This is intended to be a supportive tool, not a final judgment. It WILL be inaccurate sometimes.</Strong>

This project is designed to help users detect potential fake news and it's poltical bias. The primary function allows users to copy and paste the URL of a news article, and the system will provide an analysis based on a machine learning model. 


## Tech Stack

**Backend:**
*   Python
*   FastAPI 
*   Scikit-learn

**Frontend:**
*   React
*   Vite
*   TypeScript
*   HTML & CSS

**Machine Learning Model:**
*   The model is saved as `backend/models/fake_news_model.pkl`.
*   Model performance metrics can be found in `backend/models/model_metrics.json`.

<p align="center">
    <img src="https://github.com/user-attachments/assets/354f12c0-b8a4-4174-a3ec-e33164f5eb2d" alt="fakenews" width="45%"/>
    <img src="https://github.com/user-attachments/assets/9fca83f5-1fe8-4246-8734-909dd2a2a461" alt="image" width="45%"/>
</p>

## Setup and Installation

### Prerequisites
*   Python 3.10.12
*   Node.js v22.14.0
*   npm 11.1.0


### Backend Setup
1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt  
    ```

### Frontend Setup
1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```

## Usage

### Running the Backend
1.  Navigate to the `backend` directory.
2.  Run the application:
    ```bash
    ./run.sh 
    ```

### Running the Frontend
1.  Navigate to the `frontend` directory.
2.  Start the development server:
    ```bash
    npm run dev
    ```
3.  Open your browser and go to `http://localhost:5173` 

## Model Information

The core of this project is a machine learning model trained to classify news articles as real or fake.
*   **Model File:** `backend/models/fake_news_model.pkl`
*   **Metrics:** Detailed performance metrics are available in `backend/models/model_metrics.json`. This includes information such as accuracy, precision, recall, and F1-score.
*   **Training Data:** The model was trained on a dataset obtained from Kaggle: [Fake News Detection Datasets](https://www.kaggle.com/datasets/emineyetm/fake-news-detection-datasets).


It's important to review these metrics and understand the dataset to be aware of the model's capabilities and limitations.

## License

Distributed under the MIT License. See `LICENSE` for more information.
