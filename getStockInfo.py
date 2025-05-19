from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import warnings
import time
from bs4 import BeautifulSoup
import sqlite3
import io
import pandas as pd
from io import StringIO 
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
import json
import warnings
from cryptography.utils import CryptographyDeprecationWarning
import pymongo
from pymongo import MongoClient
from datetime import datetime
import pytz
import os
from try_IntrinsicValue import findIntrinsicValue
#from database_setup import setup_databases
from nsepython import *

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def create_required_files():
    '''Create required files if they do not exist.'''
    required_files = ["nse_companies_symbols.txt", "black_list.txt", "error_button_not_pressed.txt"]
    
    for file in required_files:
        if not os.path.exists(file):
            with open(file, "w") as f:
                pass
            print(f"Created {file}")

# Call the function to create required files, if they do not exist just in case of error
create_required_files()

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
        ttm_ROE REAL,
        Intrinsic_Value_Per_Share REAL
    )''')
    conn.commit()

    local_mongodb = "mongodb://localhost:27017/"
    cluster = MongoClient(local_mongodb)
    db = cluster["stock_mdb"]
    collection = db["info_m"]
    #collection.delete_many({})  # Clear the collection before inserting new data
    return conn, cur, cluster, collection

def is_ticker_in_sql_database(ticker, cur):
    '''Check if a ticker is already present in the SQLite database.'''
    ticker = ticker.rstrip()        # Remove any trailing whitespace(Redundant line just in case..)
    cur.execute("SELECT COUNT(*) FROM Info WHERE Symbol=?",(ticker,))
    return cur.fetchone()[0] > 0

def is_ticker_in_mongodb(ticker, collection):
    '''Check if a ticker is already present in the MongoDB collection.'''
    ticker = ticker.rstrip()         # Remove any trailing whitespace(Redundant line just in case..)
    return collection.count_documents({"_id": ticker}) > 0 

def setup_driver():
    '''Set up the Selenium Chrome WebDriver.'''
    service = Service(executable_path='/usr/local/bin/chromedriver')  # Path to the chromedriver executable
    options = Options()
    options.add_argument("--headless")  # Run the browser in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    options.add_argument("--no-sandbox")  # Disable the sandbox
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    options.add_argument("--window-size=1920x1080")  # Set window size to avoid issues with elements not being visible
    options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
    options.add_argument("--start-maximized")  # Start maximized to ensure elements are visible
    options.add_argument("--disable-extensions")  # Disable extensions to avoid interference
    options.add_argument("--disable-infobars")  # Disable infobars to avoid interference

    driver = webdriver.Chrome(service=service, options=options)
    return driver
    
    #Serv = Service(executable_path=r'/usr/local/bin/chromedriver') # Path to the chromedriver executable
    #Opt = webdriver.ChromeOptions()
    #Opt.add_argument("--headless=new")   # Run the browser in headless mode
    #Opt.add_argument("--disable-gpu")     # Disable GPU acceleration
    #Opt.add_argument("--no-sandbox")      # Disable the sandbox
    #driver = webdriver.Chrome(service=Serv, options=Opt)
    
    #return driver

def load_and_extract_stock_info(driver, ticker):
    """Load the webpage and extract stock information."""
    try:
        address = "https://www.screener.in/company/" + ticker + "/consolidated/"
        html_src = page_check(driver, address)
        page_content = BeautifulSoup(html_src, "html.parser")
        tag_str = page_content.findAll("li", attrs={'class': "flex flex-space-between"})
        current_price, market_cap, high, low, stockpe, book_value, dividend_yield, roce, roe, face_value, sector, industry = extract_stock_info(tag_str, page_content)
        growth_metrics = extract_growth_metrics(page_content)

        if all(v is None for v in [current_price, market_cap, stockpe, book_value, dividend_yield, roce, roe, face_value]):
            address = "https://www.screener.in/company/" + ticker + "/"     # Try the standalone page if the consolidated page values are None
            html_src = page_check(driver, address)
            page_content = BeautifulSoup(html_src, "html.parser")
            tag_str = page_content.findAll("li", attrs={'class': "flex flex-space-between"})
            current_price, market_cap, high,low, stockpe, book_value, dividend_yield, roce, roe, face_value, sector, industry = extract_stock_info(tag_str, page_content)
            growth_metrics = extract_growth_metrics(page_content)
        
        # if all values are none even after standalone return none
        if all(v is None for v in [current_price, market_cap, stockpe, book_value, dividend_yield, roce, roe, face_value]):
            return None, None, None, None, None, None, None, None, None, None, None, None, None
        
        return current_price, market_cap, high, low, stockpe, book_value, dividend_yield, roce, roe, face_value, sector, industry, growth_metrics
    except ValueError as e:
        print(f"An error(ValueError) occurred in load_and_extract_stock_info method: {e}")
        return None, None, None, None, None, None, None, None, None, None, None, None, None
    except Exception as e:
        print(f"An error(Exception) occurred in load_and_extract_stock_info method: {e}")
        return None, None, None, None, None, None, None, None, None, None, None, None, None

def page_check(driver, address):
    '''Load a webpage and return its HTML source.'''
    count = 1
    initial_wait_time = 2
    max_wait_time = 10
    
    while True:
        try:
            driver.get(address)
            
            # Check for specific page errors
            if "Error 404: Page Not Found" in driver.page_source: 
                raise ValueError(f"Error 404: Page Not Found for {address}")
            # Check for "Too many requests" error
            if "Too many requests" in driver.page_source:
                wait_time = min(initial_wait_time * (2 ** count), max_wait_time)  # Exponential backoff
                print(f"Too many requests for {address}. Waiting for {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                count += 1
                continue
            
            html_src = str(driver.page_source)
            return html_src 
        except WebDriverException as e:
            print(f"An error(WebDriverException) occurred while loading {address}: {e} in page_check method")
            raise
        except TimeoutException as e:
            print(f"An error(TimeoutException) occurred while loading {address}: {e} in page_check method")
            raise
        except Exception as e:
            print(f"An error(Exception) occurred while loading {address}: {e} in page_check method")
            raise

def extract_stock_info(tag_str, page_content):
    ''''Extract stock information from the HTML tags and convert it to the appropriate data types.'''
    try:
        current_price = convert_to_float(findCurrentprice(tag_str))
        market_cap = convert_to_float(findMarketCap(tag_str))
        high, low = findHighLow(tag_str)
        high = convert_to_float(high)
        low = convert_to_float(low)
        stock_pe = convert_to_float(StockPE(tag_str))
        book_value = convert_to_float(BookValue(tag_str))
        dividend_yield = convert_to_float(DividendYeild(tag_str))
        roce = convert_to_float(ROCE(tag_str))
        roe = convert_to_float(ROE(tag_str))
        face_value = convert_to_float(FaceValue(tag_str))
        sector, industry = industry_sector(page_content)
        
        return current_price, market_cap, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry
    except Exception as e:
        print(f"An error occurred while extracting stock information: {e} in extract_stock_info method")
        return None, None, None, None, None, None, None, None, None, None, None, None

def findCurrentprice(tag_str):
    '''Find the current price of a stock from the HTML tags.'''
    for tag in tag_str:
        str_tag = str(tag)
        if "Current Price" in str_tag:
            cp = BeautifulSoup(str_tag,'html.parser')
            return(cp.find("span",attrs={'class':"number"}).string)
    
    return('0')

def findMarketCap(tag_str):
    '''Find the market capitalization of a stock from the HTML tags.'''
    for tag in tag_str:
        str_tag = str(tag)
        if "Market Cap" in str_tag:
            cp = BeautifulSoup(str_tag,'html.parser')
            return(cp.find("span",attrs={'class':"number"}).string)
    
    return('0')

def findHighLow(tag_str):
    '''Find the high and low prices of a stock from the HTML tags.'''
    for tag in tag_str:
        str_tag = str(tag)
        if "High / Low" in str_tag:
            cp = BeautifulSoup(str_tag,'html.parser')
            numbers = [span.text for span in cp.findAll("span",attrs={'class':"number"})]
            return numbers[0], numbers[1]   
    
    return('0')

def StockPE(tag_str):
    '''Find the P/E ratio of a stock from the HTML tags.'''
    for tag in tag_str:
        str_tag = str(tag)
        if "Stock P/E" in str_tag:
            cp = BeautifulSoup(str_tag,'html.parser')
            return(cp.find("span",attrs={'class':"number"}).string)
    
    return('0')

def BookValue(tag_str):
    '''Find the book value of a stock from the HTML tags.'''
    for tag in tag_str:
        str_tag = str(tag)
        if "Book Value" in str_tag:
            cp = BeautifulSoup(str_tag,'html.parser')
            return(cp.find("span",attrs={'class':"number"}).string)
    
    return('0')

def DividendYeild(tag_str):
    '''Find the dividend yield of a stock from the HTML tags.'''
    for tag in tag_str:
        str_tag = str(tag)
        if "Dividend Yield" in str_tag:
            cp = BeautifulSoup(str_tag,'html.parser')
            return(cp.find("span",attrs={'class':"number"}).string)
    
    return('0')

def ROCE(tag_str):
    '''Find the ROCE of a stock from the HTML tags.'''
    for tag in tag_str:
        str_tag = str(tag)
        if "ROCE" in str_tag:
            cp = BeautifulSoup(str_tag,'html.parser')
            return(cp.find("span",attrs={'class':"number"}).string)
    
    return('0')

def ROE(tag_str):
    '''Find the ROE of a stock from the HTML tags.'''
    for tag in tag_str:
        str_tag = str(tag)
        if "ROE" in str_tag:
            cp = BeautifulSoup(str_tag,'html.parser')
            return(cp.find("span",attrs={'class':"number"}).string)
    
    return('0')

def FaceValue(tag_str):
    '''Find the face value of a stock from the HTML tags.'''
    for tag in tag_str:
        str_tag = str(tag)
        if "Face Value" in str_tag:
            cp = BeautifulSoup(str_tag,'html.parser')
            return(cp.find("span",attrs={'class':"number"}).string)
    
    return('0')

def industry_sector(page_content):
    '''Find the industry and sector of a stock from the HTML tags.'''
    try:
        sector_tag = page_content.find('section', id='peers')
        if sector_tag:
            p_tags = sector_tag.find_all('p', class_='sub')
            a_tags = []
            for p_tag in p_tags:
                # Use partial matching for 'href' to find relevant <a> tags
                a_tags.extend(p_tag.find_all('a', href=lambda href: href and '/company/compare/' in href))
            
            # Assuming the first <a> tag is the sector and the second is the industry
            sector = a_tags[0].text.strip() if a_tags else None
            industry = a_tags[1].text.strip() if len(a_tags) > 1 else None
            
            return sector, industry
        else:
            print("Sector tag not found")
            return None, None
    except Exception as e:
        print(f"An error occurred while extracting industry and sector information: {e} in industry_sector method")
        return None, None

def extract_growth_metrics(page_content):
    '''Extract growth metrics from the HTML tags.'''
    try:
        tables = page_content.find_all("table", class_="ranges-table")
        if not tables or len(tables) < 4:
            raise ValueError("Not enough growth metrics tables found")
        
        percentages = []
        for table in tables:
            for td in table.find_all("td"):
                if "%" in td.text:  # Check if the text contains a percentage symbol
                    percentages.append(td.text.strip().replace('%', ''))
        
        if len(percentages) < 16:
            raise ValueError(f"Not enough growth metrics found. Found {len(percentages)} metrics.")
        
        growth_metrics = {
            "TenYrs_SalesGrowth": convert_to_float(percentages[0]),
            "FiveYrs_SalesGrowth": convert_to_float(percentages[1]),
            "ThreeYrs_SalesGrowth": convert_to_float(percentages[2]),
            "ttm_SalesGrowth": convert_to_float(percentages[3]),
            "TenYrs_ProfitGrowth": convert_to_float(percentages[4]),
            "FiveYrs_ProfitGrowth": convert_to_float(percentages[5]),
            "ThreeYrs_ProfitGrowth": convert_to_float(percentages[6]),
            "ttm_ProfitGrowth": convert_to_float(percentages[7]),
            "TenYrs_CAGR": convert_to_float(percentages[8]),
            "FiveYrs_CAGR": convert_to_float(percentages[9]),
            "ThreeYrs_CAGR": convert_to_float(percentages[10]),
            "ttm_CAGR": convert_to_float(percentages[11]),
            "TenYrs_ROE": convert_to_float(percentages[12]),
            "FiveYrs_ROE": convert_to_float(percentages[13]),
            "ThreeYrs_ROE": convert_to_float(percentages[14]),
            "ttm_ROE": convert_to_float(percentages[15])
        }
        return growth_metrics
    except Exception as e:
        print(f"An error occurred while extracting growth metrics: {e} in extract_growth_metrics method")
        return None

def convert_to_float(value):
    '''Convert a string to a float after removing commas.'''
    if value is None: return None
    if value == "": return None
    try:
        return float(value.replace(',', '').replace('₹', '').strip())
    except (ValueError, AttributeError):
        return None


def insert_or_update_into_sql(ticker, market_cap, current_price, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry, growth_metrics, Intrinsic_Value_Per_Share, conn, cur):
    '''Insert stock information into the SQLite database.'''
    try:
        ticker = ticker.rstrip()        # Redundant but just in case
        # Check if the ticker exists in the database
        cur.execute("SELECT * FROM Info WHERE Symbol=?", (ticker,))
        if cur.fetchone() is None:
            # If not, create a new entry for the ticker
            cur.execute('''INSERT INTO Info (
                Symbol, Market_cap, Current_price, High, Low, Stock_PE, Book_Value, Dividend_Yield, ROCE, ROE, Face_Value, Sector, Industry,
                TenYrs_SalesGrowth, FiveYrs_SalesGrowth, ThreeYrs_SalesGrowth, ttm_SalesGrowth,
                TenYrs_ProfitGrowth, FiveYrs_ProfitGrowth, ThreeYrs_ProfitGrowth, ttm_ProfitGrowth,
                TenYrs_CAGR, FiveYrs_CAGR, ThreeYrs_CAGR, ttm_CAGR,
                TenYrs_ROE, FiveYrs_ROE, ThreeYrs_ROE, ttm_ROE,
                Intrinsic_Value_Per_Share
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (ticker, market_cap, current_price, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry,
            growth_metrics["TenYrs_SalesGrowth"], growth_metrics["FiveYrs_SalesGrowth"], growth_metrics["ThreeYrs_SalesGrowth"], growth_metrics["ttm_SalesGrowth"],     
            growth_metrics["TenYrs_ProfitGrowth"], growth_metrics["FiveYrs_ProfitGrowth"], growth_metrics["ThreeYrs_ProfitGrowth"], growth_metrics["ttm_ProfitGrowth"],
            growth_metrics["TenYrs_CAGR"], growth_metrics["FiveYrs_CAGR"], growth_metrics["ThreeYrs_CAGR"], growth_metrics["ttm_CAGR"],
            growth_metrics["TenYrs_ROE"], growth_metrics["FiveYrs_ROE"], growth_metrics["ThreeYrs_ROE"], growth_metrics["ttm_ROE"], Intrinsic_Value_Per_Share))
            conn.commit()
            print(f"Inserted fundamental data for {ticker} into SQLite")
        else:
            # If the ticker already exists, update the data
            cur.execute('''UPDATE Info SET 
                Market_cap=?, Current_price=?, High=?, Low=?, Stock_PE=?, Book_Value=?, Dividend_Yield=?, ROCE=?, ROE=?, Face_Value=?, Sector=?, Industry=?,
                TenYrs_SalesGrowth=?, FiveYrs_SalesGrowth=?, ThreeYrs_SalesGrowth=?, ttm_SalesGrowth=?,
                TenYrs_ProfitGrowth=?, FiveYrs_ProfitGrowth=?, ThreeYrs_ProfitGrowth=?, ttm_ProfitGrowth=?,
                TenYrs_CAGR=?, FiveYrs_CAGR=?, ThreeYrs_CAGR=?, ttm_CAGR=?,
                TenYrs_ROE=?, FiveYrs_ROE=?, ThreeYrs_ROE=?, ttm_ROE=?,
                Intrinsic_Value_Per_Share=? 
                WHERE Symbol=?''', 
                (market_cap, current_price, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry,
                growth_metrics["TenYrs_SalesGrowth"], growth_metrics["FiveYrs_SalesGrowth"], growth_metrics["ThreeYrs_SalesGrowth"], growth_metrics["ttm_SalesGrowth"],
                growth_metrics["TenYrs_ProfitGrowth"], growth_metrics["FiveYrs_ProfitGrowth"], growth_metrics["ThreeYrs_ProfitGrowth"], growth_metrics["ttm_ProfitGrowth"],
                growth_metrics["TenYrs_CAGR"], growth_metrics["FiveYrs_CAGR"], growth_metrics["ThreeYrs_CAGR"], growth_metrics["ttm_CAGR"],
                growth_metrics["TenYrs_ROE"], growth_metrics["FiveYrs_ROE"], growth_metrics["ThreeYrs_ROE"], growth_metrics["ttm_ROE"],
                Intrinsic_Value_Per_Share,
                ticker))
            conn.commit()
            print(f"Updated fundamental data for {ticker} in SQLite")
    except Exception as e:
        print(f"An error occurred while inserting or updating data for {ticker}: {e} in insert_into_sql method")

def profit_loss(driver, ticker):
    '''Extract the profit and loss table from the webpage.'''
    wait = WebDriverWait(driver, 10)
    retries = 1
    max_retries = 100
    x = 0          # variable to check if the button is pressed
    while x == 0 and retries < max_retries:
        try:
            sales_button = driver.find_elements(By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Sales')]")
            if sales_button:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Sales')]")))
                button.click()
                Sales_minus = wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Sales')]//span[contains(text(), '-')]")))

            expenses_button = driver.find_elements(By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Expenses')]")
            if expenses_button:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Expenses')]")))
                button.click()
                Expenses_minus = wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Expenses')]//span[contains(text(), '-')]")))

            other_income_button = driver.find_elements(By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Other Income')]")
            if other_income_button:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Other Income')]")))
                button.click()
                OtherIncome_minus = wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Other Income')]//span[contains(text(), '-')]")))

            net_profit_button = driver.find_elements(By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Net Profit')]")
            if net_profit_button:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Net Profit')]")))
                button.click()
                NetProfit_minus = wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@id,'profit-loss')]//button[contains(text(), 'Net Profit')]//span[contains(text(), '-')]")))

            if (not sales_button or Sales_minus.is_displayed()) and (not expenses_button or Expenses_minus.is_displayed()) and (not other_income_button or OtherIncome_minus.is_displayed()) and (not net_profit_button or NetProfit_minus.is_displayed()):
                x = 1  # If the element is found, break the loop
        except Exception as e:
            print(f"Not all buttons clicked in profit and loss table of {ticker}. Retry... ({retries + 1}/{max_retries})")
            #print(f"Error: {e}")
            # Dynamically adjust wait if multiple retries fail
            dynamic_wait = min(retries * 0.2, 5)  # Wait up to 5 seconds max if too many retries
            print(f"Waiting dynamically for {dynamic_wait} seconds before retry...")
            time.sleep(dynamic_wait)
            
            driver.refresh()
            #WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            retries += 1
            #time.sleep(5)  # Wait for 5 seconds before retrying

    if x == 0:
        print("Failed to click all buttons in profit and loss table after [10]multiple retries.")
        with open("error_button_not_pressed.txt", "a") as f:
            f.write(f"Ticker: {ticker} - Failed to click all buttons in profit and loss table\n")
        print(f"Added {ticker} to error_button_not_pressed.txt")
        return None

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find_all('section', {'id': 'profit-loss'})
    ProfitLoss_table = pd.read_html(str(table))[0]
    ProfitLoss_table.columns = ["Year"] + list(ProfitLoss_table.columns[1:])
    return ProfitLoss_table

def balance_sheet(driver, ticker):
    '''Extract the balance sheet table from the webpage.'''
    time.sleep(0.2)
    wait = WebDriverWait(driver, 10)
    retries = 1
    max_retries = 100
    x = 0              # variable to check if the button is pressed
    while x == 0 and retries < max_retries:
        try:
            borrowings_button = driver.find_elements(By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Borrowings')]")
            if borrowings_button:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Borrowings')]")))
                button.click()
                Borrowings_minus = wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Borrowings')]//span[contains(text(), '-')]")))

            other_liabilities_button = driver.find_elements(By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Other Liabilities')]")
            if other_liabilities_button:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Other Liabilities')]")))
                button.click()
                OtherLiabilities_minus = wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Other Liabilities')]//span[contains(text(), '-')]")))

            fixed_assets_button = driver.find_elements(By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Fixed Assets')]")
            if fixed_assets_button:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Fixed Assets')]")))
                button.click()
                FixedAssets_minus = wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Fixed Assets')]//span[contains(text(), '-')]")))

            other_assets_button = driver.find_elements(By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Other Assets')]")
            if other_assets_button:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Other Assets')]")))
                button.click()
                OtherAssets_minus = wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@id,'balance-sheet')]//button[contains(text(), 'Other Assets')]//span[contains(text(), '-')]")))

            if (not borrowings_button or Borrowings_minus.is_displayed()) and (not other_liabilities_button or OtherLiabilities_minus.is_displayed()) and (not fixed_assets_button or FixedAssets_minus.is_displayed()) and (not other_assets_button or OtherAssets_minus.is_displayed()):
                x = 1  # If the element is found, break the loop
        except Exception as e:
            print(f"Not all buttons clicked in balance sheet table of {ticker}. Retry... ({retries + 1}/{max_retries})")
            #print(f"Error: {e}")
            # Dynamically adjust wait if multiple retries fail
            dynamic_wait = min(retries * 0.2, 5)  # Wait up to 5 seconds max if too many retries
            print(f"Waiting dynamically for {dynamic_wait} seconds before retry...")
            time.sleep(dynamic_wait)
            
            driver.refresh()
            retries += 1
            #time.sleep(5)  # Wait for 5 seconds before retrying

    if x == 0:
        print("Failed to click all buttons in balance sheet table after multiple retries.")
        with open("error_button_not_pressed.txt", "a") as f:
            f.write(f"Ticker: {ticker} - Failed to click all buttons in balance sheet table\n")
        print(f"Added {ticker} to error_button_not_pressed.txt")
        return None

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find_all('section', {'id': 'balance-sheet'})
    BalanceSheet_table = pd.read_html(str(table))[0]
    BalanceSheet_table.columns = ["Year"] + list(BalanceSheet_table.columns[1:])
    return BalanceSheet_table

def cash_flow(driver, ticker):
    '''Extract the cash flow table from the webpage.'''
    time.sleep(0.2)
    wait = WebDriverWait(driver, 10)
    retries = 1
    max_retries = 100
    x = 0         # variable to check if the button is pressed
    while x == 0 and retries < max_retries:
        try:
            operating_cash_flow_button = driver.find_elements(By.XPATH, "//section[contains(@id,'cash-flow')]//button[contains(text(), 'Cash from Operating Activity')]")
            if operating_cash_flow_button:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//section[contains(@id,'cash-flow')]//button[contains(text(), 'Cash from Operating Activity')]")))
                button.click()
                OperatingCashFlow_minus = wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@id,'cash-flow')]//button[contains(text(), 'Cash from Operating Activity')]//span[contains(text(), '-')]")))

            investing_cash_flow_button = driver.find_elements(By.XPATH, "//section[contains(@id,'cash-flow')]//button[contains(text(), 'Cash from Investing Activity')]")
            if investing_cash_flow_button:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//section[contains(@id,'cash-flow')]//button[contains(text(), 'Cash from Investing Activity')]")))
                button.click()
                InvestingCashFlow_minus = wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@id,'cash-flow')]//button[contains(text(), 'Cash from Investing Activity')]//span[contains(text(), '-')]")))

            financing_cash_flow_button = driver.find_elements(By.XPATH, "//section[contains(@id,'cash-flow')]//button[contains(text(), 'Cash from Financing Activity')]")
            if financing_cash_flow_button:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//section[contains(@id,'cash-flow')]//button[contains(text(), 'Cash from Financing Activity')]")))
                button.click()
                FinancingCashFlow_minus = wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@id,'cash-flow')]//button[contains(text(), 'Cash from Financing Activity')]//span[contains(text(), '-')]")))

            if (not operating_cash_flow_button or OperatingCashFlow_minus.is_displayed()) and (not investing_cash_flow_button or InvestingCashFlow_minus.is_displayed()) and (not financing_cash_flow_button or FinancingCashFlow_minus.is_displayed()):
                x = 1  # If the element is found, break the loop
        except Exception as e:
            print(f"Not all buttons clicked in cash flow table of {ticker}. Retry... ({retries + 1}/{max_retries})")
            #print(f"Error: {e}")
            # Dynamically adjust wait if multiple retries fail
            dynamic_wait = min(retries * 0.2, 5)  # Wait up to 5 seconds max if too many retries
            print(f"Waiting dynamically for {dynamic_wait} seconds before retry...")
            time.sleep(dynamic_wait)
            
            driver.refresh()
            retries += 1
            #time.sleep(5)  # Wait for 5 seconds before retrying

    if x == 0:
        print("Failed to click all buttons in cash flow table after multiple retries.")
        with open("error_button_not_pressed.txt", "a") as f:
            f.write(f"Ticker: {ticker} - Failed to click all buttons in cash flow table\n")
        print(f"Added {ticker} to error_button_not_pressed.txt")
        return None

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find_all('section', {'id': 'cash-flow'})
    CashFlow_table = pd.read_html(str(table))[0]
    CashFlow_table.columns = ["Year"] + list(CashFlow_table.columns[1:])
    return CashFlow_table

def insert_or_update_into_mongodb(ticker, tables, collection):
    '''function takes a ticker symbol, a dictionary of DataFrames, and a MongoDB collection, converts the DataFrames to JSON, combines them into a single dictionary, and inserts this dictionary into the MongoDB collection.'''
    combined_data = {"_id": ticker}
    for table_name, table in tables.items():
        json_table = table.to_json(orient='columns')
        #print(f"{table_name} JSON:\n{json_table}\n")
        # Convert JSON string to dictionary
        json_data = json.loads(json_table)
        combined_data[table_name] = json_data
    # Check if the ticker exists in the MongoDB collection
    if collection.find_one({"_id": ticker}) is None:
        # If not, create a new document for the ticker
        try:
            collection.insert_one(combined_data)
            print(f"Inserted all 3 tables data for {ticker} into MongoDB")
        except Exception as e:
            print(f"An error occurred while inserting data for {ticker}: {e} in insert_or_update_into_mongodb method")
    else:
        # If the ticker already exists, update the document
        try:
            collection.update_one({"_id": ticker}, {"$set": combined_data})
            print(f"Updated all 3 tables data for {ticker} in MongoDB")
        except Exception as e:
            print(f"An error occurred while updating data for {ticker}: {e} in insert_or_update_into_mongodb method")

def display_sql(ticker, cur):
    '''Display stock information from the SQLite database.'''
    ticker = ticker.rstrip()
    cur.execute("SELECT * FROM Info WHERE Symbol=?",(ticker,))
    row = cur.fetchone()
    if row is not None:
        print(f"Data for {ticker} in SQLite:")
        print("Symbol:                ", row[0])
        print("Market Cap:            ", row[1])
        print("Current Price:         ", row[2])
        print("High:                  ", row[3])
        print("Low:                   ", row[4])
        print("Stock P/E:             ", row[5])
        print("Book Value:            ", row[6])
        print("Dividend Yield:        ", row[7])
        print("ROCE:                  ", row[8])
        print("ROE:                   ", row[9])
        print("Face Value:            ", row[10])
        print("Sector:                ", row[11])
        print("Industry:              ", row[12])
        print("TenYrs_SalesGrowth:    ", row[13])
        print("FiveYrs_SalesGrowth:   ", row[14])
        print("ThreeYrs_SalesGrowth:  ", row[15])
        print("ttm_SalesGrowth:       ", row[16])
        print("TenYrs_ProfitGrowth:   ", row[17])
        print("FiveYrs_ProfitGrowth:  ", row[18])
        print("ThreeYrs_ProfitGrowth: ", row[19])
        print("ttm_ProfitGrowth:      ", row[20])
        print("TenYrs_CAGR:           ", row[21])
        print("FiveYrs_CAGR:          ", row[22])
        print("ThreeYrs_CAGR:         ", row[23])
        print("ttm_CAGR:              ", row[24])
        print("TenYrs_ROE:            ", row[25])
        print("FiveYrs_ROE:           ", row[26])
        print("ThreeYrs_ROE:          ", row[27])
        print("ttm_ROE:               ", row[28])
        print("Intrinsic Value:       ", row[29])
        #print("++++++++++++++++++")
    else:
        print(f"No data found for {ticker} in SQLite")

def display_mongodb(ticker, collection):
    '''Display stock information from the MongoDB collection.'''
    ticker = ticker.rstrip()                       # Remove any trailing whitespace   
    result = collection.find_one({"_id": ticker})
    if result is not None:
        print(f"Data for {ticker} in MongoDB:")
        for key, value in result.items():
            if key != "_id":
                print(f"{key} of {ticker}:")
                json_data = json.dumps(value, indent=4)
                table_json = pd.read_json(StringIO(json_data))
                print(table_json.to_string(), "\n")
    else:
        print(f"No data found for {ticker} in MongoDB")

def logic(ticker, conn, cur, collection):
    '''Main logic function to fetch and store stock information.'''
    ticker = ticker.rstrip()
    in_database = is_ticker_in_sql_database(ticker, cur)
    in_mongodb = is_ticker_in_mongodb(ticker, collection)
    
    if not in_database or not in_mongodb:
        driver = setup_driver()
        try:
            if not in_database:
                current_price, market_cap, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry, growth_metrics = load_and_extract_stock_info(driver, ticker)
                try:
                    Intrinsic_Value_Per_Share = findIntrinsicValue(ticker)
                except:
                    Intrinsic_Value_Per_Share = -999999999
                insert_or_update_into_sql(ticker, market_cap, current_price, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry, growth_metrics, Intrinsic_Value_Per_Share, conn, cur)
            if not in_mongodb:
                current_price, market_cap, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry, growth_metrics = load_and_extract_stock_info(driver, ticker)
                ProfitLoss_table = profit_loss(driver, ticker)
                BalanceSheet_table = balance_sheet(driver, ticker)
                CashFlow_table = cash_flow(driver, ticker)
                # insert tables into MongoDB
                insert_or_update_into_mongodb(ticker, {"ProfitLoss": ProfitLoss_table, "BalanceSheet": BalanceSheet_table, "CashFlow": CashFlow_table}, collection)
            return True

        except Exception as e:
            print(f"An error occurred while fetching data(in logic fn) for {ticker}: {e}") 
            with open("black_list.txt", "r+") as black_list:
                black_list_content = black_list.read()
                if ticker not in black_list_content:
                    black_list.write(ticker + "\n")
                    print(f"Added {ticker} to the black_list.txt")
                else:
                    print(f"{ticker} is already in the black_list.txt") 
            return False
        finally:    
            #time.sleep(3)
            driver.quit()
    else:
        print(f"{ticker} is already present in both SQLite and MongoDB.")
    
    #time.sleep(3)
    #driver.quit()
    return True

def getStockInfo(arg):
    '''Main function to fetch and store stock information.'''
    try:
        conn, cur, cluster, collection = setup_databases()
    except Exception as e:
        print(f"An error occurred while setting up databases: {e}")
        return
    
    try:
        if isinstance(arg, str):
            logic(arg, conn, cur, collection)
            #display_sql(arg, cur)
            #display_mongodb(arg, collection)
            #findIntrinsicValue(arg)
        
        if isinstance(arg, io.TextIOBase):
            try:
                for ticker in arg:
                    logic(ticker, conn, cur, collection)
                    #display_sql(ticker, cur)
                    #display_mongodb(ticker, collection)
                    #findIntrinsicValue(ticker)
            except KeyboardInterrupt:
                print("\nProcess interrupted by user. Exiting...")
                return
    except Exception as e:
        print(f"An error occurred while fetching data: {e} in getStockInfo method")
    finally:    
        conn.close()
        cluster.close()

def logic_update_sql(ticker, conn, cur, collection):
    # used in update_sql_database
    # Get latest fundamental data and update into SQL
    ticker = ticker.rstrip()
    try:
        driver = setup_driver()
        current_price, market_cap, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry, growth_metrics = load_and_extract_stock_info(driver, ticker)
        try:
            Intrinsic_Value_Per_Share = findIntrinsicValue(ticker)
        except:
            Intrinsic_Value_Per_Share = -999999999
        #print("hi")
        insert_or_update_into_sql(ticker, market_cap, current_price, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry, growth_metrics, Intrinsic_Value_Per_Share, conn, cur)
    
    except Exception as e:
        print(f"An error occurred while fetching data(in logic_update fn) for {ticker}: {e}")
        with open("black_list.txt", "r+") as black_list:
            black_list_content = black_list.read()
            if ticker not in black_list_content:
                black_list.write(ticker + "\n")
                print(f"Added {ticker} to the black_list.txt")
            else:
                print(f"{ticker} is already in the black_list.txt")
    finally:
        #time.sleep(3)
        driver.quit()
    #time.sleep(3)
    #driver.quit()
    return
def update_sql_database(arg):
    # update latest scraped fundamental data into sql database
    try:
        conn, cur, cluster, collection = setup_databases()
    except Exception as e:
        print(f"An error occurred while setting up databases: {e} in update_sql_database method")
        return
    
    try:
        if isinstance(arg, str):
            # get data for database and update if already exists if not insert
            logic_update_sql(arg, conn, cur, collection)
            #display_sql(arg, cur)
        
        if isinstance(arg, io.TextIOBase):
            try:
                for ticker in arg:
                    logic_update_sql(ticker, conn, cur, collection)
                    #display_sql(ticker, cur)
            except KeyboardInterrupt:
                print("\nProcess interrupted by user. Exiting...")
                return
    except Exception as e:
        print(f"An error occurred while fetching data: {e} in update_sql_database method")
    finally: 
        conn.close()
        cluster.close()

def logic_update_mongodb(ticker, conn, cur, collection):    
    # used in update_mongodb
    # Get all 3 tables from screener and insert into MongoDB
    ticker = ticker.rstrip()
    try:
        driver = setup_driver()
        current_price, market_cap, high, low, stock_pe, book_value, dividend_yield, roce, roe, face_value, sector, industry, growth_metrics = load_and_extract_stock_info(driver, ticker)
        ProfitLoss_table = profit_loss(driver, ticker)
        BalanceSheet_table = balance_sheet(driver, ticker)
        CashFlow_table = cash_flow(driver, ticker)
        # insert tables into MongoDB
        insert_or_update_into_mongodb(ticker, {"ProfitLoss": ProfitLoss_table, "BalanceSheet": BalanceSheet_table, "CashFlow": CashFlow_table}, collection)
    except Exception as e:
        print(f"An error occurred while fetching data(in logic_update fn) for {ticker}: {e}")
        with open("black_list.txt", "r+") as black_list:
            black_list_content = black_list.read()
            if ticker not in black_list_content:
                black_list.write(ticker + "\n")
                print(f"Added {ticker} to the black_list.txt")
            else:
                print(f"{ticker} is already in the black_list.txt") 
    finally:    
        #time.sleep(3)
        driver.quit()
    #time.sleep(3)
    #driver.quit()
    return
def update_mongodb(arg):
    # update latest scraped tables: ProfitLoss, BalanceSheet, CashFlow into MongoDB
    try:
        conn, cur, cluster, collection = setup_databases()
    except Exception as e:
        print(f"An error occurred while setting up databases: {e} in update_mongodb method")
        return
    
    try:
        if isinstance(arg, str):
            logic_update_mongodb(arg, conn, cur, collection)
            #display_mongodb(arg, collection)
        
        if isinstance(arg, io.TextIOBase):
            try:
                for ticker in arg:
                    logic_update_mongodb(ticker, conn, cur, collection)
                    #display_mongodb(ticker, collection)
            except KeyboardInterrupt:
                print("\nProcess interrupted by user. Exiting...")
                return
    except Exception as e:
        print(f"An error occurred while fetching data: {e} in update_mongodb method")
        return
    finally:   
        conn.close()
        cluster.close()

def check_and_update_file():
    nse_symbols = nse_eq_symbols()
    existing_symbols = set()
    blacklist = set()
    
    try:
        with open("nse_companies_symbols.txt", "r") as file:
            existing_symbols = set(line.strip() for line in file)
    except FileNotFoundError:
        print("nse_companies_symbols.txt not found. Creating it.")
        with open("nse_companies_symbols.txt", "w") as file:
            pass
    
    try:
        with open("black_list.txt", "r") as file:
            blacklist = set(line.strip() for line in file)
    except FileNotFoundError:
        print("black_list.txt not found. Creating it.")
        with open("black_list.txt", "w") as file:
            pass
    
    new_symbols = set(nse_symbols) - existing_symbols - blacklist
    
    if new_symbols:
        conn, cur, cluster, collection = setup_databases()
        added_symbols = 0
        try:
            with open("nse_companies_symbols.txt", "a") as file:
                for symbol in new_symbols:
                    try:
                        if logic(symbol, conn, cur, collection):
                            file.write(symbol + "\n")
                            added_symbols += 1
                            print(f"Added {symbol} to nse_companies_symbols.txt and inserted into databases.")                        
                        else:
                            print(f"Failed to add {symbol} to nse_companies_symbols.txt and databases.")
                            with open("black_list.txt", "r+") as black_list:
                                black_list_content = black_list.read()
                                if symbol not in black_list_content:
                                    black_list.write(symbol + "\n")
                                    print(f"Added {symbol} to the black_list.txt")
                                else:
                                    print(f"{symbol} is already in the black_list.txt") 
                    except Exception as e:
                        print(f"An error occurred while fetching data(in update_nse_symbols fn) for {symbol}: {e}")
                        with open("black_list.txt", "r+") as black_list:
                            black_list_content = black_list.read()
                            if symbol not in black_list_content:
                                black_list.write(symbol + "\n")
                                print(f"Added {symbol} to the black_list.txt")
                            else:
                                print(f"{symbol} is already in the black_list.txt") 
            if added_symbols == len(new_symbols):
                print(f"Added {added_symbols} new symbols to nse_companies_symbols.txt and inserted into databases.")
            else:
                print(f"Added {added_symbols} out of {len(new_symbols)} new symbols to nse_companies_symbols.txt and inserted into databases.")
        finally:
            conn.close()
            cluster.close()
    
    else:
        print("No new symbols found. File is up-to-date.")
    # Explicitly clear new_symbols before function ends (optional)
    new_symbols = set()

def display(arg) :
    conn, cur, cluster, collection = setup_databases()
    
    if isinstance(arg, str):
        display_sql(arg, cur)
        display_mongodb(arg, collection)
    
    if isinstance(arg, io.TextIOBase):
        try:
            for ticker in arg:
                display_sql(ticker, cur)
                display_mongodb(ticker, collection)
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting...")
            return
    
    conn.close()
    cluster.close()  

#def add_intrinsic_value_column(cur, conn):
#    try:
#        cur.execute('''
#            ALTER TABLE Info
#            ADD COLUMN Intrinsic_Value_Per_Share REAL
#        ''')
#        conn.commit()
#        print("Intrinsic_Value_Per_Share column added successfully.")
#    except sqlite3.OperationalError as e:
#        if "duplicate column name" in str(e):
#            print("Column already exists.")
#        else:
#            print(f"An error occurred: {e}")

def logic_intrinsic_value(cur, conn, symbol, new_intrinsic_value):
    try:
        symbol = symbol.rstrip()        # not rstrip whole stripe reight and left
        cur.execute('''
            UPDATE Info
            SET Intrinsic_Value_Per_Share = ?
            WHERE Symbol = ?
        ''', (new_intrinsic_value, symbol))
        conn.commit()
        print(f"Updated Intrinsic_Value_Per_Share for {symbol} to {new_intrinsic_value}")
    except Exception as e:
        print(f"An error occurred: {e}")
def update_intrinsic_value(arg):
    conn, cur, cluster, collection = setup_databases()
    
    if isinstance(arg, str):
        logic_intrinsic_value(cur, conn, arg, findIntrinsicValue(arg))
    
    if isinstance(arg, io.TextIOBase):
        try:
            for ticker in arg:
                logic_intrinsic_value(cur, conn, ticker, findIntrinsicValue(ticker))
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting...")
            return
    
    conn.close()
    cluster.close()

# files used: black_list.txt, error_button_not_pressed.txt, nse_companies_symbols.txt
    """
Function:
1. Database Functions:
    insert_or_update_into_sql: Inserts or updates stock information in the SQLite database.
    insert_or_update_into_mongodb: Converts DataFrames to JSON and inserts or updates the combined JSON data into a MongoDB collection.
    display_sql: Displays stock information from the SQLite database.
    display_mongodb: Displays stock information from the MongoDB collection.
    logic_intrinsic_value: Updates the intrinsic value of a stock in the SQLite database.
    update_intrinsic_value: Updates the intrinsic value for a given ticker symbol or a file containing multiple ticker symbols.
2. Web Scraping Functions:
    setup_driver: Sets up the Selenium WebDriver.
    page_check: Loads a webpage and returns its HTML source, handling errors like "404" and "Too many requests".
    extract_stock_info: Extracts stock information from the parsed HTML. Functions used: findCurrentprice, findMarketCap, findHighLow, StockPE, BookValue, DividendYield, ROCE, ROE, FaceValue, industry_sector, extract_growth_metrics.
    load_and_extract_stock_info: Loads the webpage and extracts stock information, retrying with an alternative URL if necessary.
    profit_loss: Extracts the profit and loss table from the webpage.
    balance_sheet: Extracts the balance sheet table from the webpage.
    cash_flow: Extracts the cash flow table from the webpage.
3. Main Logic Functions:
    logic: The main function to fetch and store stock information. It checks if the ticker symbol is already present in the databases and fetches the data from the web if not. It inserts the data into the SQLite database and MongoDB collection as needed.
    logic_update_sql: Fetches the latest fundamental data and updates it in the SQLite database.
    logic_update_mongodb: Fetches the latest financial tables and updates them in the MongoDB collection.
4. Main Functions:
    getStockInfo: The main function to fetch and store stock information for a given ticker symbol or a file containing multiple ticker symbols. It connects to the databases, calls the logic function for each ticker symbol, and closes the database connections.
    update_sql_database: Updates the latest scraped fundamental data in the SQLite database.
    update_mongodb: Updates the latest scraped financial tables in the MongoDB collection.
    check_and_update_file: Checks for new stock symbols, updates the `nse_companies_symbols.txt` file, and inserts new symbols into the databases.
    display: Displays stock information from both the SQLite database and MongoDB collection for a given ticker symbol or a file containing multiple ticker symbols.
"""
