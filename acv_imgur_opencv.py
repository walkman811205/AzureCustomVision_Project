# import flask related
from flask import Flask, request, abort
# import linebot related
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage
)
#import azure custom vision
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import time
import pyimgur #imgur package
import cv2

# create flask server
app = Flask(__name__)
# your linebot message API - Channel access token (from LINE Developer)
line_bot_api = LineBotApi('AbkQ/yMuPwDU5wRk5dloLdB+Glwxvb7yhXTJAI6B/u83WeDb/NpL/HKKkHwafQVQP331Q2vBsvsK6iYP9Hy0ZPK+Lj10aHSNmQEJnHVttlIjwh4i/mNSGj3psiH9zGrfBygYr/WHNg0oqVMsrramkgdB04t89/1O/w1cDnyilFU=')
# your linebot message API - Channel secret
handler = WebhookHandler('70f60f6c949603102090680a7362c807')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        print('receive msg')
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# handle msg
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    # get user info & message
    user_id = event.source.user_id
    # msg = event.message.text
    user_name = line_bot_api.get_profile(user_id).display_name
 
    name_img = 'C:\\Users\\Tibame\\Desktop\\Programming\\Azure\\aaa.jpg'
    message_content = line_bot_api.get_message_content(event.message.id)
    
    with open(name_img, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
        # ??????customvision???????????????
        ENDPOINT = "https://duke-cvaio.cognitiveservices.azure.com/"
        training_key = "6e767a3c09c446ada34d6fc85c998aaa"
        prediction_key = "adc306cb86b84a308d6bf15489c7f017"
        prediction_resource_id = "/subscriptions/2eb1a049-0d06-452c-8182-df0e4a04ef2f/resourceGroups/test/providers/Microsoft.CognitiveServices/accounts/dukeCVAIO-Prediction"

        credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
        trainer = CustomVisionTrainingClient(ENDPOINT, credentials)
        prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
        predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)

        #publish????????????????????????
        publish_iteration_name = "helment"

        credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
        trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

        #???????????????????????????????????????????????????????????????
        base_image_location = "C:\\Users\\Tibame\\Desktop\\Programming\\Azure\\"

        # <snippet_test>
        # Now there is a trained endpoint that can be used to make a prediction
        prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
        predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)


        #???????????????????????????????????????????????????Azure??????????????????
        with open(base_image_location + "aaa.jpg", mode="rb") as test_data:
            results = predictor.detect_image('171a6dfc-3f69-41b9-9536-798547992ff7', publish_iteration_name, test_data)

        # ???OpenCV????????????????????????????????????????????????????????????
        img_path ='C:\\Users\\Tibame\\Desktop\\Programming\\Azure\\aaa.jpg'
   
        # ???????????????OpenCV
        image = cv2.imread(img_path) 

        # ???shape????????????????????????????????????
        sp = image.shape[:]
        imageheigh = sp[0]
        imageWidth = sp[1]

       # ?????????????????????????????????
        window_name = 'Image'
        
        # Blue color in BGR 
        color = (255, 0, 0) 
        
        # Line thickness of 2 px 
        thickness = 2
        
        list = [] #??????????????????list
        # ??????????????????????????????
        for o in results.predictions:
            if o.probability >= 0.5:
                print("\t" + o.tag_name + ": {0:.2f}%, object at location (X1, Y1, X2, Y2): {1:.2f}, {2:.2f}, {3:.2f}, {4:.2f}".format(o.probability * 100, 
                o.bounding_box.left, o.bounding_box.left + o.bounding_box.width, o.bounding_box.top, o.bounding_box.top + o.bounding_box.height))
                #???????????????????????????????????????XY
                X1 = int(o.bounding_box.left* imageWidth)
                Y1 = int(o.bounding_box.top * imageheigh)
                X2 = int(o.bounding_box.width* imageWidth + X1)
                Y2 = int(o.bounding_box.height * imageheigh + Y1)
                title =o.tag_name + ": {:.2%}".format(o.probability) #?????????????????????title??????
                 #?????????????????????????????????????????? 
                cv2.rectangle(image, (X1,Y1), (X2,Y2), color , thickness)    
                cv2.putText(image, str(title) ,(X1-20, Y1-20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.9, (0, 0, 225), 1, cv2.LINE_AA)
                
                str_title = [title]#??????str_title???title?????????????????????????????????
                for i in str_title:#??????for??????????????????????????????????????????????????????list
                    list.append(i)
        
        str_list = ', '.join(list)#???list????????????

        print('====================')


        # Displaying the image  
        # cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        #save image to file
        cv2.imwrite('C:\\Users\\Tibame\\Desktop\\Programming\\Azure\\output.jpg', image)        
        
        #imgur
        CLIENT_ID = "030a355399d5d25"
        PATH = "C:\\Users\\Tibame\\Desktop\\Programming\\Azure\\output.jpg" #A Filepath to an image on your computer"

        im = pyimgur.Imgur(CLIENT_ID)
        uploaded_image = im.upload_image(PATH)

    print(uploaded_image.link)#get url
    print('msg from [', user_name, '](', user_id, ') : ',uploaded_image.link)
    
    line_bot_api.reply_message(event.reply_token, 
                            [TextSendMessage(text = str_list),
                                ImageSendMessage(original_content_url=uploaded_image.link, 
                                                preview_image_url=uploaded_image.link),
    
                                ])



# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345) 