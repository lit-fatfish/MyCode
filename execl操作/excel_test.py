import os, sys
import xlwings as xw




# 创建一个execl文件，然后保存和关闭
# app = xw.App(visible = True, add_book = False)
# workbook = app.books.add()

# workbook.save('./test.xlsx')
# workbook.close()
# app.quit()


# 打开一个execl文件
app = xw.App(visible = True, add_book = False)
workbook = app.books.open('./test.xlsx')

worksheet = workbook.sheets['Sheet1']
worksheet.range('A1').value = "haha"

workbook.save('./test.xlsx')
# workbook.close()
# app.quit()
