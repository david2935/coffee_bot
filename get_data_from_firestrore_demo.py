#引用套件
from google.cloud import firestore

#建立firestore客戶端(是為了讓用戶能夠通過這裡去發指令操作)
db = firestore.Client()

#指定操作哪一個表格的哪一筆資料
#取db_user表格裡面的 資料主鍵叫做Alfred的資料
doc_ref  =  db.collection(u'db_user').document(u'Alfred')

#取得資料
doc = doc_ref.get()

#若資料存在
if doc.exists:
    print(f'Document data:{doc.to_dict()}')

else:
    print(f'No such document')
