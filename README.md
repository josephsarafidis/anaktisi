# Parliament Search App

A full-stack application for searching and analyzing parliamentary speeches, featuring LSI topic modeling, K-Means clustering, and Sentiment Analysis.

## 🚀 Quick Start

To run the app on your local machine using Docker:

1.  **Clone this repository**
2.  **Start the application:**
    Open your terminal in the project root and run:
    ```bash
    docker compose up --build
    ```
    *Note: The first run may take a few minutes as it builds the images and runs the data processing pipeline automatically.*

3.  **Open in Browser:**
    Navigate to [http://localhost:5173/](http://localhost:5173/)

---

## 📊 Using the Complete Dataset

By default, this repository uses a sample of 10,000 speeches (`data/random_sample.csv`) due to file size limitations. To use the complete dataset or your own custom data, follow these steps:

1.  **Add your data:**
    Place your full CSV file inside the `data/` folder.

2.  **Update the configuration (Optional):**
    If your file is named something other than `random_sample.csv`, open `data-processing-scripts/preprocess.py` and update the `INPUT_FILE` variable:
    ```python
    INPUT_FILE = "data/your_full_dataset.csv"
    ```

3.  **Re-run the pipeline:**
    Simply run the Docker command again. The `data_pipeline` container will detect the changes, process the new data (Stemming, TF-IDF, LSI, Clustering, etc.), and update the backend automatically.
    ```bash
    docker compose up --build
    ```

    *Tip: If you only want to re-process the data without restarting the web server, you can run:*
    ```bash
    docker compose up --build data_pipeline
    ```

## 🐳 Architecture

The application is containerized into three services:

* **`parliament_pipeline`**: Runs the Python data science scripts (cleaning, clustering, modeling) sequentially. It shares the results with the API via a shared volume.
* **`parliament_api`**: A FastAPI backend (Python 3.11) that serves the search results and analytics.
* **`parliament_web`**: A React frontend served via Vite.

