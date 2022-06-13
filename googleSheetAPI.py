import gspread
from oauth2client.service_account import ServiceAccountCredentials
auth_json_path = '/home/amyge2935/amyge_GCP_test/token.json'
gss_scopes = ['https://spreadsheets.google.com/feeds']
#連線
credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_json_path,gss_scopes)
gss_client = gspread.authorize(credentials)
#開啟 Google Sheet 資料表
spreadsheet_key = '1rEIHr7cA2gtxS4hv58dLWtQ03QbXWWp8qxRVnY1mF6E' 
#建立工作表1
sheet = gss_client.open_by_key(spreadsheet_key).sheet1
#自定義工作表名稱
#sheet = gss_client.open_by_key(spreadsheet_key).worksheet('測試1')



a = sheet.findall('ABC', in_column=1 )
print(type(a))
print(a.)     
# #Google Sheet 資料表操作(舊版)
# sheet.clear() # 清除 Google Sheet 資料表內容
# listtitle=["姓名","電話"]
# sheet.append_row(listtitle)  # 標題
# listdata=["Liu","0912-345678"]
# sheet.append_row(listdata)  # 資料內容

# #Google Sheet 資料表操作(20191224新版)
# sheet.update_acell('D2', 'ABC')  #D2加入ABC
# sheet.update_cell(2, 4, 'ABC')   #D2加入ABC(第2列第4行即D2)
# #寫入一整列(list型態的資料)
# values = ['A','B','C','D']
# sheet.insert_row(values, 1) #插入values到第1列
# #讀取儲存格
# sheet.acell('B1').value
# sheet.cell(1, 2).value
# #讀取整欄或整列
# sheet.row_values(1) #讀取第1列的一整列
# sheet.col_values(1) #讀取第1欄的一整欄
# #讀取整個表
# sheet.get_all_values()