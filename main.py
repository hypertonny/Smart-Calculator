import sys
import math
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QMenu, 
                           QAction, QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QTableWidget,
                           QTableWidgetItem, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QKeySequence
from ui_main import Ui_MainWindow
from db_manager import DBManager

class CalculatorApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db = DBManager()
        self.settings = QSettings('Smart-Calculator', 'Calculator')
        self.history = []
        self.undo_stack = []
        self.redo_stack = []
        self.initUI()
        self.current_input = ""
        self.operation = None
        self.first_operand = None
        self.setupHamburgerMenu()
        self.setupKeyboardShortcuts()
        self.loadTheme()
        self.loadHistory()

    def setupHamburgerMenu(self):
        self.menu = QMenu(self)
        
        # Recent Calculations
        history_action = self.menu.addAction("Recent Calculations")
        history_action.triggered.connect(self.showHistory)
        
        # Customer Management
        customer_menu = self.menu.addMenu("Customer Management")
        view_customers = customer_menu.addAction("View Customers")
        view_customers.triggered.connect(self.showCustomers)
        add_customer = customer_menu.addAction("Add Customer")
        add_customer.triggered.connect(self.addCustomer)
        
        # Theme
        theme_menu = self.menu.addMenu("Theme")
        light_theme = theme_menu.addAction("Light")
        light_theme.triggered.connect(lambda: self.setTheme("light"))
        dark_theme = theme_menu.addAction("Dark")
        dark_theme.triggered.connect(lambda: self.setTheme("dark"))
        
        # About
        about_action = self.menu.addAction("About")
        about_action.triggered.connect(self.showAbout)
        
        self.btn_menu.clicked.connect(self.showMenu)

    def setupKeyboardShortcuts(self):
        # Number keys
        for i in range(10):
            self.addKeyboardShortcut(str(i), lambda x=i: self.update_display(str(x)))
        
        # Operation keys
        self.addKeyboardShortcut("+", lambda: self.set_operation("+"))
        self.addKeyboardShortcut("-", lambda: self.set_operation("-"))
        self.addKeyboardShortcut("*", lambda: self.set_operation("*"))
        self.addKeyboardShortcut("/", lambda: self.set_operation("/"))
        self.addKeyboardShortcut("Return", self.calculate_result)
        self.addKeyboardShortcut("Enter", self.calculate_result)
        self.addKeyboardShortcut("Escape", self.clear_display)
        
        # Advanced operations
        self.addKeyboardShortcut("Ctrl+S", lambda: self.advanced_operation("sqrt"))
        self.addKeyboardShortcut("Ctrl+P", lambda: self.advanced_operation("pow"))
        self.addKeyboardShortcut("Ctrl+L", lambda: self.advanced_operation("log"))

    def addKeyboardShortcut(self, key, slot):
        shortcut = QKeySequence(key)
        action = QAction(self)
        action.setShortcut(shortcut)
        action.triggered.connect(slot)
        self.addAction(action)

    def advanced_operation(self, op):
        try:
            value = float(self.display.text())
            result = 0
            if op == "sqrt":
                result = math.sqrt(value)
            elif op == "pow":
                result = value ** 2
            elif op == "log":
                result = math.log10(value)
            self.display.setText(str(result))
            self.addToHistory(f"{op}({value}) = {result}")
        except ValueError:
            self.showError("Invalid input for operation")
        except Exception as e:
            self.showError(str(e))

    def showError(self, message):
        QMessageBox.critical(self, "Error", message)

    def addToHistory(self, calculation):
        self.history.append(calculation)
        self.saveHistory()

    def saveHistory(self):
        self.settings.setValue('history', self.history[:100])  # Keep last 100 calculations

    def loadHistory(self):
        self.history = self.settings.value('history', [])

    def showHistory(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Recent Calculations")
        layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.addItems(self.history)
        layout.addWidget(list_widget)
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(lambda: self.clearHistory(list_widget))
        layout.addWidget(clear_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def clearHistory(self, list_widget):
        self.history.clear()
        self.saveHistory()
        list_widget.clear()

    def setTheme(self, theme):
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; }
                QPushButton { background-color: #3b3b3b; color: white; }
                QLineEdit { background-color: #3b3b3b; color: white; }
            """)
        else:
            self.setStyleSheet("")
        self.settings.setValue('theme', theme)

    def loadTheme(self):
        theme = self.settings.value('theme', 'light')
        self.setTheme(theme)

    def initUI(self):
        # Connect buttons to functions
        self.btn_0.clicked.connect(lambda: self.update_display("0"))
        self.btn_1.clicked.connect(lambda: self.update_display("1"))
        self.btn_2.clicked.connect(lambda: self.update_display("2"))
        self.btn_3.clicked.connect(lambda: self.update_display("3"))
        self.btn_4.clicked.connect(lambda: self.update_display("4"))
        self.btn_5.clicked.connect(lambda: self.update_display("5"))
        self.btn_6.clicked.connect(lambda: self.update_display("6"))
        self.btn_7.clicked.connect(lambda: self.update_display("7"))
        self.btn_8.clicked.connect(lambda: self.update_display("8"))
        self.btn_9.clicked.connect(lambda: self.update_display("9"))
        self.btn_decimal.clicked.connect(lambda: self.update_display("."))
        self.btn_add.clicked.connect(lambda: self.set_operation("+"))
        self.btn_subtract.clicked.connect(lambda: self.set_operation("-"))
        self.btn_multiply.clicked.connect(lambda: self.set_operation("*"))
        self.btn_divide.clicked.connect(lambda: self.set_operation("/"))
        self.btn_equals.clicked.connect(self.calculate_result)
        self.btn_clear.clicked.connect(self.clear_display)
        self.btn_add_transaction.clicked.connect(self.add_transaction)
        self.load_transactions()

        # Add search field for customers
        self.customer_search_input = QLineEdit(self)
        self.customer_search_input.setPlaceholderText("Search Customer...")
        self.customer_search_input.textChanged.connect(self.searchCustomers)
        self.verticalLayout.addWidget(self.customer_search_input)

        self.customer_list_widget = QListWidget(self)
        self.customer_list_widget.itemClicked.connect(self.selectCustomer)
        self.verticalLayout.addWidget(self.customer_list_widget)

    def update_display(self, value):
        if self.display.text() == "0" and value != ".":
            self.display.setText(value)
        else:
            self.display.setText(self.display.text() + value)

    def set_operation(self, op):
        if self.display.text():
            self.first_operand = float(self.display.text())
            self.current_input = ""
            self.operation = op
            self.display.setText("")

    def calculate_result(self):
        if self.display.text() and self.first_operand is not None and self.operation:
            second_operand = float(self.display.text())
            result = 0
            if self.operation == "+":
                result = self.first_operand + second_operand
            elif self.operation == "-":
                result = self.first_operand - second_operand
            elif self.operation == "*":
                result = self.first_operand * second_operand
            elif self.operation == "/":
                result = self.first_operand / second_operand if second_operand != 0 else "Error"
            self.display.setText(str(result))
            self.first_operand = None
            self.operation = None

    def clear_display(self):
        self.display.setText("0")
        self.first_operand = None
        self.operation = None

    def add_transaction(self):
        amount = float(self.display.text()) if self.display.text() else 0.0
        description = "Transaction Description"  # You can change this to get description from another input field if needed
        self.db.add_transaction(amount, description)
        self.load_transactions()
        self.clear_display()

    def load_transactions(self):
        transactions = self.db.get_transactions()
        # Assuming you have a QListWidget named transaction_list in your UI
        if hasattr(self, 'transaction_list'):
            self.transaction_list.clear()
            for trans in transactions:
                item = f"{trans[1]} - {trans[2]} ({trans[3]})"
                self.transaction_list.addItem(item)

    def showCustomers(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Customers")
        layout = QVBoxLayout()
        table_widget = QTableWidget()
        table_widget.setRowCount(0)
        table_widget.setColumnCount(5)
        table_widget.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Email", "Actions"])
        customers = self.db.get_customers()
        for customer in customers:
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)
            for col, value in enumerate(customer):
                table_widget.setItem(row_position, col, QTableWidgetItem(str(value)))
            # Add action buttons for modify and delete
            modify_btn = QPushButton("Modify")
            modify_btn.clicked.connect(lambda checked, id=customer[0]: self.modifyCustomer(id))
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, id=customer[0]: self.deleteCustomer(id))
            add_transaction_btn = QPushButton("Add Transaction")
            add_transaction_btn.clicked.connect(lambda checked, id=customer[0]: self.addTransaction(id))
            view_transactions_btn = QPushButton("View Transactions")
            view_transactions_btn.clicked.connect(lambda checked, id=customer[0]: self.showCustomerTransactions(id))
            table_widget.setCellWidget(row_position, 4, modify_btn)
            table_widget.setCellWidget(row_position, 4, delete_btn)
            table_widget.setCellWidget(row_position, 4, add_transaction_btn)
            table_widget.setCellWidget(row_position, 4, view_transactions_btn)
        layout.addWidget(table_widget)
        add_btn = QPushButton("Add Customer")
        add_btn.clicked.connect(self.addCustomer)
        layout.addWidget(add_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def modifyCustomer(self, customer_id):
        customer = self.db.get_customer(customer_id)
        dialog = QDialog(self)
        dialog.setWindowTitle("Modify Customer")
        layout = QVBoxLayout()
        name_input = QLineEdit(customer[1])
        phone_input = QLineEdit(customer[2])
        email_input = QLineEdit(customer[3])
        layout.addWidget(QLabel("Name"))
        layout.addWidget(name_input)
        layout.addWidget(QLabel("Phone"))
        layout.addWidget(phone_input)
        layout.addWidget(QLabel("Email"))
        layout.addWidget(email_input)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.saveModifiedCustomer(customer_id, name_input.text(), phone_input.text(), email_input.text()))
        layout.addWidget(save_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def saveModifiedCustomer(self, customer_id, name, phone, email):
        self.db.update_customer(customer_id, name, phone, email, "")  # Address can be added later
        QMessageBox.information(self, "Success", "Customer modified successfully!")

    def deleteCustomer(self, customer_id):
        self.db.delete_customer(customer_id)
        QMessageBox.information(self, "Success", "Customer deleted successfully!")

    def addCustomer(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Customer")
        layout = QVBoxLayout()
        name_input = QLineEdit()
        phone_input = QLineEdit()
        email_input = QLineEdit()
        layout.addWidget(QLabel("Name"))
        layout.addWidget(name_input)
        layout.addWidget(QLabel("Phone"))
        layout.addWidget(phone_input)
        layout.addWidget(QLabel("Email"))
        layout.addWidget(email_input)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(lambda: self.saveCustomer(name_input.text(), phone_input.text(), email_input.text()))
        layout.addWidget(add_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def saveCustomer(self, name, phone, email):
        if name and email:
            self.db.add_customer(name, phone, email, "")  # Address can be added later
            QMessageBox.information(self, "Success", "Customer added successfully!")
        else:
            QMessageBox.warning(self, "Error", "Name and Email are required fields.")

    def addTransaction(self, customer_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Transaction")
        layout = QVBoxLayout()
        amount_input = QLineEdit()
        type_input = QLineEdit()  # 'credit' or 'debit'
        description_input = QLineEdit()
        layout.addWidget(QLabel("Amount"))
        layout.addWidget(amount_input)
        layout.addWidget(QLabel("Type (credit/debit)"))
        layout.addWidget(type_input)
        layout.addWidget(QLabel("Description"))
        layout.addWidget(description_input)
        add_btn = QPushButton("Add Transaction")
        add_btn.clicked.connect(lambda: self.saveTransaction(customer_id, amount_input.text(), type_input.text(), description_input.text()))
        layout.addWidget(add_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def saveTransaction(self, customer_id, amount, type, description):
        if type in ['credit', 'debit']:
            self.db.add_customer_transaction(customer_id, float(amount), type, description)
            QMessageBox.information(self, "Success", "Transaction added successfully!")
        else:
            QMessageBox.warning(self, "Error", "Transaction type must be 'credit' or 'debit'.")

    def showCustomerTransactions(self, customer_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Transaction History")
        layout = QVBoxLayout()
        table_widget = QTableWidget()
        table_widget.setRowCount(0)
        table_widget.setColumnCount(4)
        table_widget.setHorizontalHeaderLabels(["ID", "Amount", "Type", "Description"])
        transactions = self.db.get_customer_transactions(customer_id)
        for transaction in transactions:
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)
            for col, value in enumerate(transaction):
                table_widget.setItem(row_position, col, QTableWidgetItem(str(value)))
        layout.addWidget(table_widget)
        dialog.setLayout(layout)
        dialog.exec_()

    def showAbout(self):
        QMessageBox.information(self, "About", "Smart Calculator")

    def showMenu(self):
        self.menu.exec_(self.btn_menu.mapToGlobal(self.btn_menu.rect().bottomLeft()))

    def searchCustomers(self):
        search_text = self.customer_search_input.text().lower()
        self.customer_list_widget.clear()
        customers = self.db.get_customers()
        for customer in customers:
            if search_text in customer[1].lower():  # Assuming customer[1] is the name
                self.customer_list_widget.addItem(f"{customer[1]} (ID: {customer[0]})")

    def selectCustomer(self, item):
        customer_id = int(item.text().split("(ID: ")[1][:-1])  # Extract ID from text
        self.current_customer_id = customer_id
        QMessageBox.information(self, "Customer Selected", f"Selected Customer ID: {customer_id}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalculatorApp()
    window.show()
    sys.exit(app.exec_())
