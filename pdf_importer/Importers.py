""" Collection of importers.
"""

# Imports

# Third party
import camelot
from dateutil.parser import parse
from pandas import concat

# import Cembra (Certo
def extract_cembra(filename):
    entries = []

    tables = camelot.read_pdf(filename, pages='2-end')

    for page, pdf_table in enumerate(tables):
        df = tables[page].df
        for _, row in df.iterrows():
            try:
                date = parse(row[1].strip(), dayfirst=True).date()
                _ = parse(row[0].strip(), dayfirst=True).date()
                text = row[2]
                credit = row[3].replace('\'', '')
                debit = row[4].replace('\'', '')
                amount = -float(debit) if debit else float(credit)
                entries.append([date, amount, text])
            except ValueError:
                pass

    return entries

# import SwissCards (Cashback Cards) statement
def extract_cashback(filename):
    entries = []

    tables = []
    for page in range(1, camelot.read_pdf(filename, pages='1', flavor='stream').n):
        page_tables = camelot.read_pdf(
            filename,
            pages=str(page),
            flavor='stream',
            table_areas=['50,800,560,50'],
            columns=['120,530']
        )
        tables += page_tables

    df = concat([table.df for table in tables])

    for index, row in df.iterrows():
        try:
            date = parse(row[0].strip(), dayfirst=True).date()
            text = row[1].replace("\n", " ")
            amount = -float(row[2].replace("'", ""))

            if text == "YOUR PAYMENT – THANK YOU":
                amount = -amount

            entries.append([date, amount, text])
        except ValueError:
            pass

    return entries
