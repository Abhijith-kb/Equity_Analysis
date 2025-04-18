from getStockInfo import getStockInfo, update_sql_database, update_mongodb, check_and_update_file, display, findIntrinsicValue, update_intrinsic_value
import os
import getopt, sys
import time

def process_file(filename, option):
    if not os.path.exists(filename):
        print(f"No file found with name: {filename}")
    fh = open(filename)
    if option == 1:
        getStockInfo(fh)
    elif option == 2:
        update_sql_database(fh)
    elif option == 3:
        update_mongodb(fh)
    elif option == 4:
        display(fh)
    elif option == 5:
        Intrinsic_Value = findIntrinsicValue(fh)
        print(f"check value: {Intrinsic_Value}")
    elif option == 6:
        check_and_update_file()
    elif option == 7:
        update_intrinsic_value(fh)
    else:
        print("Invalid option selected!")

def process_ticker(ticker, option):
    """Process a single ticker based on the selected option."""
    if option == 1:
        getStockInfo(ticker)
    elif option == 2:
        update_sql_database(ticker)
    elif option == 3:
        update_mongodb(ticker)
    elif option == 4:
        display(ticker)
    elif option == 5:
        Intrinsic_Value = findIntrinsicValue(ticker)
        print(f"check value: {Intrinsic_Value}")
    elif option == 6:
        check_and_update_file()
    elif option == 7:
        update_intrinsic_value(ticker)
    else:
        print("Invalid option selected!")

def my_main(argv):
    ticker = None
    filename = None
    
    # Usage message
    def usage():
        print("Usage: script.py -t <ticker> -f <filename> -o <option>")
        print("Options:")
        print("  1: Check ticker presence in database, if not present then inserts data into databases")
        print("  2: Maintainance: Refresh data in SQLite")
        print("  3: Maintainance: Refresh data in MongoDB")
        print("  4: Display all information of the ticker")
        print("  5: To display Intrinsic value of the ticker")
        print("  6: Check and update, if new symbols exists in nse_module then update nse_companies_symbols.txt and insert into database. If any symbol cannot be fetched then it will be written in black_list.txt")
        print("  7: Maintainance: To Update Intrinsic Value of the ticker")
        print("Command example: python screener.py -t INFY -f ZENTEC.txt -o 1 or python screener.py -f tickers.txt -o 6 or python screener.py -o 6")
        sys.exit(2)
    
    # Parse command-line arguments
    try:
        opts, _ = getopt.getopt(argv, "t:f:o:", ["ticker=", "file=", "option="])
    except getopt.GetoptError:
        usage()
    
    option = None
    
    for opt, arg in opts:
        #if opt in ("-t", "--ticker") and opt in ("-f", "--file"):       # if both ticker and file is given
        #    print("Both ticker and file cannot be provided together.")
        #    usage()
        if opt in ("-t", "--ticker"):
            ticker = arg
        elif opt in ("-f", "--file"):
            filename = arg
        elif opt in ("-o", "--option"):
            option = int(arg)
    
    if option is None:
        usage()
    
    # Execute based on input type
    if filename:
        process_file(filename, option)
    elif ticker:
        process_ticker(ticker, option)
    elif option == 6:
        check_and_update_file()
    else:
        print("Ticker or file is required for this option.")
        usage()
    
    # Check if Black_list.txt exists and is not empty
    if os.path.exists("Black_list.txt") and os.path.getsize("Black_list.txt") > 0:
        with open("Black_list.txt", "r") as file:
            lines = file.readlines()
            print(f"Number of tickers in Black_list.txt: {len(lines)}")
            print("These are all tickers which caused error while fetching data")
    
    # Check if error_buttton_not_pressed.txt exists and is not empty
    if os.path.exists("error_buttton_not_pressed.txt") and os.path.getsize("error_buttton_not_pressed.txt") > 0:
        with open("error_buttton_not_pressed.txt", "r") as file:
            lines = file.readlines()
            print(f"Number of tickers in error_buttton_not_pressed.txt: {len(lines)}")
            print("These are all tickers which failed to click all buttons after multiple(100) retries")


if __name__ == '__main__':
    start_time = time.time()    # Record the start time
    my_main(sys.argv[1:])       # Call the main function
    end_time = time.time()      # Record the end time
    print(f"Total time taken to execute the script: {end_time - start_time} seconds")
