#引用套件
from google.cloud import storage

#建立客戶端(是為了讓用戶能夠通過這裡去發指令操作)
storage_client = storage.Client()

#指定bucket name
bucket_name = 'amyge-ai-storage-user-info' 
#bucket內物件的名字
blob_name = 'amyge.txt'

#建立bucket的客戶端(後續才能指定某個桶子內的物件去操作)
bucket =storage_client.bucket(bucket_name)

#建立物件的客戶端
blob = bucket.blob(blob_name)

#請刪除物件
blob.delete()

