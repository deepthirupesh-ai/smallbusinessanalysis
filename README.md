# Small Business Data Analysis: Coffee Shop Demo

This project creates a synthetic dataset for a fictional small coffee shop business and performs exploratory data analysis (EDA) to uncover insights about sales trends, customer behavior, and product performance.

## Project Structure

*   `generate_data.py`: A Python script that creates a SQLite database (`coffee_shop.db`) and populates it with realistic fake data (customers, products, transactions).
*   `analyze_data.py`: A Python script that queries the database, processes the data using Pandas, and generates visualization charts using Matplotlib and Seaborn.
*   `requirements.txt`: A list of Python libraries required to run the scripts.
*   `analysis_output/`: The folder where generated visualizations are saved.

## Setup & Installation

1.  **Prerequisites:** Ensure you have Python installed.
2.  **Install Dependencies:** Run the following command to install the necessary libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Generate the Data
Run the generation script to create the database and seed it with synthetic data. This mimics 90 days of business operations.

```bash
python generate_data.py
```
*Output: Creates `coffee_shop.db` with tables for products, customers, transactions, and transaction_items.*

### 2. Run the Analysis
Run the analysis script to process the data and generate reports/charts.

```bash
python analyze_data.py
```
*Output: Prints general statistics to the console and saves visualization images to the `analysis_output/` folder.*

## Database Schema

The SQLite database (`coffee_shop.db`) contains the following tables:
*   **products**: Menu items with categories and prices.
*   **customers**: Registered customers with name, email, and join date.
*   **transactions**: Sales records including customer link, timestamp, and total amount.
*   **transaction_items**: Individual items purchased within a transaction (linking products and transactions).

## Visualizations

The analysis script generates the following insights in `analysis_output/`:
*   **daily_sales_trend.png**: Tracks total revenue over time to identify growth or seasonal patterns.
*   **hourly_traffic.png**: Shows transaction volume by hour of the day to identify peak rush hours.
*   **top_products.png**: Highlights the most popular menu items by quantity sold.
*   **category_sales.png**: Displays the revenue share distribution across different product categories (e.g., Coffee vs. Bakery).
*   **aov_by_day.png**: Compares the Average Order Value (AOV) across different days of the week.

## Customization

You can modify `generate_data.py` to:
*   Change the date range or number of transactions.
*   Add new products or categories.
*   Adjust traffic weights (e.g., make weekends busier).
