#引用flask套件
from flask import Flask, request, abort
# 引用line bot套件
from linebot import (
    LineBotApi, WebhookHandler
)
# 驗證消息用的套件
from linebot.exceptions import (
    InvalidSignatureError
)
# 引用line的消息套件
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent, ImageMessage
)


# 圖片下載與上傳專用
import urllib.request
import os

# 建立日誌紀錄設定檔
# https://googleapis.dev/python/logging/latest/stdlib-usage.html
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler

# 啟用log的客戶端
client = google.cloud.logging.Client()


# 建立line event log，用來記錄line event
bot_event_handler = CloudLoggingHandler(client,name="amyge_bot_event")
bot_event_logger=logging.getLogger('amyge_bot_event')
bot_event_logger.setLevel(logging.INFO)
bot_event_logger.addHandler(bot_event_handler)

# 準備app
app = Flask(__name__)


# 註冊機器人
# 專門跟line溝通的
line_bot_api = LineBotApi('HK4Fd7j61yuzCKRkeK4IpimK4INl6iHAKSdJgOiByOvODUHqCAUfLH4tE7/fxa+BnOvHjXGFbGT22lb8Fpa0EetZRWvh4+bZ7nS3TRscsj1RIsrwQbX11nelC+nDLGpDGSd0ZRKiPtV8/qNmDqt2/QdB04t89/1O/w1cDnyilFU=')
# 收消息用的
handler = WebhookHandler('bd37e59984fc46353c1e28c7b4145ab5')

# 設定機器人訪問入口 (給line發消息用的http入口)
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print(body)
    # 消息整個交給bot_event_logger，請它傳回GCP
    bot_event_logger.info(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'



from google.cloud import storage
from google.cloud import firestore
@handler.add(FollowEvent)
def handle_follow_event(event):


        # 歡迎使用者加入後, 要求輸入住戶獨有驗證碼
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="歡迎加入[OO]社區事務服務機器,請輸入'@user_驗證碼'以便系統確認身分"))
        
        

        # 取個資
        line_user_profile= line_bot_api.get_profile(event.source.user_id)

        # 跟line 取回照片，並放置在本地端
        file_name = line_user_profile.user_id+'.jpg'
        urllib.request.urlretrieve(line_user_profile.picture_url, file_name)

       # 設定內容
        storage_client = storage.Client()
        bucket_name="amyge-ai-storage-user-info"
        destination_blob_name=f"{line_user_profile.user_id}/user_pic.png"
        source_file_name=file_name
       
      # 進行上傳
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)


        
      # 設定用戶資料json
        user_dict={
            "user_id":line_user_profile.user_id,
            "picture_url": f"https://storage.googleapis.com/{bucket_name}/destination_blob_name",
            "display_name": line_user_profile.display_name,
            "status_message": line_user_profile.status_message
        }
      # 插入firestore
        db = firestore.Client()
        doc_ref = db.collection(u'line-user').document(user_dict.get("user_id"))
        doc_ref.set(user_dict)





# 當用戶收到文字消息的時候，回傳用戶講過的話
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    
    if (event.message.text.find('@user_')) != -1:
    
        auth_num = event.message.text
        
        db = firestore.Client()
        
        doc_ref  =  db.collection(u'user_list').document(auth_num[6:])

  
        doc = doc_ref.get()


        if doc.exists:
            
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='住戶驗證成功, 歡迎使用住戶功能輸入@help'))
            
            doc_ref  =  db.collection(u'line-user').document(event.source.user_id)

            # 將認證碼以及認證狀態新增進去
            doc_ref.update({
                u'auth_key':auth_num[6:],
                u'identification':True,
                
            })            


        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='查無登記住戶資料'))
            # 將認證碼以及認證狀態新增進去
            doc_ref  =  db.collection(u'line-user').document(event.source.user_id)
            doc_ref.update({
                u'auth_key':auth_num[6:],
                u'identification':False,
                
            })     
            

    elif event.message.text == '@help':
        
        db = firestore.Client()
        doc_ref  =  db.collection(u'line-user').document(event.source.user_id)
        doc = doc_ref.get()
        if doc.get('identification') == True:
            # line_bot_api.reply_message(event.reply_token, TextSendMessage(text='help你老師'))
            # 引入相關套件
            from linebot.models import (
                MessageAction, URIAction,
                PostbackAction, DatetimePickerAction,
                CameraAction, CameraRollAction, LocationAction,
                QuickReply, QuickReplyButton
            )

            # 創建QuickReplyButton 

            ## 點擊後，以用戶身份發送文字消息
            MessageAction 
            vote_QRB = QuickReplyButton(
                action=MessageAction(
                    label="投票區", 
                    text="@Vote"
                    
                )
                
            )

            announcement_QRB = QuickReplyButton(
                action=MessageAction(
                    label="公告項目", 
                    text="@Announcement"
                    
                )
                
            )

            finance_QRB = QuickReplyButton(
                action=MessageAction(
                    label="繳費狀態", 
                    text="@ManagementFee"
                    
                )
                
            )



            # 點擊後，以Postback事件回應Server 
            report_QRB = QuickReplyButton(
                action=PostbackAction(
                    label="舉報填單",
                    data="這住戶夠雞歪",
                    text= "@Report"
                
                
                )
            )
            
            quickReplyList = QuickReply(
                items = [vote_QRB, announcement_QRB, report_QRB]
            )

            # 製作TextSendMessage，並將剛封裝的QuickReply放入

            # 將quickReplyList 塞入TextSendMessage 中 
        
            quick_reply_text_send_message = TextSendMessage(text='請選擇社區事務項目', quick_reply=quickReplyList)

            line_bot_api.reply_message(event.reply_token, quick_reply_text_send_message)

        else:
            
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='非授權用戶,無法使用此功能'))


    elif event.message.text == '@vote':
        db = firestore.Client()
        doc_ref  =  db.collection(u'line-user').document(event.source.user_id)
        doc = doc_ref.get()
        if doc.get('identification') == True:
            


        else:
            
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='非授權用戶,無法使用此功能'))            







from linebot.models import ImageMessage
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):


    # 取出照片
    image_blob = line_bot_api.get_message_content(event.message.id)
    temp_file_path=f"""{event.message.id}.png"""

    with open(temp_file_path, 'wb') as fd:
        for chunk in image_blob.iter_content():
            fd.write(chunk)

    # 上傳至cloud storage
    storage_client = storage.Client()
    bucket_name = "amyge-ai-storage-user-info"
    destination_blob_name = f'{event.source.user_id}/image/{event.message.id}.png'
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(temp_file_path)

    # 未來放ai功能

    # 回應用戶
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(f"""圖片已上傳，請期待未來的AI服務！""")
        )




#運行, 自動運行在 8080 port
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))



#後續在下方terminal操作
# 啟動應用程式，預設是8080 Port， port那段是為了可以部署到cloud run 而增設的
# 下載ngrok 並變更成可執行的檔案
# wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
# unzip ngrok-stable-linux-amd64.zip
# sudo chmod u+x ngrok
# ./ngrok http --region ap  8080

# 在亞洲執行ngrok，轉發 flask 8080 Port的流量

# 有發行失敗的可能  操


