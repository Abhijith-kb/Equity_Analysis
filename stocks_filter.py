# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stocks_filter.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import sqlite3
import sys
signs = ["<", ">", "="]
sector_industry = {
    'Mining & Mineral products': ['Mining / Minerals / Metals'], 'Finance': ['Finance & Investments', 'Finance - Housing', 'Finance - Term-Lending Institutions'], 'IT - Software': ['Computers - Software - Medium / Small', 'Computers - Software - Large', 'Computers - Education'], 'Diversified': ['Diversified - Large', 'Diversified - Medium / Small', 'Diversified - Mega'], 'Stock/ Commodity Brokers': ['Finance & Investments'], 'Infrastructure Developers & Operators': ['Engineering - Turnkey Services', 'Construction', 'Transmisson Line Towers / Equipment', 'Miscellaneous'], 'Oil Drill/Allied': ['Oil Drilling / Allied Services'], 'Pharmaceuticals': ['Pharmaceuticals - Indian - Bulk Drugs', 'Pharmaceuticals - Indian - Bulk Drugs & Formln', 'Pharmaceuticals - Multinational', 'Pharmaceuticals - Indian - Formulations', 'Miscellaneous'], 'Capital Goods-Non Electrical Equipment': ['Engineering', 'Electrodes - Welding Equipment', 'Abrasives And Grinding Wheels', 'Engines', 'Compressors / Drilling Equipment', 'Electrodes - Graphites', 'Pumps', 'Electric Equipment'], 'Capital Goods - Electrical Equipment': ['Electric Equipment', 'Transmisson Line Towers / Equipment'], 'Chemicals': ['Chemicals', 'Dyes And Pigments', 'Chlor Alkali / Soda Ash', 'Miscellaneous'], 'Textiles': ['Textiles - Cotton/Blended', 'Textiles - Processing', 'Textiles - Products', 'Textiles - Spinning - Synthetic / Blended', 'Textiles - Manmade', 'Textiles - Jute - Yarn / Products', 'Textiles - Composite'], 'Miscellaneous': ['Miscellaneous', 'Aquaculture', 'Recreation / Amusement Parks', 'Travel Agencies', 'Food - Processing - Indian', 'Photographic And Allied Products'], 'Crude Oil & Natural Gas': ['Oil Drilling / Allied Services'], 'Alcoholic Beverages': ['Breweries & Distilleries'], 'Retail': ['Textiles - Products', 'Trading', 'Miscellaneous'], 'Trading': ['Trading'], 'Paper': ['Paper'], 'Cement': ['Cement - North India', 'Cement - South India'], 'Logistics': ['Miscellaneous', 'Couriers', 'Transport - Airlines'], 'Power Generation & Distribution': ['Power Generation And Supply'], 'Marine Port & Services': ['Miscellaneous'], 'FMCG': ['Food - Processing - Indian', 'Miscellaneous', 'Personal Care - Indian', 'Food - Processing - MNC', 'Personal Care - Multinational', 'Diversified - Large'], 'Plywood Boards/Laminates': ['Miscellaneous'], 'Hotels & Restaurants': ['Hotels'], 'Steel': ['Steel - Medium / Small', 'Steel - Large', 'Steel - Sponge Iron'], 'Engineering': ['Engineering', 'Textile Machinery'], 'Petrochemicals': ['Petrochemicals'], 'Packaging': ['Packaging'], 'Realty': ['Construction', 'Miscellaneous'], 'Fertilizers': ['Fertilizers'], 'IT - Hardware': ['Computers - Hardware'], 'Castings, Forgings & Fastners': ['Castings & Forgings', 'Fasteners'], 'Leather': ['Leather / Leather Products'], 'Cables': ['Cables - Telephone', 'Cables - Power'], 'Paints/Varnish': ['Paints / Varnishes'], 'Consumer Durables': ['Electronics - Components', 'Miscellaneous', 'Cycles And Accessories', 'Domestic Appliances', 'Air-conditioners', 'Ceramics - Tiles / Sanitaryware', 'Electric Equipment', 'Electronics - Consumer'], 'Aerospace & Defence': ['Electronics - Components', 'Telecommunications - Equipment', 'Engineering', 'Miscellaneous', 'Steel - Medium / Small', 'Chemicals'], 'Healthcare': ['Healthcare', 'Miscellaneous'], 'Plastic products': ['Plastics Products', 'Moulded Luggage'], 'Tyres': ['Tyres'], 'Computer Education': ['Computers - Education'], 'Auto Ancillaries': ['Auto Ancillaries'], 'Construction': ['Construction'], 'Glass & Glass Products': ['Glass & Glass Products'], 'Automobile': ['Automobiles - LCVs / HCVs', 'Automobiles - Scooters And 3 - Wheelers', 'Automobiles - Motorcycles / Mopeds', 'Automobiles - Tractors', 'Automobiles - Passenger Cars'], 'Ceramic Products': ['Ceramics - Tiles / Sanitaryware'], 'Agro Chemicals': ['Pesticides / Agrochemicals - Indian', 'Pesticides / Agrochemicals - Multinational'], 'Gas Distribution': ['Miscellaneous'], 'Banks': ['Banks - Private Sector', 'Banks - Public Sector'], 'Sugar': ['Sugar'], 'Edible Oil': ['Solvent Extraction'], 'Entertainment': ['Entertainment / Electronic Media Software', 'Recreation / Amusement Parks', 'Miscellaneous'], 'Quick Service Restaurant': ['Hotels'], 'Telecomm-Service': ['Telecommunications - Service Provider'], 'Cement - Products': ['Cement Products'], 'Refineries': ['Refineries'], 'Financial Services': ['Miscellaneous'], 'Education': ['Miscellaneous', 'Computers - Education'], 'Credit Rating Agencies': ['Miscellaneous'], 'Plantation & Plantation Products': ['Tea', 'Miscellaneous'], 'Non Ferrous Metals': ['Aluminium and Aluminium Products', 'Mining / Minerals / Metals'], 'Electronics': ['Electronics - Components'], 'E-Commerce/App based Aggregator': ['Trading', 'Travel Agencies', 'Miscellaneous'], 'Media - Print/Television/Radio': ['Entertainment / Electronic Media Software'], 'Readymade Garments/ Apparells': ['Textiles - Products'], 'Printing & Stationery': ['Printing & Stationery'], 'Diamond, Gems and Jewellery': ['Diamond Cutting / Jewellery'], 'Shipping': ['Shipping'], 'Dry cells': ['Dry Cells'], 'Insurance': ['Finance & Investments', 'Miscellaneous'], 'Air Transport Service': ['Transport - Airlines'], 'Tobacco Products': ['Cigarettes'], 'Telecomm Equipment & Infra Services': ['Telecommunications - Equipment', 'Engineering - Turnkey Services', 'Transmisson Line Towers / Equipment', 'Telecommunications - Service Provider'], 'Refractories': ['Refractories / Intermediates'], 'Ferro Alloys': ['Mining / Minerals / Metals'], 'Railways': ['Travel Agencies'], 'Ship Building': ['Miscellaneous'], 'Power Infrastructure': ['Construction'], 'Bearings': ['Bearings']
}
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(3000, 1520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 3000, 600))
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        # labels
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(100, 100, 350, 100))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(100, 250, 350, 100))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(1800, 50, 300, 100))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(100, 400, 350, 100))
        self.label_4.setObjectName("label_4")
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(1800, 400, 300, 100))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(1800, 175, 300, 100))
        self.label_7.setObjectName("label_7")
        
        # comboBox: market_cap_sign, current_price_sign, roce_sign, sector_input, industry_input, dcf_sign
        self.market_cap_sign = QtWidgets.QComboBox(self.groupBox)
        self.market_cap_sign.setGeometry(QtCore.QRect(450, 125, 100, 50))
        self.market_cap_sign.setObjectName("market_cap_sign")
        self.current_price_sign = QtWidgets.QComboBox(self.groupBox)
        self.current_price_sign.setGeometry(QtCore.QRect(450, 275, 100, 50))
        self.current_price_sign.setObjectName("current_price_sign")
        self.sector_input = QtWidgets.QComboBox(self.groupBox)
        self.sector_input.setGeometry(QtCore.QRect(450, 425, 500, 100))
        self.sector_input.setObjectName("sector_input")
        self.roce_sign = QtWidgets.QComboBox(self.groupBox)
        self.roce_sign.setGeometry(QtCore.QRect(2100, 65, 100, 50))
        self.roce_sign.setObjectName("roce_sign")
        self.roe_sign = QtWidgets.QComboBox(self.groupBox)
        self.roe_sign.setGeometry(QtCore.QRect(2100, 190, 100, 50))
        self.roe_sign.setObjectName("roe_sign")        
        self.industry_input = QtWidgets.QComboBox(self.groupBox)
        self.industry_input.setGeometry(QtCore.QRect(2100, 425, 400, 100))
        self.industry_input.setObjectName("industry_input")
        self.dcf_sign = QtWidgets.QCheckBox(self.groupBox)
        self.dcf_sign.setGeometry(QtCore.QRect(1800, 250, 700, 150))
        self.dcf_sign.setObjectName("dcf_sign")
        
        # lineEdit: market_cap_value, current_price_value, roce_value
        self.market_cap_value = QtWidgets.QLineEdit(self.groupBox)
        self.market_cap_value.setGeometry(QtCore.QRect(650, 115, 400, 100))
        self.market_cap_value.setObjectName("market_cap_value")
        self.current_price_value = QtWidgets.QLineEdit(self.groupBox)
        self.current_price_value.setGeometry(QtCore.QRect(650, 250, 400, 100))
        self.current_price_value.setObjectName("current_price_value")
        self.roce_value = QtWidgets.QLineEdit(self.groupBox)
        self.roce_value.setGeometry(QtCore.QRect(2300, 50, 400, 100))
        self.roce_value.setObjectName("roce_value")
        self.roe_value = QtWidgets.QLineEdit(self.groupBox)
        self.roe_value.setGeometry(QtCore.QRect(2300, 175, 400, 100))
        self.roe_value.setObjectName("roe_value")
        
        # pushButton: submit
        self.submit = QtWidgets.QPushButton(self.centralwidget)
        self.submit.setGeometry(QtCore.QRect(600, 600, 500, 100))
        font = QtGui.QFont()
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.submit.setFont(font)
        self.submit.setObjectName("submit")
        
        # tableWidget: output_table : add columns all 13 or 14
        self.output_table = QtWidgets.QTableWidget(self.centralwidget)
        self.output_table.setGeometry(QtCore.QRect(0, 700, 3000, 800))
        font = QtGui.QFont()
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.output_table.setFont(font)
        self.output_table.setObjectName("output_table")
        # this setup_table() method will add columns and headers
        self.setup_table()
        
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 3000, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # comboBox: market_cap_sign, current_price_sign, sector_input, industry_input, dcf_sign, roce_sign
        # lineEdit: market_cap_value, current_price_value, roce_value
        # pushButton: submit
        # checkBox: dcf_sign
        self.populate_sign()
        self.populate_sec_ind_combo()
        
        self.submit.clicked.connect(self.filter_companies)
    def setup_table(self):
        """Method to add columns and headers."""
        column_headers = [
            "Symbol", "Market_cap", "Current_price", "Intrinsic_value_per_share",
            "High", "Low", "Stock_PE", "Book_value",
            "Dividend_yield", "ROCE", "ROE", "Face_value",
            "Sector", "Industry"
        ]
        
        column_count = len(column_headers)  # Dynamically set column count
        self.output_table.setColumnCount(column_count) 
        self.output_table.setRowCount(0)
        self.output_table.setHorizontalHeaderLabels(column_headers)
        
        # Automatically resize all columns to fit contents
        header = self.output_table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        
        # Ensure columns expand when needed (optional)
        # header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        # If you want only some columns to stretch:
        # header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)  # Symbol column expands

    def populate_sign(self):
        for sign in signs:
            self.market_cap_sign.addItem(sign)
            self.current_price_sign.addItem(sign)
            self.roce_sign.addItem(sign)
            self.roe_sign.addItem(sign)
        self.market_cap_sign.setCurrentIndex(1)
        self.current_price_sign.setCurrentIndex(1)
        self.roce_sign.setCurrentIndex(1)
        self.roe_sign.setCurrentIndex(1)
    
    def populate_sec_ind_combo(self):
        self.sector_input.addItem("All")
        for sector in sector_industry.keys():
            self.sector_input.addItem(sector)
        self.sector_input.setCurrentIndex(1)
        self.sector_input.currentIndexChanged.connect(self.update_industry_input)
    def update_industry_input(self, index):
        sector = self.sector_input.itemText(index)
        industries = sector_industry.get(sector, [])
        self.industry_input.clear()
        self.industry_input.addItems(["All"]+industries)
        self.industry_input.setCurrentIndex(0)
    
    def filter_companies(self):
        market_cap = convert_to_float(self.market_cap_value.text())
        current_price = convert_to_float(self.current_price_value.text())
        roce = convert_to_float(self.roce_value.text())
        roe = convert_to_float(self.roe_value.text())
        
        sign_market_cap = self.market_cap_sign.currentText()
        sign_current_price = self.current_price_sign.currentText()
        sign_roce = self.roce_sign.currentText()
        sign_roe = self.roe_sign.currentText()        
        sector = self.sector_input.currentText()
        industry = self.industry_input.currentText()
        
        dcf_tick = self.dcf_sign.isChecked()
        
        query = "SELECT Symbol, ROUND(Market_cap,2), ROUND(Current_price,2), ROUND(Intrinsic_Value_Per_Share,2), ROUND(High,2), ROUND(Low,2), ROUND(Stock_PE,2), ROUND(Book_Value,2), ROUND(Dividend_Yield,2), ROUND(ROCE,2), ROUND(ROE,2), ROUND(Face_Value,2), Sector, Industry FROM Info WHERE 1=1"
        params = []
        
        if market_cap is not None:
            query += f" AND Market_cap {sign_market_cap} ?"
            params.append(market_cap)
        if current_price is not None:
            query += f" AND Current_price {sign_current_price} ?"
            params.append(current_price)
        if roce is not None:
            query += f" AND ROCE {sign_roce} ?"
            params.append(roce)
        if roe is not None:
            query += f" AND ROE {sign_roe} ?"
            params.append(roe)
        if sector != "All":
            query += " AND Sector == ?"
            params.append(sector)   
        if industry != "All":
            query += " AND Industry == ?"
            params.append(industry)
        if dcf_tick:
            query += " AND Intrinsic_Value_Per_Share > Current_price"

        conn = sqlite3.connect("stockdb1.sqlite")
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        conn.close()
        
        self.output_table.setRowCount(len(results))
        for i, result in enumerate(results):
            for j, value in enumerate(result):
                item = QtWidgets.QTableWidgetItem(str(value))
                self.output_table.setItem(i, j, item)
        
        #row = 0 
        #self.OUTPUT_TABLE.setRowCount(len(results))
        #for result in results:
        #    self.OUTPUT_TABLE.setItem(row,0,QtWidgets.QTableWidgetItem(str(result[0])))
        #    self.OUTPUT_TABLE.setItem(row,1,QtWidgets.QTableWidgetItem(str(result[1])))
        #    self.OUTPUT_TABLE.setItem(row,2,QtWidgets.QTableWidgetItem(str(result[2])))
        #    self.OUTPUT_TABLE.setItem(row,3,QtWidgets.QTableWidgetItem(str(result[3])))
        #    self.OUTPUT_TABLE.setItem(row,4,QtWidgets.QTableWidgetItem(str(result[4])))
        #    self.OUTPUT_TABLE.setItem(row,5,QtWidgets.QTableWidgetItem(str(result[5])))
        #    self.OUTPUT_TABLE.setItem(row,6,QtWidgets.QTableWidgetItem(str(result[6])))
        #    self.OUTPUT_TABLE.setItem(row,7,QtWidgets.QTableWidgetItem(str(result[7])))
        #    self.OUTPUT_TABLE.setItem(row,8,QtWidgets.QTableWidgetItem(str(result[8])))
        #    self.OUTPUT_TABLE.setItem(row,9,QtWidgets.QTableWidgetItem(str(result[9])))
        #    self.OUTPUT_TABLE.setItem(row,10,QtWidgets.QTableWidgetItem(str(result[10])))
        #    self.OUTPUT_TABLE.setItem(row,11,QtWidgets.QTableWidgetItem(str(result[11])))
        #    self.OUTPUT_TABLE.setItem(row,12,QtWidgets.QTableWidgetItem(str(result[12])))
        #    row += 1
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "Filter stocks by Market Cap, Price, ROCE (>, <, =), Sector & Industry. Check DCF to show undervalued stocks (DCF > Price)."))
        self.label.setText(_translate("MainWindow", "Market Capitalization"))
        self.label_2.setText(_translate("MainWindow", "Current Price"))
        self.label_3.setText(_translate("MainWindow", "ROCE"))
        self.label_4.setText(_translate("MainWindow", "Sector"))
        self.label_6.setText(_translate("MainWindow", "Industry"))
        self.label_7.setText(_translate("MainWindow", "ROE"))
        self.dcf_sign.setText(_translate("MainWindow", "Show only undervalued companies"))
        self.submit.setText(_translate("MainWindow", "Submit"))

def convert_to_float(value):
    if value is None or value.strip() == "":
        return None
    # if value is not float or integer like string or other
    if value is str: raise ValueError("Invalid input string.")
    
    try:
        # Remove commas from the string and then converts to float
        value = value.replace(",", "")
        return float(value)
    except ValueError:
        raise ValueError("Invalid input string.")

def display(mar_cap, cur_price, roe, dcf, sign_market_cap, sign_current_price, sign_dcf, sign_roe, sector, industry):
    conn = sqlite3.connect('stockdb1.sqlite')
    cur = conn.cursor()
    cur.execute('''SELECT Symbol, Market_cap, Current_price, High, Low, Stock_PE, Book_Value, Dividend_Yield, ROCE, ROE, Sector, Industry, Intrinsic_Value_Per_Share FROM Info WHERE Market_cap {} ? AND Current_price {} ? AND ROE {} ? AND Intrinsic_Value_Per_Share {} ? AND Sector == ? AND Industry == ?'''.format(sign_market_cap, sign_current_price, sign_roe, sign_dcf),(mar_cap, cur_price, roe, dcf, sector, industry))
    result = cur.fetchall()
    #for row in result:
    #    print(row)
    return result
    


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow( )
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
