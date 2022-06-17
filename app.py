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
    MessageEvent, TextMessage, TextSendMessage, FollowEvent, ImageMessage, PostbackEvent, ImageSendMessage, FlexSendMessage
)


#引用時間戳套件
from datetime import datetime, timezone




# 引用google sheet的串接套件
# 以及其授權功能
import gspread
from oauth2client.service_account import ServiceAccountCredentials

auth_json_path = './token.json'
# auth_json_path = '/home/amyge2935/amyge_GCP_test/token.json'
gss_scopes = ['https://spreadsheets.google.com/feeds']

# 建立google sheet API的客戶端
credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_json_path,gss_scopes)


gss_client = gspread.authorize(credentials)
#開啟 Google Sheet 資料表
spreadsheet_key = '1rEIHr7cA2gtxS4hv58dLWtQ03QbXWWp8qxRVnY1mF6E' 
#建立工作表1
sheet = gss_client.open_by_key(spreadsheet_key).sheet1


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
line_bot_api = LineBotApi('')
# 收消息用的
handler = WebhookHandler('')



#建置圖文選單json形式
menuRawData="""
{
  "size": {
    "width": 2500,
    "height": 1686
  },
  "selected": true,
  "name": "咖啡自助服務表單",
  "chatBarText": "查看服務功能",
  "areas": [
    {
      "bounds": {
        "x": 0,
        "y": 0,
        "width": 1114,
        "height": 1686
      },
      "action": {
        "type": "uri",
        "uri": "https://shop.7-11.com.tw/shop/rui003.faces?catid=65964&ladosidg=61145_6&icmpid=NA014"
      }
    },
    {
      "bounds": {
        "x": 1233,
        "y": 4,
        "width": 1267,
        "height": 810
      },
      "action": {
        "type": "postback",
        "text": "@Check",
        "data": "@Check"
      }
    },
    {
      "bounds": {
        "x": 1246,
        "y": 911,
        "width": 1254,
        "height": 775
      },
      "action": {
        "type": "postback",
        "text": "@Exchange",
        "data": "@Exchange"
      }
    }
  ]
}
"""

from linebot.models import RichMenu
import requests
import json
#將上面圖文選單形式由json格式讀取
menuJson=json.loads(menuRawData)
#然後利用圖文選單資料建立圖文選單物件並生成圖文選單ID
lineRichMenuId = line_bot_api.create_rich_menu(rich_menu=RichMenu.new_from_json_dict(menuJson))
# print(lineRichMenuId)
#打開圖文選單的圖
uploadImageFile=open("./richMenu.jpg",'rb')
# uploadImageFile=open("/home/amyge2935/amyge_GCP_test/richMenu.jpg",'rb')

#將圖與圖文選單ID綁在一起
line_bot_api.set_rich_menu_image(lineRichMenuId,'image/jpeg',uploadImageFile)




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







@handler.add(FollowEvent)
def handle_follow_event(event):
       
    from google.cloud import storage
    from google.cloud import firestore
    from linebot.models import (
                    MessageAction, URIAction,
                    PostbackAction, DatetimePickerAction,
                    CameraAction, CameraRollAction, LocationAction,
                    QuickReply, QuickReplyButton
                )
    # 創建QuickReplyButton 

    ## 點擊後，以用戶身份發送文字消息
    # MessageAction 
    BuyOnWeb_QRB = QuickReplyButton(
        action=URIAction(
            label="Coffee Shop", 
            uri='https://shop.7-11.com.tw/shop/rui003.faces?catid=65964&ladosidg=61145_6&icmpid=NA014'
            )
        
    )

    Check_QRB = QuickReplyButton(
        action=MessageAction(
            label="查詢持有兌換券", 
            text="@Check"
            
        )
        
    )

    Exchange_QRB = QuickReplyButton(
        action=PostbackAction(
            label="兌換!", 
            text="@Exchange",
            data='customer_exchange'
            
        )
        
    )

    # quickReplyList = QuickReply(
    #     items = [BuyOnWeb_QRB, Check_QRB, Exchange_QRB]
    # )

    # 製作TextSendMessage，並將剛封裝的QuickReply放入

    # 將quickReplyList 塞入TextSendMessage 中 

    # quick_reply_text_send_message = TextSendMessage(text='請選擇服務項目', quick_reply=quickReplyList)

    # line_bot_api.reply_message(event.reply_token, quick_reply_text_send_message)

                    

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

    # 將用戶資料登記到外部google sheet
    ###### 後續正式使用不能由此生成 否則會造成重新follow無限續杯
    userCell = sheet.find(user_dict['user_id'])
    if userCell == None:
        sheet.append_row([user_dict['user_id'],7,7,7,7])
        
    else:
        for col in range(2,6):
            sheet.update_cell(userCell.row , col, 3)
        
           
    
          
    # else:
    #     user_row = sheet.find(user_dict['user_id']).row
    #     sheet.update_cell(user_row, 2, 10) 
    #     sheet.update_cell(user_row, 3, 10) 
    #     sheet.update_cell(user_row, 4, 10) 
    #     sheet.update_cell(user_row, 5, 10) 
        # for col in range(2,6):
            # sheet.update_cell(user_row, col, 10)  


    # 插入firestore
    db = firestore.Client()
    doc_ref = db.collection(u'line-user').document(user_dict.get("user_id"))
    doc_ref.set(user_dict)

    # 歡迎使用者加入
    line_bot_api.reply_message(
    event.reply_token,
    # TextSendMessage(text="歡迎使用自助咖啡服務機器人, 請選擇服務項目", quick_reply = quickReplyList))
    TextSendMessage(text="歡迎使用自助咖啡服務機器人, 請使用下方按鈕選擇服務項目"))
    
    #將使用者與圖文選單綁定
    line_bot_api.link_rich_menu_to_user(event.source.user_id, lineRichMenuId)

    # rich_menu_id = line_bot_api.get_rich_menu_id_of_user(event.source.user_id)

    

# 當用戶收到文字消息的時候，回傳用戶講過的話
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    from google.cloud import storage
    from google.cloud import firestore
    if (event.message.text.find('@Check')) != -1:


        user_row = sheet.find(event.source.user_id)
        # print(cell)
        # print(sheet.row_values(cell.row)[1:]) 
        user_tickets = sheet.row_values(user_row.row)[1:]

        db = firestore.Client()
        doc_ref  =  db.collection(u'line-user').document(event.source.user_id)
        doc = doc_ref.get()
        user_nickname = doc.get('display_name')

        line_bot_api.reply_message(
            event.reply_token, 
            [
                TextSendMessage(text=f'查詢結果,{user_nickname}目前持有:'),
                TextSendMessage(f'義式濃縮{user_tickets[0]}杯'), 
                TextSendMessage(f'美式咖啡{user_tickets[1]}杯'), 
                TextSendMessage(f'拿鐵咖啡{user_tickets[2]}杯'),
                TextSendMessage(f'卡布奇諾{user_tickets[3]}杯')
            ]
        
        )
        # ---------------------------------------------------------------------------
        # 本區是利用GCP的firestore模擬外部資料庫
        # db = firestore.Client()

        # doc_ref  =  db.collection(u'line-user').document(event.source.user_id)
        # doc = doc_ref.get()
        # if doc.exists:

        #     coffee_A = doc.get('coffee_A')
        #     coffee_B = doc.get('coffee_B')
        #     coffee_C = doc.get('coffee_C')
        #     user_nickname = doc.get('display_name')

        # line_bot_api.reply_message(
        #     event.reply_token, 
        #     [
        #         TextSendMessage(text=f'查詢結果,{user_nickname}目前持有:'),
        #         TextSendMessage(f'A咖啡{coffee_A}杯'), 
        #         TextSendMessage(f'B咖啡{coffee_B}杯'), 
        #         TextSendMessage(f'C咖啡{coffee_C}杯')
        #     ]
        
        # )
        # ------------------------------------------------------------------------- 

    elif event.message.text == '@Exchange':
        
        db = firestore.Client()
        doc_ref  =  db.collection(u'line-user').document(event.source.user_id)
        doc = doc_ref.get()
         
        # 引入相關套件
        from linebot.models import (
            MessageAction, URIAction,
            PostbackAction, DatetimePickerAction,
            CameraAction, CameraRollAction, LocationAction,
            QuickReply, QuickReplyButton
        )

        # 創建QuickReplyButton 

        ## 點擊後，以用戶身份發送文字消息
        # MessageAction 
        Espresso_QRB = QuickReplyButton(
            action=PostbackAction(
                label="義式濃縮",
                data="@Exchange_Espresso",
                text= "@兌換義式濃縮"
            )
            
        )

        CaffeAmericano_QRB = QuickReplyButton(
            action=PostbackAction(
                label="美式咖啡",
                data="@Exchange_CaffeAmericano",
                text= "@兌換美式咖啡"
            )
            
        )

        CaffeLatte_QRB = QuickReplyButton(
            action=PostbackAction(
                label="拿鐵咖啡",
                data="@Exchange_CaffeLatte",
                text= "@兌換拿鐵咖啡"
            )
            
        )

        Capuccino_QRB = QuickReplyButton(
            action=PostbackAction(
                label="卡布奇諾",
                data="@Exchange_Capuccino",
                text= "@兌換卡布奇諾"
            )
            
        )
        
        #全品項種類
        allTypeCoffee = [Espresso_QRB, CaffeAmericano_QRB, CaffeLatte_QRB, Capuccino_QRB]
        
        user_row = sheet.find(event.source.user_id)
        user_tickets = sheet.row_values(user_row.row)[1:]

        # 判斷是否還有該品項可兌換, 有的話才顯示泡泡
        items = []
        i = 0
        for coffee_num in user_tickets:
            if int(coffee_num)>0:
                items.append(allTypeCoffee[i])
                i+=1
            else:
                i+=1
        if items == []:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="目前帳戶內並無任何可兌換品項"))
        else:
            quickReplyList = QuickReply(
                items
            )
            quick_reply_text_send_message = TextSendMessage(text='請選擇要兌換的咖啡品項', quick_reply=quickReplyList)

            line_bot_api.reply_message(event.reply_token, quick_reply_text_send_message)

    elif    event.message.text == '@Buy':
        # https://developers.line.biz/flex-simulator/ 模擬器 直接拉完元件貼content
        FlexContainerRaw="""
            {
                "type": "carousel",
                "contents": 
                    [
                        {
                            
                            "type": "bubble",

                            "styles": 
                                {
                                    "header": 
                                        {
                                            "backgroundColor": "#ffaaaa"
                                        },
                                    "body": 
                                        {
                                            "backgroundColor": "#aaffaa"
                                        },
                                    "footer": 
                                        {
                                            "backgroundColor": "#aaaaff"
                                        }
                                },

                                "header": 
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": 
                                            [
                                                {
                                                    "type": "text",
                                                    "text": "header"
                                                }
                                            ]               
                                },

                                "hero": 
                                    {
                                        "type": "image",
                                        "url": "https://example.com/flex/images/image.jpg",
                                        "size": "full",
                                        "aspectRatio": "2:1"
                                },

                                "body": 
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": 
                                            [
                                                {
                                                    "type": "text",
                                                    "text": "body"
                                                }
                                            ]
                                },

                                "footer":
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": 
                                            [
                                                {
                                                    "type": "text",
                                                    "text": "footer"
                                                }
                                            ]
                                    }
                        }
                    ]
            }
            """

# import requests
# def qrCode_generate(QRdata):
    
#     img_data = requests.get(f'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={QRdata}').content
#     with open('image_name.jpg', 'wb') as handler:
#         handler.write(img_data)

    

# 增加後台postback event處理
@handler.add(PostbackEvent)
def handle_post_message(event):

    
    user_row = sheet.find(event.source.user_id)
    
    # user_tickets = sheet.row_values(user_row.row)[1:]

    if (event.postback.data.find('@Exchange_Espresso') != -1):

        coffee_col = sheet.find('Espresso')
        EspressoNum = sheet.row_values(user_row.row)[1]
        sheet.update_cell(user_row.row, coffee_col.col, int(EspressoNum) -1)

        # qrCode_generate('timestamp+userID+productName')
        timestamp = datetime.now().timestamp()
        
        QRdata = timestamp

        line_bot_api.reply_message(
        event.reply_token,[
            ImageSendMessage(
                original_content_url=f'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={QRdata}',
                preview_image_url=f'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={QRdata}'
            ),
            TextSendMessage(text = '已生成兌換二維條碼, 請盡速使用')
            ]
        )
    elif (event.postback.data.find('@Exchange_CaffeAmericano') != -1):

        coffee_col = sheet.find('CaffeAmericano')
        CaffeAmericanoNum = sheet.row_values(user_row.row)[2]
        sheet.update_cell(user_row.row, coffee_col.col, int(CaffeAmericanoNum) -1)

        timestamp = datetime.now().timestamp()
        
        QRdata = timestamp

        line_bot_api.reply_message(
        event.reply_token,[
            ImageSendMessage(
                original_content_url=f'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={QRdata}',
                preview_image_url=f'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={QRdata}'
            ),
            TextSendMessage(text = '已生成兌換二維條碼, 請盡速使用')
            ]
        )
    elif (event.postback.data.find('@Exchange_CaffeLatte') != -1):

        coffee_col = sheet.find('CaffeLatte')
        CaffeLatteNum = sheet.row_values(user_row.row)[3]
        sheet.update_cell(user_row.row, coffee_col.col, int(CaffeLatteNum) -1)

        timestamp = datetime.now().timestamp()
        
        QRdata = timestamp

        line_bot_api.reply_message(
        event.reply_token,[
            ImageSendMessage(
                original_content_url=f'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={QRdata}',
                preview_image_url=f'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={QRdata}'
            ),
            TextSendMessage(text = '已生成兌換二維條碼, 請盡速使用')
            ]
        )
    elif (event.postback.data.find('@Exchange_Capuccino') != -1):

        coffee_col = sheet.find('Capuccino')
        CapuccinoNum = sheet.row_values(user_row.row)[4]
        sheet.update_cell(user_row.row, coffee_col.col, int(CapuccinoNum) -1)

        timestamp = datetime.now().timestamp()
        
        QRdata = timestamp

        line_bot_api.reply_message(
        event.reply_token,[
            ImageSendMessage(
                original_content_url=f'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={QRdata}',
                preview_image_url=f'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={QRdata}'
            ),
            TextSendMessage(text = '已生成兌換二維條碼, 請盡速使用')
            ]
        )

    else:
        pass

# from google.cloud import storage
# from google.cloud import firestore
# from linebot.models import ImageMessage
# @handler.add(MessageEvent, message=ImageMessage)
# def handle_image_message(event):

#     # 取出照片
#     image_blob = line_bot_api.get_message_content(event.message.id)
#     temp_file_path=f"""{event.message.id}.png"""

#     with open(temp_file_path, 'wb') as fd:
#         for chunk in image_blob.iter_content():
#             fd.write(chunk)

#     # 上傳至cloud storage
#     storage_client = storage.Client()
#     bucket_name = "amyge-ai-storage-user-info"
#     destination_blob_name = f'{event.source.user_id}/image/{event.message.id}.png'
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)
#     blob.upload_from_filename(temp_file_path)

#     # 未來放ai功能

#     # 回應用戶
#     line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(f"""圖片已上傳，請期待未來的AI服務！""")
#         )




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


