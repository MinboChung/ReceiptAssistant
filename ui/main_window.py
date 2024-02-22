from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QIcon
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QWidget
import re
import sys
import pandas as pd
from dateutil import parser
from enum import Flag, auto
from core.excel_exporter import ExcelExporter
from datetime import date
import pprint as pp
pp.PrettyPrinter(indent=6)

class MissType(Flag):
    ItemMiss = auto()
    PlaceMiss = auto()
    DateMiss = auto()
    PriceMiss = auto()
    CurrencyMiss = auto()
    VatMiss = auto()

class ReceiptForm(QWidget):
    def __init__(self):
        super().__init__()
        gray_palette = QPalette()
        gray = QColor(128,128,128)
        gray_palette.setColor(QPalette.ColorRole.PlaceholderText, gray)
        # Layout
        self.main_receipt_form = QHBoxLayout(self)
        # Item name
        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("Item name")
        self.item_input.setPalette(gray_palette)   
        # Place bought
        self.place_input = QLineEdit()     
        self.place_input.setPlaceholderText("Place of the market")
        self.place_input.setPalette(gray_palette)   
        # Date of receipt
        self.date_of_receipt_input = QLineEdit()
        self.date_of_receipt_input.setPlaceholderText("Date of receipt: YYYYmmDD")
        self.date_of_receipt_input.setPalette(gray_palette)
        # Price of the item
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        self.price_input.setPalette(gray_palette)
        # Currency unit
        self.currency_input = QComboBox()
        self.currency_input.addItems(['', '€', '₩', '$', '¥ CN', '¥ JP'])
        # VAT
        self.vat_input = QLineEdit()
        self.vat_input.setPlaceholderText("VAT")
        self.vat_input.setPalette(gray_palette)
        # Country
        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("Country: E.g. NL or KR")
        self.country_input.setPalette(gray_palette)
        # Query button
        self.query_button = QPushButton(self)
        icon = QIcon("./assets/download-button.png")
        self.query_button.clicked.connect(self.query_form)
        self.query_button.setIcon(icon)
        
        self.main_receipt_form.addWidget(self.item_input)
        self.main_receipt_form.addWidget(self.place_input)
        self.main_receipt_form.addWidget(self.date_of_receipt_input)
        self.main_receipt_form.addWidget(self.price_input)
        self.main_receipt_form.addWidget(self.currency_input)
        self.main_receipt_form.addWidget(self.vat_input)
        self.main_receipt_form.addWidget(self.country_input)
        self.main_receipt_form.addWidget(self.query_button)

    
    @staticmethod
    def validate_datetime(dt):
        try:
            parsed_dt = parser.parse(dt)
        except ValueError:
            raise ValueError("Invalid date format. Use YYYYmmDD.")

    @staticmethod
    def validate_price_n_vat(vat_val, miss_type):
        flag = MissType.PriceMiss | MissType.VatMiss
        r = r'^\d+(\.\d+)?$'
        res = None
        pattern = re.compile(r)
        if not re.match(pattern, vat_val):
            # raise ValueError("validate_price: input does not meet the requirement")
            res = flag & miss_type
        return res
    @staticmethod
    def validate_item(item):
        res = None
        if not item:
            res = MissType.ItemMiss
        return res
    @staticmethod
    def validate_place(place):
        res = None
        if not place:
            res = MissType.PlaceMiss
        return res

    @staticmethod
    def validate_currency(currency):
        supported_currencies = {"€", "₩", "$", "¥ CN", "¥ JP"}
        if not currency or currency not in supported_currencies:
            raise ValueError("Invalid currency.")

    def query_form(self):
        item = self.item_input.text()
        place = self.place_input.text()
        price = self.price_input.text()
        vat = self.vat_input.text()
        date_of_receipt = self.date_of_receipt_input.text()
        currency = self.currency_input.currentText()
        country = self.country_input.text()

        fields = [
            ("Item", item),
            ("Place", place),
            ("Datetime", date_of_receipt),
            ("Currency", currency)
        ]
        validation_errors = []

        for (field, value) in fields:
            validation_method = getattr(self, f"validate_{field.lower()}")
            error = validation_method(value)
            if error:
                validation_errors.append(value)

        self.validate_price_n_vat(price, MissType.PriceMiss)
        self.validate_price_n_vat(vat, MissType.VatMiss)

        if validation_errors:
            raise AttributeError("\n".join(validation_errors))

        pp.pprint([
            ("Item", item),
            ("Place", place),
            ("Date of receipt", date_of_receipt),
            ("Price", price),
            ("Currency", currency),
            ("VAT", vat),
            ("Country", country)
        ])
        params = {
            'path_folder': './output/',
            'file_name': 'groceries.xlsx',
            'data':pd.DataFrame({
                'Item': [item],
                'Place': [place],
                'Date of receipt': [date_of_receipt],
                'Price': [price],
                'Currency': [currency],
                'VAT':[vat],
                'Country':[country]
            })
        }
        exporter = ExcelExporter(**params)
        exporter.check_folder_and_export_excel()

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # self.setGeometry(100, 100, 580, 600)  # (x, y, width, height)
        self.setWindowTitle("Reciept Assistant")

        # Main layout
        self.main_layout = QVBoxLayout()
        # Title
        self.title_label = QLabel("Receipt Assistant")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title_label)
        # Receipt request form
        self.request_form = ReceiptForm()
        self.main_layout.addWidget(self.request_form)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
          

if __name__=="__main__":
    app = QApplication(sys.argv)

    main_window = MainApp()
    main_window.show()

    sys.exit(app.exec())
