import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget
from ui_main import Ui_MainWindow
from db_manager import DBManager

class CalculatorApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db = DBManager()
        self.initUI()
        self.current_input = ""
        self.operation = None
        self.first_operand = None

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalculatorApp()
    window.show()
    sys.exit(app.exec_())
