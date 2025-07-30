# Casper Sales Analysis Dashboard

A Streamlit dashboard for analyzing Casper sales data across different channels, divisions, and time periods.

## Features

- **Flexible Filtering**: Select any combination of sales channels and product divisions
- **Time Aggregation**: View data by month or quarter
- **Multiple Metrics**: Analyze Sales Amount (Billion VND), Total Volume, and Actual Sales Volume
- **Year-over-Year Analysis**: Compare performance with the same period last year
- **Summary Statistics**: View key metrics for the latest period with YoY comparison
- **Interactive Charts**: Powered by Plotly for interactive data visualization

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Place your data file `Sales Report by Month Raw Data.xlsx` in the project directory
4. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Project Structure

- `streamlit_app.py` - Main Streamlit application with visualization
- `data_processing.py` - Data loading and cleaning functions
- `requirements.txt` - Python dependencies
- `Casper Sales Data.py` - Original data processing script (for reference)

## Data Requirements

The application expects an Excel file named `Sales Report by Month Raw Data.xlsx` with the following columns:
- Month
- Distribution channel
- Division
- Region
- Type of product
- Sales amount (exclude VAT)
- Total volume
- Actual sales volume

