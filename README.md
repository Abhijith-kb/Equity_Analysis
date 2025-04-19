# Equity Analysis

## Overview
This project automates the process of collecting, storing, and analyzing fundamental financial data for companies listed on the National Stock Exchange (NSE) of India. It scrapes detailed financial statements from Screener.in, calculates the intrinsic value of each company’s stock using a Discounted Cash Flow (DCF) model, and provides a user-friendly interface to filter and explore companies based on key financial metrics.

## Features
- Retrieves a complete list of NSE-listed companies using the `nsepython` library.
- Automates data extraction from Screener.in using Selenium and BeautifulSoup.
- Handles rate limiting by adding delays between web requests to avoid blocking.
- Stores general company fundamentals in a SQLite database.
- Saves detailed financial statements (balance sheet, profit & loss, cash flow) in MongoDB.
- Logs companies not found on Screener.in in a blacklist for reference.
- Calculates intrinsic value per share using a DCF valuation model.
- Provides a PyQt5-based graphical user interface to filter companies by market cap, ROE, current price, sector, and industry.

## Technologies Used
- Python 3.x
- `nsepython` for NSE company data
- Selenium for browser automation
- BeautifulSoup for HTML parsing
- SQLite for relational data storage
- MongoDB for document-based financial data storage
- PyQt5 for desktop GUI development

## Installation & Setup
1. **Clone the repository:**
  git clone https://github.com/Abhijith-kb/Equity_Analysis.git
  cd Equity_Analysis

2. **Create and activate a virtual environment:**
- Windows:
  '''bash
  python -m venv venv
  venv\Scripts\activate

- Mac/Linux:
  python3 -m venv venv
  source venv/bin/activate

3. **Install dependencies:**
  pip install -r requirements.txt

4. **Set up MongoDB:**
- Make sure MongoDB is installed and running on your machine.
- Update the MongoDB connection string in the configuration file if needed.

5. **Run the data extraction script:**
- command for ticker : python3 screener.py -t ticker -o option , for filenames : python3 screener.py -f filename.txt -o option
- Check ticker presence in database, if not present then inserts data into databases : python3 screener.py -t TCS -o 1
- Maintainance: Refresh data in SQLite : python3 screener.py -t TCS -o 2
- Maintainance: Refresh data in MongoDB : python3 screener.py -t TCS -o 3
- Display all information of the ticker : python3 screener.py -t TCS -o 4
- To display Intrinsic value of the ticker : python3 screener.py -t TCS -o 5
- Check and update, if new symbols exists in nse_module then update nse_companies_symbols.txt and insert into database. If any symbol cannot be fetched then it will be written in black_list.txt : python3 screener.py -f filename.txt -o 6
- Maintainance: To Update Intrinsic Value of the ticker : python3 screener.py -t TCS -o 1
This will fetch company data, scrape financials, and populate the databases.

6. **Launch the GUI:**
- python3 stocks_filter.py
- Use the interface to filter and explore companies based on your criteria.

## Usage
- Use the GUI to select filters like market capitalization, Current price, ROCE, ROE, sector, industry and undervalued companies
- The app displays companies that meet all selected criteria along with their intrinsic value estimates.
- The blacklist file contains companies that could not be found on Screener.in.

## Images for understanding
Command prompt output displaying the result of executing the Python script screener.py with the ticker symbol 'TCS' and option '-o 4', showing the script's processed data or analysis related to TCS stock.
![Screenshot from 2025-04-19 14-32-08](https://github.com/user-attachments/assets/541047f3-e03e-4401-92a8-d4979f5796bb)

Screenshots of the stocks filtering GUI launched via python3 stocks_filter.py, showing the interface where users can apply filters such as market capitalization, current price, ROCE, ROE, sector, industry, and undervalued status to explore companies meeting selected criteria along with their intrinsic value estimates.
- All companies
![Screenshot from 2025-04-19 14-41-09](https://github.com/user-attachments/assets/373b95cf-6bf1-4105-a249-36ee51a7d415)

- Only Undervalued Companies
![Screenshot from 2025-04-19 14-41-19](https://github.com/user-attachments/assets/dfc3cc42-24bd-4781-8c65-e77fe4df3f36)


