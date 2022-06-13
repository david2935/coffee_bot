#引用套件
from google.cloud import firestore

#建立firestore客戶端(是為了讓用戶能夠通過這裡去發指令操作)
db = firestore.Client()

#指定操作哪一個表格的哪一筆資料
#取db_user表格裡面的 資料主鍵叫做Alfred的資料
doc_ref  =  db.collection(u'user_list').document(u'TYUFG412865496RE')

# 插入一個dict
doc_ref.set({
    u'name':u'LoveCraft',
    u'floor':u'13',
    u'born':u'1937',
})
