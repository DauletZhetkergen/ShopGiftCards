import sqlite3
import xlsxwriter


conn = sqlite3.Connection("shop_originals.db", check_same_thread=False)
cursor = conn.cursor()
path = "report"



def generate_excel():
    cursor.execute("SELECT * from orders")
    res = cursor.fetchall()
    workbook = xlsxwriter.Workbook('datas.xlsx')
    worksheet = workbook.add_worksheet()
    header_data = ['number','product id','product name','price','buyer id','username']
    for col_num, data in enumerate(header_data):
        worksheet.write(0, col_num, data,)
    for i,row in enumerate(res):
        for j,value in enumerate(row):
            worksheet.write(i+1, j, value)
    workbook.close()
    return 'datas.xlsx'

generate_excel()




