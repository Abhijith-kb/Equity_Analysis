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
   '''
   git clone https://github.com/Abhijith-kb/Equity_Analysis.git
   cd Equity_Analysis
   '''

2. **Create and activate a virtual environment:**
- Windows:
   '''
   python -m venv venv
   venv\Scripts\activate
   '''
- Mac/Linux:
   '''
   python3 -m venv venv
   source venv/bin/activate
   '''

3. **Install dependencies:**
   '''
   pip install -r requirements.txt
   '''

4. **Set up MongoDB:**
- Make sure MongoDB is installed and running on your machine.
- Update the MongoDB connection string in the configuration file if needed.

5. **Run the data extraction script:**
