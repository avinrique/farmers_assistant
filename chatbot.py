import google.generativeai as genai
genai.configure(api_key="AIzaSyCRUpuFm2Nc17FbHNL-Fv-zNeogCDlqKBg")
model = genai.GenerativeModel('gemini-pro')
#chat history 
chat = model.start_chat(history=[])
chat.send_message("Suppose you are now a chatbot designed to answer the question regarding farming, now the one who askes the question is the farmer and the farmer might ask few questions reqarding anything about the farming or farm , you are supposeed to answer the questions , now in upcoming prompts he may ask the question")
chat.send_message("""the crops / plants that the farmer is growing in his field are tomatos , potatos and spinich , the mositure of soil for those plants are { tomato : 100% , potato : 50% , spinich : 20% }. """)
# prompt  =  "what are the crops in my field"
count = 2
while True :
    prompt =  input("Ask the assistant")
    a = chat.send_message(f""" Is the given prompt about the plants of the farmers field ,like the plants he grows about their health and all Any thing that basically grows in his farm and the question is regarding the items growing in the farm then just reply with '''yes''' and nothing else otherwise reply with '''no''' , here the prompt is {prompt}  """)
    print(chat.history)
    chat.history.pop(-1)
    print("------------------------------------")
    print(chat.history)
    b = a.text
    print(a.text)
    if "yes" in str(b).lower() :
        print(chat.send_message(prompt).text)
        count += 1
    else :
        print("not about the crops")

# print(a.text)
# chat.send_message(f""" """ , safety_settings={'HARASSMENT':'block_none'})