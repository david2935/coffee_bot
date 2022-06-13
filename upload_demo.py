#引用套件
from google.cloud import storage

#建立客戶端(是為了讓用戶能夠通過這裡去發指令操作)
storage_client = storage.Client()

#指定bucket name
bucket_name = 'amyge-ai-storage-user-info' 

#上傳到bucket之後的名字
destination_blob_name = 'amyge.txt'

#本地要上傳的檔案
source_file_name = 'requirements.txt'

#將本地端的requirements.txt上傳到amyge-ai-storage-user-info的桶子 並將檔名改為amyge.txt
#建立bucket的客戶端(後續才能指定某個桶子內的物件去操作)
bucket = storage_client.bucket(bucket_name)
#指定桶子內物件
blob = bucket.blob(destination_blob_name)
#把本地檔案上傳
blob.upload_from_filename(source_file_name)