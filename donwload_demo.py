#引用套件
from google.cloud import storage

#建立客戶端(是為了讓用戶能夠通過這裡去發指令操作)
storage_client = storage.Client()

#指定桶子名字
bucket_name = 'amyge-ai-storage-user-info'

#告知遠端物件的名字
source_blob_name = 'amyge.txt'

# 下載回本地端的名字
destination_file_name = 'downloadBack.txt'

#建立bucket的客戶端(後續才能指定某個桶子內的物件去操作)
bucket = storage_client.bucket(bucket_name)

#建立遠端物件的客戶端
blob = bucket.blob(source_blob_name)

#下載回本地端
blob.download_to_filename(destination_file_name)
