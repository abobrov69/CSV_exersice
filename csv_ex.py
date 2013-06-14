from csv_work import CSVAverageCalculate, BaseCSVHandler
import sys

csv_han = CSVAverageCalculate(double_rec_is_error=False)
csv_han.process_all()