# 📊 Django Data Analyzer App

Upload CSV/Excel files, analyze your dataset, and generate interactive charts — all in a Django web app.

## 🚀 Features

- Upload CSV/XLSX/XLS datasets
- Auto summary statistics using pandas
- Chart types:
  - Histogram
  - Pie Chart
  - Line Chart
  - Area Chart
- Per-chart detail pages
- Uses Plotly for interactive visualization

## 🛠 Built With

- Django
- Bootstrap
- pandas
- Plotly

## 📦 Setup Instructions

```bash
git clone https://github.com/dydevops/Django-Data-Analyzer.git
cd django-data-analyzer
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
