from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from blog.templatetags import extras
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .forms import DatasetForm
import pandas as pd
import plotly.express as px
import os
from .models import Dataset
# Create your views here.


def upload_and_analyze(request):
    chart_html = None
    df = None
    columns_list = []

    if request.method == 'POST':
        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save()
            file_path = dataset.file.path
            ext = os.path.splitext(file_path)[1].lower()

            try:
                # 📄 Read CSV or Excel based on file extension
                if ext == '.csv':
                    try:
                        df = pd.read_csv(file_path, encoding='utf-8')
                    except UnicodeDecodeError:
                        df = pd.read_csv(file_path, encoding='ISO-8859-1')
                elif ext == '.xlsx':
                    df = pd.read_excel(file_path, engine='openpyxl')
                elif ext == '.xls':
                    df = pd.read_excel(file_path, engine='xlrd')
                else:
                    return render(request, 'analysis/error.html', {
                        'error': 'Unsupported file format. Please upload CSV or Excel files.'
                    })

                # 🧾 Summary
                summary = df.describe(include='all').to_html(classes='table table-bordered')

                # 📋 Get all column names
                columns_list = df.columns.tolist()

                # 📈 Automatically pick a numeric column
                numeric_cols = df.select_dtypes(include='number').columns
                if len(numeric_cols) > 0:
                    fig = px.histogram(df, x=numeric_cols[0], title=f'{numeric_cols[0]} Distribution')
                    chart_html = fig.to_html()
                else:
                    chart_html = "<p class='text-warning'>No numeric columns found for charting.</p>"

                return render(request, 'analysis/result.html', {
                    'form': form,
                    'summary': summary,
                    'chart_html': chart_html,
                    'columns_list': columns_list
                })

            except Exception as e:
                return render(request, 'analysis/error.html', {'error': str(e)})

    else:
        form = DatasetForm()

    return render(request, 'analysis/upload.html', {'form': form})



def dataset_list(request):
    datasets = Dataset.objects.order_by('-uploaded_at')
    return render(request, 'analysis/dataset_list.html', {'datasets': datasets})



def dataset_detail(request, data_slug):
    dataset = get_object_or_404(Dataset, slug=data_slug)
    file_path = dataset.file.path
    ext = os.path.splitext(file_path)[1].lower()

    chart_html = None
    pie_chart_html = None
    line_chart_html = None
    area_chart_html = None
    columns_list = []

    try:
        # Load dataset
        if ext == '.csv':
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='ISO-8859-1')
        elif ext in ['.xlsx', '.xls']:
            engine = 'openpyxl' if ext == '.xlsx' else 'xlrd'
            df = pd.read_excel(file_path, engine=engine)
        else:
            return render(request, 'analysis/error.html', {'error': 'Unsupported file format'})

        summary = df.describe(include='all').to_html(classes='table table-bordered')
        columns_list = df.columns.tolist()

        # 📊 Histogram
        numeric_cols = df.select_dtypes(include='number').columns
        if len(numeric_cols) > 0:
            fig = px.histogram(df, x=numeric_cols[0], title=f'{numeric_cols[0]} Distribution')
            chart_html = fig.to_html()
        else:
            chart_html = "<p class='text-warning'>No numeric column found for histogram.</p>"

        # 🥧 Pie Chart
        cat_cols = df.select_dtypes(include='object').columns
        if len(cat_cols) > 0 and len(numeric_cols) > 0:
            pie_df = df.groupby(cat_cols[0])[numeric_cols[0]].sum().reset_index()
            pie_fig = px.pie(pie_df, names=cat_cols[0], values=numeric_cols[0],
                             title=f'{numeric_cols[0]} by {cat_cols[0]}')
            pie_chart_html = pie_fig.to_html()
        else:
            pie_chart_html = "<p class='text-danger'>No suitable columns found for pie chart.</p>"

        # 📈 Line & Area Charts (detect valid datetime column)
        valid_date_col = None
        for col in df.select_dtypes(include='object').columns:
            try:
                converted = pd.to_datetime(df[col], errors='raise')
                if not converted.isnull().all():
                    valid_date_col = col
                    df[col] = converted
                    break
            except Exception:
                continue

        if valid_date_col and len(numeric_cols) > 0:
            try:
                df_sorted = df.sort_values(by=valid_date_col)
                line_fig = px.line(df_sorted, x=valid_date_col, y=numeric_cols[0],
                                   title=f'{numeric_cols[0]} Over {valid_date_col}')
                line_chart_html = line_fig.to_html()

                area_fig = px.area(df_sorted, x=valid_date_col, y=numeric_cols[0],
                                   title=f'Area Chart: {numeric_cols[0]} Over Time')
                area_chart_html = area_fig.to_html()
            except Exception as e:
                line_chart_html = f"<p class='text-danger'>Line chart error: {e}</p>"
                area_chart_html = f"<p class='text-danger'>Area chart error: {e}</p>"
        else:
            line_chart_html = "<p class='text-warning'>No valid datetime and numeric columns for line chart.</p>"
            area_chart_html = "<p class='text-warning'>No valid datetime and numeric columns for area chart.</p>"

        return render(request, 'analysis/dataset_detail.html', {
            'dataset': dataset,
            'summary': summary,
            'columns_list': columns_list,
            'chart_html': chart_html,
            'pie_chart_html': pie_chart_html,
            'line_chart_html': line_chart_html,
            'area_chart_html': area_chart_html,
        })

    except Exception as e:
        return render(request, 'analysis/error.html', {'error': str(e)})
