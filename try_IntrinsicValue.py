import sqlite3
import getopt, sys
import time
from pymongo import MongoClient
import pandas as pd
from io import StringIO
import json
import yfinance as yf
from datetime import datetime, timedelta

#def convert_to_float(value):
# '''Convert a string to a float after removing commas.'''
    #if value is None: return None
    #if value == "": return None
    #try:
        #return float(value.replace(',', '').replace('₹', '').strip())
    #except (ValueError, AttributeError):
        #print(f"Conversion to float failed for value: {value}")
        #return None

def setup_databases():
    '''Set up the SQLite database and create the table if it doesn't exist.'''
    conn = sqlite3.connect('stockdb1.sqlite')
    cur = conn.cursor()
    #cur.execute('DROP TABLE IF EXISTS Info')  # Drop the table if it already exists
    cur.execute('''CREATE TABLE IF NOT EXISTS Info (
        Symbol TEXT,
        Market_cap REAL,
        Current_price REAL,
        High REAL,
        Low REAL,
        Stock_PE REAL,
        Book_Value REAL,
        Dividend_Yield REAL,
        ROCE REAL,
        ROE REAL,
        Face_Value REAL,
        Sector TEXT,
        Industry TEXT,
        TenYrs_SalesGrowth REAL,
        FiveYrs_SalesGrowth REAL,
        ThreeYrs_SalesGrowth REAL,
        ttm_SalesGrowth REAL,
        TenYrs_ProfitGrowth REAL,
        FiveYrs_ProfitGrowth REAL,
        ThreeYrs_ProfitGrowth REAL,
        ttm_ProfitGrowth REAL,
        TenYrs_CAGR REAL,
        FiveYrs_CAGR REAL,
        ThreeYrs_CAGR REAL,
        ttm_CAGR REAL,
        TenYrs_ROE REAL,
        FiveYrs_ROE REAL,
        ThreeYrs_ROE REAL,
        ttm_ROE REAL
    )''')
    conn.commit()

    atlas_mongodb = "mongodb+srv://abhijithk:lLGJeCvvFMBGC4O5@cluster0.3gtba.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    local_mongodb = "mongodb://localhost:27017/"
    cluster = MongoClient(local_mongodb)
    db = cluster["stock_mdb"]
    collection = db["info_m"]
    #collection.delete_many({})  # Clear the collection before inserting new data
    return conn, cur, cluster, collection

def get_alldata(ticker):
    conn, cur, cluster, collection = setup_databases()
    growth_metrics = {}
    ticker = ticker.rstrip()
    cur.execute("SELECT * FROM Info WHERE Symbol=?",(ticker,))
    row = cur.fetchone()
    # Unpack the row into individual variables
    (ticker, market_cap, current_price, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry,
    ten_yrs_sales_growth, five_yrs_sales_growth, three_yrs_sales_growth, ttm_sales_growth,
    ten_yrs_profit_growth, five_yrs_profit_growth, three_yrs_profit_growth, ttm_profit_growth,
    ten_yrs_cagr, five_yrs_cagr, three_yrs_cagr, ttm_cagr,
    ten_yrs_roe, five_yrs_roe, three_yrs_roe, ttm_roe, Intrinsic_Value_Per_Share) = row
    
    # Assign growth metrics to the dictionary
    growth_metrics["TenYrs_SalesGrowth"] = ten_yrs_sales_growth
    growth_metrics["FiveYrs_SalesGrowth"] = five_yrs_sales_growth
    growth_metrics["ThreeYrs_SalesGrowth"] = three_yrs_sales_growth
    growth_metrics["ttm_SalesGrowth"] = ttm_sales_growth
    growth_metrics["TenYrs_ProfitGrowth"] = ten_yrs_profit_growth
    growth_metrics["FiveYrs_ProfitGrowth"] = five_yrs_profit_growth
    growth_metrics["ThreeYrs_ProfitGrowth"] = three_yrs_profit_growth
    growth_metrics["ttm_ProfitGrowth"] = ttm_profit_growth
    growth_metrics["TenYrs_CAGR"] = ten_yrs_cagr
    growth_metrics["FiveYrs_CAGR"] = five_yrs_cagr
    growth_metrics["ThreeYrs_CAGR"] = three_yrs_cagr
    growth_metrics["ttm_CAGR"] = ttm_cagr
    growth_metrics["TenYrs_ROE"] = ten_yrs_roe
    growth_metrics["FiveYrs_ROE"] = five_yrs_roe
    growth_metrics["ThreeYrs_ROE"] = three_yrs_roe
    growth_metrics["ttm_ROE"] = ttm_roe
    
    
    return (ticker, market_cap, current_price, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry, growth_metrics, Intrinsic_Value_Per_Share)

def get_last_Yrs_fcf(ticker):
    '''Fetch the last year's free cash flow (FCF) from MongoDB. not considering NetInvestment and dividend paid
    FCF = Cash from Operating Activities - Working Capital Changes - Fixed Assets Purchased(or capital expenditure)'''
    ticker = ticker.rstrip()  # Remove any trailing whitespace
    conn, cur, cluster, collection = setup_databases()
    result = collection.find_one({"_id": ticker})
    if result is not None and "CashFlow" in result:
        for key, value in result.items():
            if key == "CashFlow":
                cash_flow_json = json.dumps(value, indent=4)
                # Convert JSON to DataFrame
                cash_flow_df = pd.read_json(StringIO(cash_flow_json))
                #print(f"Cash Flow DataFrame for {ticker}:\n{cash_flow_df}")
                #print(f"Columns in Cash Flow DataFrame for {ticker}: {cash_flow_df.columns}")
                # Get the latest two years
                last_year = cash_flow_df.columns[-1]
                #second_last_year = cash_flow_df.columns[-2]
                #print(f"Last year in Cash Flow DataFrame for {ticker}: {last_year}")
                #print(f"Second last year in Cash Flow DataFrame for {ticker}: {second_last_year}")

                Cash_from_Operating_Activity_last_year = cash_flow_df.loc[cash_flow_df['Year'].str.startswith('Cash from Operating Activity'), last_year].values[0]
                #Working_capital_changes_last_year = cash_flow_df.loc[cash_flow_df['Year'].str.startswith('Working capital changes'), last_year].values[0]
                Fixed_assets_purchased_last_year = cash_flow_df.loc[cash_flow_df['Year'].str.startswith('Fixed assets purchased'), last_year].values[0]
                
                # if value are none then 0 is assigned
                Cash_from_Operating_Activity_last_year = Cash_from_Operating_Activity_last_year if Cash_from_Operating_Activity_last_year is not None else 0
                #Working_capital_changes_last_year = Working_capital_changes_last_year if Working_capital_changes_last_year is not None else 0
                Fixed_assets_purchased_last_year = Fixed_assets_purchased_last_year if Fixed_assets_purchased_last_year is not None else 0
                
                fcf_last_year = Cash_from_Operating_Activity_last_year  + Fixed_assets_purchased_last_year
                # fcf_last_year = Cash_from_Operating_Activity_last_year - Working_capital_changes_last_year - Fixed_assets_purchased_last_year
                # here fixed assets purchased(capital expenditure) is taken as {+} because screener already gives negative value
                # Extract the required values for the second last year
                #Cash_from_Operating_Activity_second_last_year = cash_flow_df.loc[cash_flow_df['Year'].str.startswith('Cash from Operating Activity'), second_last_year].values[0]
                #Working_capital_changes_second_last_year = cash_flow_df.loc[cash_flow_df['Year'].str.startswith('Working capital changes'), second_last_year].values[0]
                #Fixed_assets_purchased_second_last_year = cash_flow_df.loc[cash_flow_df['Year'].str.startswith('Fixed assets purchased'), second_last_year].values[0]
                #fcf_second_last_year = Cash_from_Operating_Activity_second_last_year - Working_capital_changes_second_last_year - Fixed_assets_purchased_second_last_year
                #print(f"FCF for the last year for {ticker}: {fcf_last_year}, FCF for the second last year for {ticker}: {fcf_second_last_year}")
                # Calculate the average FCF of the last two years
                #average_fcf = (float(fcf_last_year) + float(fcf_second_last_year)) / 2
                #print(f"Average FCF for the last two years for {ticker}: {average_fcf}")
                #return float(average_fcf)
                return fcf_last_year
    else:
        raise ValueError(f"No cash flow data found for {ticker} in MongoDB")

def get_Weighted_Averages(growth_metrics):
    '''Calculate the weighted average of profit growth, sales growth, and ROE using specified weights.'''
    # Extract the profit growth rates, using 0 as a default if any are None
    ttm_profit_growth = growth_metrics.get("ttm_ProfitGrowth", 0) or 0
    three_yrs_profit_growth = growth_metrics.get("ThreeYrs_ProfitGrowth", 0) or 0
    five_yrs_profit_growth = growth_metrics.get("FiveYrs_ProfitGrowth", 0) or 0
    ten_yrs_profit_growth = growth_metrics.get("TenYrs_ProfitGrowth", 0) or 0
    
    # Calculate the weighted average profit growth rate. More weightage to 3 and 5 years profit growth
    if ttm_profit_growth is not None and three_yrs_profit_growth is not None and five_yrs_profit_growth is not None and ten_yrs_profit_growth is not None:
        Weighted_ProfitGrowth = (0.2 * ttm_profit_growth) + (0.4 * three_yrs_profit_growth) + (0.3 * five_yrs_profit_growth) + (0.1 * ten_yrs_profit_growth)  # Weights= 20%, 40%, 30%, 10% = 100%
    elif ten_yrs_profit_growth is None:
        Weighted_ProfitGrowth = (0.2 * ttm_profit_growth) + (0.4 * three_yrs_profit_growth) + (0.4 * five_yrs_profit_growth)  # Weights= 20%, 40%, 40% = 100%
    elif ten_yrs_profit_growth is None and five_yrs_profit_growth is None:
        Weighted_ProfitGrowth = (0.3 * ttm_profit_growth) + (0.7 * three_yrs_profit_growth)  # Weights= 30%, 70% = 100%
    elif ten_yrs_profit_growth is None and five_yrs_profit_growth is None and three_yrs_profit_growth is None:
        Weighted_ProfitGrowth = ttm_profit_growth
        print(f"Only TTM Profit Growth is available: {Weighted_ProfitGrowth}, future profit growth rate is uncertain!!!")
    if Weighted_ProfitGrowth is None:
        raise ValueError("Weighted Profit Growth is None. Cannot calculate the average profit growth rate.")
    Weighted_ProfitGrowth = Weighted_ProfitGrowth / 100  # Convert the percentage to a decimal
    
    # Extract the sales growth rates, using 0 as a default if any are None
    ttm_sales_growth = growth_metrics.get("ttm_SalesGrowth", 0) or 0
    three_yrs_sales_growth = growth_metrics.get("ThreeYrs_SalesGrowth", 0) or 0
    five_yrs_sales_growth = growth_metrics.get("FiveYrs_SalesGrowth", 0) or 0
    ten_yrs_sales_growth = growth_metrics.get("TenYrs_SalesGrowth", 0) or 0
    
    # Calculate the weighted average sales growth rate
    if ttm_sales_growth is not None and three_yrs_sales_growth is not None and five_yrs_sales_growth is not None and ten_yrs_sales_growth is not None:
        Weighted_SalesGrowth = (0.2 * ttm_sales_growth) + (0.4 * three_yrs_sales_growth) + (0.3 * five_yrs_sales_growth) + (0.1 * ten_yrs_sales_growth)  # Weights= 20%, 40%, 30%, 10% = 100%
    elif ten_yrs_sales_growth is None:
        Weighted_SalesGrowth = (0.2 * ttm_sales_growth) + (0.4 * three_yrs_sales_growth) + (0.4 * five_yrs_sales_growth)  # Weights= 20%, 40%, 40% = 100%
    elif ten_yrs_sales_growth is None and five_yrs_sales_growth is None:
        Weighted_SalesGrowth = (0.3 * ttm_sales_growth) + (0.7 * three_yrs_sales_growth)  # Weights= 30%, 70% = 100%
    elif ten_yrs_sales_growth is None and five_yrs_sales_growth is None and three_yrs_sales_growth is None:
        Weighted_SalesGrowth = ttm_sales_growth
        print(f"Only TTM Sales Growth is available: {Weighted_SalesGrowth}, future sales growth rate is uncertain!!!")
    if Weighted_SalesGrowth is None:
        raise ValueError("Weighted Sales Growth is None. Cannot calculate the average sales growth rate.")
    Weighted_SalesGrowth = Weighted_SalesGrowth / 100  # Convert the percentage to a decimal

    # Extract the ROE rates, using 0 as a default if any are None
    ttm_roe = growth_metrics.get("ttm_ROE", 0) or 0
    three_yrs_roe = growth_metrics.get("ThreeYrs_ROE", 0) or 0
    five_yrs_roe = growth_metrics.get("FiveYrs_ROE", 0) or 0
    ten_yrs_roe = growth_metrics.get("TenYrs_ROE", 0) or 0
    
    # Calculate the weighted average ROE rate
    if ttm_roe is not None and three_yrs_roe is not None and five_yrs_roe is not None and ten_yrs_roe is not None:
        Weighted_ROE = (0.2 * ttm_roe) + (0.4 * three_yrs_roe) + (0.3 * five_yrs_roe) + (0.1 * ten_yrs_roe)  # Weights= 20%, 40%, 30%, 10% = 100%
    elif ten_yrs_roe is None:
        Weighted_ROE = (0.2 * ttm_roe) + (0.4 * three_yrs_roe) + (0.4 * five_yrs_roe)  # Weights= 20%, 40%, 40% = 100%
    elif ten_yrs_roe is None and five_yrs_roe is None:
        Weighted_ROE = (0.3 * ttm_roe) + (0.7 * three_yrs_roe)  # Weights= 30%, 70% = 100%
    elif ten_yrs_roe is None and five_yrs_roe is None and three_yrs_roe is None:
        Weighted_ROE = ttm_roe
        print(f"Only TTM ROE is available: {Weighted_ROE}, future ROE rate is uncertain!!!")
    if Weighted_ROE is None:
        raise ValueError("Weighted ROE is None. Cannot calculate the average ROE rate.")
    Weighted_ROE = Weighted_ROE / 100  # Convert the percentage to a decimal

    # Calculate the weighted average of all three metrics
    #print(f"Weighted profit growth: {Weighted_ProfitGrowth}, Weighted Sales Growth: {Weighted_SalesGrowth}, Weighted ROE: {Weighted_ROE}")
    Weighted_Average = (0.6 * Weighted_ProfitGrowth) + (0.3 * Weighted_SalesGrowth) + (0.1 * Weighted_ROE)

    return Weighted_ProfitGrowth, Weighted_Average

def get_terminal_growth_rate(Weighted_growth_average):
    '''Calculate the terminal growth rate based on the difference between the Weighted CAGR and the GDP growth rate.'''
    gdp_growth_rate = 0.07  # GDP Growth Rate of India (7%)
    diff_cagr_gdp = Weighted_growth_average - gdp_growth_rate 
    # Calculate the terminal growth rate based on the difference between the Weighted CAGR and the GDP growth rate
    # If the difference is less than or equal to 1%, the terminal growth rate is 2% 
    if diff_cagr_gdp <= 0.01:
        terminal_growth_rate = 0.03
        #print(f"Minimum growth(or matured): {terminal_growth_rate}")
    # else if the difference is greater than 1% and less than or equal to 3%, the terminal growth rate is 3% 
    elif diff_cagr_gdp > 0.01 and diff_cagr_gdp <= 0.06: # for diff greater than 0.01 and less than or equal to 0.03
        terminal_growth_rate = 0.04
        #print(f"Moderate growth: {terminal_growth_rate}")
    # else the terminal growth rate is 4%
    elif diff_cagr_gdp > 0.06:
        terminal_growth_rate = 0.06
        #print(f"High growth: {terminal_growth_rate}")
    else:
        raise ValueError("Invalid difference between Weighted CAGR and GDP growth rate.difference between Weighted CAGR and GDP growth rate: {diff_cagr_gdp}")
    terminal_growth_rate = min(terminal_growth_rate, gdp_growth_rate)  # Cap the terminal growth rate at the GDP growth rate
    return terminal_growth_rate


# Project Free Cash Flows for the specified number of years
def project_cash_flows(fcf, Weighted_cagr, years):
    # Check if the initial Free Cash Flow (FCF) is provided
    if fcf is None:
        raise ValueError("Free Cash Flow (FCF) is None. Cannot project cash flows.")
    
    cash_flows = []
    
    # Loop through each year from 1 to the specified number of projection years
    for year in range(1, years + 1):
        # using the formula: Future FCF = Last FCF * (1 + Weighted CAGR) ^ Year
        future_fcf = fcf * ((1 + Weighted_cagr) ** year)
        cash_flows.append(future_fcf)
    
    return cash_flows


def get_WACC(ticker, market_cap, current_price, stock_pe, growth_metrics, Weighted_ProfitGrowth):
    '''Calculate the discount rate (WACC) for the Discounted Cash Flow (DCF) analysis.'''
    def get_market_return(stock_pe, Weighted_ProfitGrowth):      # Using implied market return, market_return = earnings yeild+profit growth rate
        '''Fetch the market return from the stock table in MongoDB.'''
        earnings_yield = 1 / stock_pe
        market_return = earnings_yield + Weighted_ProfitGrowth
        #print(f"Implied Market Return: {market_return}, Earnings Yield: {earnings_yield}, Profit Growth Rate: {get_Weighted_ProfitGrowth(growth_metrics)}")
        return market_return
    
    def get_cost_of_equity(ticker): # Cost of Equity = Risk-Free Rate + Beta * (Market Return - Risk-Free Rate)
        '''Fetch the cost of equity from the stock table in MongoDB.'''
        ticker = ticker.rstrip()
        #bond = yf.Ticker("NIFTYGS10YR.NS")
        #bond_data = bond.history(period="1d")
        #if bond_data.empty:
            #print("No data found for NIFTYGS10YR.NS, setting risk-free rate to default value of India 10-year government bond = 7% => 0.07")
            #risk_free_rate = 0.07
        #else:
            #risk_free_rate = bond_data['Close'].iloc[-1] / 100
        #print(f"Risk-Free Rate: {risk_free_rate}")
        
        def get_beta(ticker):
            if not ticker.endswith(".NS"):
                ticker = ticker + ".NS"
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                if 'beta' in info:
                    beta_value = info['beta']
                else:
                    beta_value = '1'
                    print(f"No beta value found for {ticker}. Setting beta value to 1.")
            except Exception as e:
                beta_value = '1'
                print(f"Error fetching data for {ticker}: {e}. Setting beta value to 1.")
            #print(ticker, beta_value)
            return float(beta_value)
        
        risk_free_rate = 0.069  # 10-year Indian Government Bond Yield (6.9%) as of 2021-09-30 taken in middle of 6.6% and 7.2% for past three years
        beta = 1             # get_beta(ticker) due to error, correctioin needed
        #print(f"Beta value for {ticker}: {beta}")
        market_return = get_market_return(stock_pe, Weighted_ProfitGrowth)
        #print(f"risk_free_rate:{risk_free_rate}, beta: {beta}, market return:{market_return}")
        cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
        if cost_of_equity is None:
            raise ValueError(f"Cost of equity is None for {ticker}")
        return float(cost_of_equity)
    
    def get_Debt_And_Interest(ticker):
        '''Fetch the debt and interest expense from the balance sheet in MongoDB.'''
        ticker = ticker.rstrip()  # Remove any trailing whitespace
        conn, cur, cluster, collection = setup_databases()
        result = collection.find_one({"_id": ticker})
        Borrowings = None
        interest = None

        if result is not None and "BalanceSheet" in result:
            for key, value in result.items():
                if key == "BalanceSheet":
                    balance_sheet_json = json.dumps(value, indent=4)
                    # Convert JSON to DataFrame
                    balance_sheet_df = pd.read_json(StringIO(balance_sheet_json))
                    # Assuming the DataFrame has a column named 'Year' and 'FreeCashFlow'
                    last_year = balance_sheet_df.columns[-1]  # Get the latest year
                    Borrowings = balance_sheet_df.loc[balance_sheet_df['Year'].str.startswith('Borrowings'), last_year].values[0]
                    if Borrowings is None:
                        Borrowings = 0 # change this
#                        raise ValueError(f"Borrowings is None for {ticker} in the latest year")

        if result is not None and "ProfitLoss" in result:
            for key, value in result.items():
                if key == "ProfitLoss":
                    profit_loss_json = json.dumps(value, indent=4)
                    # Convert JSON to DataFrame
                    profit_loss_df = pd.read_json(StringIO(profit_loss_json))
                    # Assuming the DataFrame has a column named 'Year' and 'Interest'
                    last_year = profit_loss_df.columns[-2]  # Get the latest year
                    interest = profit_loss_df.loc[profit_loss_df['Year'].str.startswith('Interest'), last_year].values[0]
                    if interest is None:
                        interest = 0  # change this
#                        raise ValueError(f"Interest is None for {ticker} in the latest year")

        if Borrowings is not None and interest is not None:
            return float(Borrowings), float(interest)
        else:
            raise ValueError(f"Borrowings or interest is None for {ticker} in the latest year")
    
    def get_tax_rate(ticker):
        '''Fetch the tax rate from the profit and loss table in MongoDB.'''
        ticker = ticker.rstrip()  # Remove any trailing whitespace
        conn, cur, cluster, collection = setup_databases()
        result = collection.find_one({"_id": ticker})
        if result is not None and "ProfitLoss" in result:
            for key, value in result.items():
                if key == "ProfitLoss":
                    profit_loss_json = json.dumps(value, indent=4)
                    # Convert JSON to DataFrame
                    profit_loss_df = pd.read_json(StringIO(profit_loss_json))
                    # Assuming the DataFrame has a column named 'Year' and 'Tax'
                    last_year = profit_loss_df.columns[-2]  # Get the second latest year
                    tax_percentage = profit_loss_df.loc[profit_loss_df['Year'].str.startswith('Tax'), last_year].values[0]
                    if tax_percentage is None:
                        tax_percentage = 1  # change this
#                        raise ValueError(f"Tax percentage is None for {ticker} in the latest year")
                    tax_percentage = float(tax_percentage.strip('%'))
                    tax_rate = tax_percentage / 100
                    return tax_rate
        else:
            raise ValueError(f"No profit and loss data found for {ticker} in MongoDB")
    
    # WACC Calculation wacc = (Cost of Equity * Equity Weight) + (Cost of Debt * Debt Weight * (1 - Tax Rate))
    equity_value = market_cap  # Equity Value
    debt, interest_expense = get_Debt_And_Interest(ticker)  # Debt and Interest Expense
    debt_value = debt  # Debt Value
    
    equity_weight = equity_value / (equity_value + debt_value)  # Equity_weight = equity_value / (equity_value + debt_value)
    debt_weight = debt_value / (equity_value + debt_value)  # Debt_weight = debt_value / (equity_value + debt_value)
    
    cost_of_equity = get_cost_of_equity(ticker)  # Cost of Equity
    #print(f"Cost of Equity: {cost_of_equity}")
    tax_rate = get_tax_rate(ticker)          # Tax Rate
    #print(f"Tax Rate: {tax_rate}")
    if debt != 0:
        cost_of_debt = interest_expense / (debt * (1 - tax_rate))
    else:
        cost_of_debt = 0
        #print(f"Debt is 0 for {ticker}. Setting Cost of Debt to 0.")
    
    # Calculate the WACC
    #print(f"context: cost_of_equity={cost_of_equity}, equity_weight={equity_weight}, cost_of_debt={cost_of_debt}, debt_weight={debt_weight}, tax_rate={tax_rate}")
    #wacc = (cost_of_equity * equity_weight) + (cost_of_debt * debt_weight * (1 - tax_rate))
    wacc = (cost_of_equity * equity_weight) + (cost_of_debt * debt_weight)
    return float(wacc)

# Calculate Terminal Value, terminal value = last_fcf * (1 + terminal growth rate) / (wacc - terminal growth rate)
def calculate_terminal_value(last_fcf, terminal_growth_rate, wacc):
    if last_fcf is None or last_fcf == 0:
        raise ValueError("Last year's Free Cash Flow (FCF) is None or 0. Cannot calculate terminal value.")
    return last_fcf * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)

# Discount Cash Flows to Present Value, discount cash flows = cash flows / (1 + discount rate) ^ year 
def discount_cash_flows(cash_flows, WACC):
    discounted_values = []
    num_years = len(cash_flows) - 1  # The last value in cash_flows is the terminal value
    for year, cf in enumerate(cash_flows[:num_years], start=1):
        try:
            discount_factor = 1 / ((1 + WACC) ** year)
            discounted_value = cf * discount_factor
            #print(f"Year: {year}, Cash Flow: {cf}, Discount Factor: {discount_factor}, Discounted Value: {discounted_value}")
            discounted_values.append(discounted_value)
        except OverflowError:
            print(f"OverflowError: cf={cf}, year={year}, discount_rate={WACC}")
            discounted_values.append(float('inf'))  # Use infinity to indicate overflow
    
    # Handle the terminal value separately
    terminal_value = cash_flows[-1]
    terminal_discount_factor = 1 / ((1 + WACC) ** num_years)
    discounted_terminal_value = terminal_value * terminal_discount_factor
    #print(f"Terminal Value: {terminal_value}, Terminal Discount Factor: {terminal_discount_factor}, Discounted Terminal Value: {discounted_terminal_value}")
    discounted_values.append(discounted_terminal_value)
    
    return discounted_values

def Net_Debt(ticker):
    '''Calculate the Net Debt of the company.'''
    ticker = ticker.rstrip()  # Remove any trailing whitespace
    conn, cur, cluster, collection = setup_databases()
    result = collection.find_one({"_id": ticker})
    if result is not None and "BalanceSheet" in result:
        for key, value in result.items():
            if key == "BalanceSheet":
                balance_sheet_json = json.dumps(value, indent=4)
                # Convert JSON to DataFrame
                balance_sheet_df = pd.read_json(StringIO(balance_sheet_json))
                #print(f"Balance Sheet DataFrame for {ticker}:\n{balance_sheet_df}")
                #print(f"Columns in Balance Sheet DataFrame for {ticker}: {balance_sheet_df.columns}")
                # Assuming the DataFrame has a column named 'Year' and 'FreeCashFlow'
                last_year = balance_sheet_df.columns[-1]     # Get the latest year
                #print(f"Last year in Balance Sheet DataFrame for {ticker}: {last_year}")
                Borrowings = balance_sheet_df.loc[balance_sheet_df['Year'].str.startswith('Borrowings'), last_year].values[0]
                #print(f"Borrowings for last year for {ticker}: {Borrowings}")
                Cash_Equivalents = balance_sheet_df.loc[balance_sheet_df['Year'].str.startswith('Cash Equivalents'),last_year].values[0]
                #print(f"Cash Equivalents for last year for {ticker}: {Cash_Equivalents}")
                if Borrowings is None or Cash_Equivalents is None:
                    Borrowings = 0        # change this
                    Cash_Equivalents = 0  # change this
#                    raise ValueError(f"Borrowings or Cash Equivalents is None for {ticker} in the latest year")
                net_debt = Borrowings - Cash_Equivalents
                return net_debt
    else:
        raise ValueError(f"No balance sheet data found for {ticker} in MongoDB")

def findIntrinsicValue(ticker):
    try:
        # Get all the data for the ticker
        ticker, market_cap, current_price, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry, growth_metrics, Intrinsic_Value_Per_Share = get_alldata(ticker)
        # if current_price is None or current_price == 0: stock_pe =0 or none or any other value used in calculation is none then return intrinsic value as -999999999
        if market_cap is None or market_cap == 0 or current_price is None or current_price == 0 or stock_pe is None or stock_pe == 0:
            return -999999999
        # DCF Calculation Parameters
        #fcf_last_year = 5000000  # Last year's Free Cash Flow (in dollars)
        #growth_rate = 0.05  # Growth rate for the next few years (5%)
        #discount_rate = 0.10  # Discount rate (WACC) (10%)
        #terminal_growth_rate = 0.03  # Terminal growth rate (3%)
        projection_years = 5  # Number of years to project
        
        # Fetch last year free cash flow
        fcf_last_year = get_last_Yrs_fcf(ticker)
        #print(f"The last year free cash flow: {fcf_last_year}")

        # Calculate the average growth rate for future cash flows
        Weighted_ProfitGrowth, Weighted_Growth_Average = get_Weighted_Averages(growth_metrics)     
        #print(f"Weighted Growth average of profit growth, sales growth and roe: {Weighted_Growth_Average}")
        
        # Calculate the terminal growth rate
        terminal_growth_rate = get_terminal_growth_rate(Weighted_Growth_Average)
        #print(f"Terminal Growth Rate: {terminal_growth_rate}")
        
        # Project Free Cash Flows
        projected_future_fcfs = project_cash_flows(fcf_last_year, Weighted_Growth_Average, projection_years)
        #print(f"Projected Free Cash Flows: {projected_future_fcfs}")
        
        # Calculate the Weighted Average Cost of Capital (WACC)
        WACC = get_WACC(ticker, market_cap, current_price, stock_pe, growth_metrics, Weighted_ProfitGrowth)  # Weighted Average Cost of Capital (WACC)
    #    if WACC <= 0:
    #        raise ValueError("WACC must be a positive value for discounting cash flows.")
        #print(f"WACC: {WACC}")
        
        # Calculate the Terminal Value
        terminal_value = calculate_terminal_value(projected_future_fcfs[-1], terminal_growth_rate, WACC)
        #print(f"Terminal Value: {terminal_value}")
        
        # Discount Cash Flows to Present Value
        total_cash_flows = projected_future_fcfs + [terminal_value] 
        discounted_cash_flows = discount_cash_flows(total_cash_flows, WACC)
        #print(f"Discounted Cash Flows: {discounted_cash_flows}")
        
        # Calculate the Net Debt of the company
        net_debt_value = Net_Debt(ticker)
        #print(f"Net Debt: {net_debt_value}")
        
        # Calculate the Intrinsic Value of the company
        intrinsic_value = sum(discounted_cash_flows) - net_debt_value         # sum(discounted_cash_flows) => Enterprise Value
        #print("Total Discounted Cash Flows: ", sum(discounted_cash_flows), "Net Debt: ", net_debt_value, "Intrinsic Value: ", intrinsic_value)
        num_shares = (market_cap ) / current_price  # Number of shares in crores as market cap is in crores 
        #print("Number of Shares Outstanding in crores: ", num_shares)
        intrinsic_value_per_share = intrinsic_value / num_shares   # Intrinsic Value per Share
        #print("Intrinsic Value of the Company (DCF) per share: ₹", round(intrinsic_value_per_share, 4))
        #print("Current Price of the Stock: ₹", current_price)

        # Calculate the percentage difference between the intrinsic value and the current price
        percentage_difference = ((intrinsic_value_per_share - current_price) / current_price) * 100
        #print(f"Percentage Difference between Intrinsic Value and Current Price: {round(percentage_difference, 4)}%")

    #    if abs(percentage_difference) > 100:
    #        print(f"-----------------The {ticker} stock is within the expected value range.---------------------")
    #   elif intrinsic_value_per_share > current_price:
    #        print(f"The {ticker} stock is undervalued.")
    #    elif intrinsic_value_per_share == current_price:
    #        print(f"The {ticker} stock is fairly valued.")
    #    elif intrinsic_value_per_share < current_price:
    #        print(f"The {ticker} stock is overvalued.")
    #    else:
    #        print(f"The {ticker} stock is not within the expected value range.")
        
        return intrinsic_value_per_share
    except Exception as e:
        print(f"An error occurred: {e}")
        return -999999999

def my_main(argv):
    try:
        opts, args = getopt.getopt(argv, "hs:f:")
    except getopt.GetoptError:
        print('screener.py -h [-s SCRIP] [-f filename]')
        sys.exit(2)

    sym = 'INFY'
    file = None

    for opt, arg in opts:
        if opt == '-h':
            print('screener.py -h [-s SCRIP] [-f filename]')
            sys.exit()
        elif opt in ("-s"):
            sym = str(arg)
        elif opt in ("-f"):
            file = str(arg)

    if file:
        with open(file, 'r') as fh:
            for line in fh:
                ticker = line.strip()
                if ticker:
                    Intrinsic_Value_Per_Share = findIntrinsicValue(ticker)
                    print(f"check value: {Intrinsic_Value_Per_Share}")
    else:
        Intrinsic_Value_Per_Share = findIntrinsicValue(sym)
        print(f"check value: {Intrinsic_Value_Per_Share}")

if __name__ == '__main__':
    start_time = time.time()  # Record the start time
    my_main(sys.argv[1:])  # Call the main function
    end_time = time.time()  # Record the end time
    print(f"Total time taken to execute the script: {end_time - start_time} seconds")