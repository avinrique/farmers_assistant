import requests
from bs4 import BeautifulSoup
from datetime import date
import re
import geocoder
import google.generativeai as genai
g = geocoder.ip('me')
from geopy.geocoders import Nominatim
from time import sleep
import copy

#getting city location using ip address 
geolocator = Nominatim(user_agent="GetLSystemsoc")
location = geolocator.reverse((g.latlng[0], g.latlng[1]))
city = None
address_components = location.raw.get("address", {})
if "city" in address_components:
    city = address_components["city"]
elif "town" in address_components:
    city = address_components["town"]
elif "village" in address_components:
    city = address_components["village"]

#configuring genai and checking the avilable models
genai.configure(api_key="AIzaSyCRUpuFm2Nc17FbHNL-Fv-zNeogCDlqKBg")
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)
model = genai.GenerativeModel('gemini-pro')

#chat history 
chat = model.start_chat(history=[])


#initialing headers and checking statuscode
def get_page_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch page content from {url}: {e}")
        return None

#extracting page content 
def extract_text_from_page(page_soup):

    elements_to_extract = ['p', 'ul', 'h1', 'h2', 'h3' ,'h4' ,'h5', ]
    page_text = ""

    for element_name in elements_to_extract:
        elements = page_soup.find_all(element_name)
        for element in elements:
            page_text += element.get_text() + "\n"

    return page_text

#a google search query
def google_search(query ,base_url):
   
    params = {"q": query ,  "near": location.address}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(base_url, params=params, headers=headers)

    if response.status_code == 200:
        
        soup = BeautifulSoup(response.text, "html.parser")

        search_results = []
        for result in soup.find_all("div", class_="tF2Cxc"):
            title_element = result.find("h3")
            link_element = result.find("a")

            if title_element and link_element and "href" in link_element.attrs:
                title = title_element.get_text()
                link = link_element["href"]

                page_content = get_page_content(link)
                if page_content:
                    page_soup = BeautifulSoup(page_content, "html.parser")
                    page_text = extract_text_from_page(page_soup)

                    search_results.append({"title": title, "link": link, "page_text": page_text})
            else:
                print("Skipping result due to missing information.")

        return search_results
    else:
        print(f"Failed to fetch results. Status code: {response.status_code}" , f"blocked by  {base_url}")
        google_search(query=query ,  base_url="https://api.duckduckgo.com/?q=<your search string>&format=json&pretty=1&no_html=1&skip_disambig=1")

#initialising the 2 prompts
chat.send_message(f"todays date is {date.today()} and my loaction is {location.address} and my name is avinav gupta , i am a student of bmsit banglore 3rd sem , my hobbies are playing basketball ,chess , call of duty and other games , reading books novels and books on pschyology , i am a programmer i know python , js well. i know a bit of java and c . i know a webdevlopment , a bit of penetration testing a, script writing , prompt engineering , a very very bit of app and game developemnt and 3d modeling , and i am trying to learn ai, i know how to program raspberry pi and i know linux . i also know a bit of automation. well i am a kinda guy who likes to learn new things. and i am from nepal born in katmandu and lived in biratnagar, you will address me as a boss and i will address you as ryan" , safety_settings={'HARASSMENT':'block_none'})
chat.send_message(f"you are also a helpful assistant that helps me in my most of the works , answer like you are jarvis ")


while True :
    prompt =  input("say : ")
    while prompt == "" or prompt == " ":
        prompt = input("say : ")
    # classifying the prompt for realtimedata or not
    response = model.generate_content(f"""if the prompt is related to realtime data or current affairs or current news, 
                                          then say strictly yes and if no say no
                                          here to make you clear what might be realtime data are '
                                          if asked about price of something , political learders or current news or ongoing events anywhere or weather or upcoming or releasing movies '
                                          ,and to make sure you dont say yes to everything ,
                                          and if  asked to look for something in interet or search for something in internet then return "intquery"
                                          where the prompt : {prompt} """)
    print(response.text)
    
    if response.text.lower() == "yes"  :
       # converting prompt to query 
       rep2 = model.generate_content(f"""suppose you are a google search query bot and your work is to omptimise the prompt given by the user in such a way that google can use that 
                                     search query to get the desired result and you give the a single search query,
                                     an example for this is  if a prompt is ' hey yo whats the price of silver in my country ' 
                                     and query is ' silver price today ',
                                     strictly convert the given prompt to the query well todays date is {date.today()} and my location is {city}
                                     where the prompt by user is : {prompt} """)
       testrep = model.generate_content("if you know any popular website related to this propmt then give me the list of website in json format , where the prompt is {rep2}, if you dont know any website than ,just give a empy json")
       print(testrep.text)
       #rep2 = model.generate_content(f"just convert the given prompt to google search query that can be used to get desire results from the google search,
        #                              just a single search query ,
         #                             where the prompt is prompt : ''' {prompt} '''  " ,generation_config=genai.types.GenerationConfig(
        #temperature=0.4))
       #removing unwanted charaters from query
       rep2 = re.sub(r"\*\*Search Query:\*\*.*$", "", rep2.text)
       rep2 = re.sub(r"\*\*\*\*.*$", "", rep2)
       rep2 = re.sub(r'Search Query:','', rep2)
       rep2 = re.sub(r'Query:','', rep2)

       print(rep2)
       search_query = rep2
       #calling google search function with google
       results = google_search(search_query,base_url="https://www.google.com/search")
       all_text = ""
       if results:
          for idx, result in enumerate(results, 1):
              all_text += f"\nResult #{idx}\n"
              all_text += f"Title: {result['title']}\n"
              all_text += f"Link: {result['link']}\n"
              all_text += f"Page Text:\n{result['page_text']}\n\n"
              rep3 = model.generate_content(f" there are two prompt i.e. prompt 1 ''' {prompt} ''' and prompt 2 ''' {rep2} ''' , they are basically the same question as a prompt and would have the same answer,so according to these prompt try to answer from the text where the text is '''{result}''' well if you didn't find the asnwer in the text just strictky return 'negative' , well if you do find the answer then also try to return its unit , quantity , measurement or rate  if its givven there.   ")
                    
              #rep3 = model.generate_content(f" answer ''' {rep2} ''' accordingly to the text where the text is  :''' {result} '''well if you didn't find the asnwer in the text just strictky return 'negative' , well if you do find the answer then also try to return its unit , quantity , measurement or rate  if its givven there.  ")
              #rep4 = model.generate_content(f" answer ''' {prompt} ''' accordingly to the text where the text is  :''' {result} '''well if you didn't find the asnwer in the text just strictky return 'negative' , well if you do find the answer then also try to return its unit , quantity , measurement or rate  if its givven there.  ")
              

              with open('mod.txt' ,'a') as f :
                  f.write(f"---------------------------------------------------------------\n{all_text}\n----------------------------------------------------------")     
              if rep3.text.lower() != 'negative' and rep3.text.lower() != "":
            #  if rep3.text.lower() != 'negative' or rep3.text.lower() != "" ''' or rep4.text.lower() != 'negative ''' :
                 # if rep3.text.lower() != 'negative'  or rep3.text.lower() != ""  :
                  k = copy.deepcopy(chat.history[0])
                  l = copy.deepcopy(chat.history[1])
                  chat.history.insert(len(chat.history),k)
                  chat.history[len(chat.history)-1].role = "user"
                  chat.history[len(chat.history)-1].parts[0].text = f" there are two prompt i.e. prompt 1 ''' {prompt} ''' and prompt 2 ''' {rep2} ''' , they are basically the same question as a prompt and would have the same answer,so according to these prompt try to answer from the text where the text is '''{result}''' well if you didn't find the asnwer in the text just strictky return 'negative' , well if you do find the answer then also try to return its unit , quantity , measurement or rate  if its givven there.   "
                  chat.history.insert(len(chat.history),l)
                  chat.history[len(chat.history)-1].role = "model"
                  chat.history[len(chat.history)-1].parts[0].text = rep3.text
                  print(rep3.text)
                 # if rep4.text.lower() != 'negative' :
                  #    print(rep4.text) 
                  print(result['link'])
                  break
              elif(rep3.text.lower()=="") :
                  print("cannot get answer from the source")
                  pass
              else :
                  print("negetive")
              

              all_text = ""

      # rep3 = model.generate_content(f"answer {prompt} according to the text where the text is  :''' {all_text} '''")
       #rep3 = model.generate_content(f"go through the data from the scraped web properly and from the given data answer the prompt ccorrectly , where the data from scraped web is  **** {all_text} **** and the prompt is '{prompt}' ,well but go through the text properly because the answer of the prompt is there , the text there is a google search results and you need to find the answer from the text ")
    #checking in prompt for search query
    elif response.text.lower() == "intquery" :
        rep2 = model.generate_content(f"""suppose you are a google search query bot and your work is to omptimise the prompt given by the user in such a way that google can use that 
                                     search query to get the desired result and you give the a single search query,
                                      if its a name of a man then just prompt name and if additional information is given then just add it to the query or if other things are given to look then do according to you
                                     where the prompt by user is : {prompt} """)
       

       #rep2 = model.generate_content(f"just convert the given prompt to google search query that can be used to get desire results from the google search,
        #                              just a single search query ,
         #                             where the prompt is prompt : ''' {prompt} '''  " ,generation_config=genai.types.GenerationConfig(
        #temperature=0.4))
       
        rep2 = re.sub(r"\*\*Search Query:\*\*.*$", "", rep2.text)
        rep2 = re.sub(r"\*\*\*\*.*$", "", rep2)
        rep2 = re.sub(r'Search Query:','', rep2)
        rep2 = re.sub(r'Query:','', rep2)
        print(rep2)
        search_query = rep2
        results = google_search(search_query , base_url="https://www.google.com/search")
        all_text = ""

        if results:
           for idx, result in enumerate(results, 1):
               all_text += f"\nResult #{idx}\n"
               all_text += f"Title: {result['title']}\n"
               all_text += f"Link: {result['link']}\n"
               all_text += f"Page Text:\n{result['page_text']}\n\n"
               rep3 = model.generate_content(f" tell about''' {rep2} ''' in short accordingly to the text where the text is  :''' {result} '''well if you didn't find the asnwer in the text just strictky return 'negative' , if you do get  results then explain in short about it")
               
               with open('mod.txt' ,'a') as f :
                  f.write(f"---------------------------------------------------------------\n{all_text}\n----------------------------------------------------------")     

               if rep3.text.lower() != 'negative'  and rep3.text.lower() != "":
                  k = copy.deepcopy(chat.history[0])
                  l = copy.deepcopy(chat.history[1])
                  chat.history.insert(len(chat.history),k)
                  chat.history[len(chat.history)-1].role = "user"
                  chat.history[len(chat.history)-1].parts[0].text = f" there are two prompt i.e. prompt 1 ''' {prompt} ''' and prompt 2 ''' {rep2} ''' , they are basically the same question as a prompt and would have the same answer,so according to these prompt try to answer from the text where the text is '''{result}''' well if you didn't find the asnwer in the text just strictky return 'negative' , well if you do find the answer then also try to return its unit , quantity , measurement or rate  if its givven there.   "
                  chat.history.insert(len(chat.history),l)
                  chat.history[len(chat.history)-1].role = "model"
                  chat.history[len(chat.history)-1].parts[0].text = rep3.text
                  print(rep3.text)
                  print(result['link'])
                  break
               else :
                  print("negetive")
              

               all_text = ""        
    else :
       rep2 = chat.send_message(prompt, stream=True)
       for chunk in rep2:
            print(chunk.text)




    '''
    response = model.generate_content(f"""if i ask you a question about real time data like price of something or current affairs or current news only then convert the prompt to a google search , and if the prompt is not about realtime data or current news or current affairs and you have some info a about the prompt then give your usual results as you give , here  i made  a dailog where im the  user and you are gemini and you are supposed to answer like gemini  given below in the dailouge, you are not supposed to  adapt to the way gemini answer the user query,
                                      

                                      The Dialouge 

                                      user   :  whats the price of bitcoin 
                                      gemini :  price of bitcoin ---query--- $catagory price
                                      user   :  hey whats up?
                                      gemini :  i am good.what about you? 
                                      user   :  whose prime minister of nepal right now?
                                      gemini :  prime minister of nepal ---query--- $catagory current afairs
                                      user   :  humour me 
                                      gemini :  okey boss ! How about a quick joke ? 
                                                Why don't scientists trust atoms?
                                                Because they make up everything!
                                      user   :  give me some tips for imporving my english 
                                      gemini :  Certainly! Improving your English can be a rewarding journey. Here are some tips to help you enhance your English skills:

                                                Read Regularly:

                                                Read a variety of materials, including books, newspapers, articles, and online content. This exposure to different writing styles and vocabulary will broaden your language skills.
                                                Expand Your Vocabulary:

                                                Learn new words every day and try to use them in your conversations and writing. You can use vocabulary-building apps, flashcards, or simply keep a word journal.
                                                Watch English Movies and TV Shows:

                                                Watching movies and TV shows in English is an enjoyable way to improve your listening skills and get accustomed to various accents and colloquial expressions.
                                                Practice Speaking:

                                                Engage in conversations with native speakers or language exchange partners. This will improve your pronunciation, fluency, and overall communication skills.
                                                Use Language Learning Apps:

                                                There are many apps designed to help you learn and practice English. Duolingo, Babbel, and Memrise are popular choices for language learners.
                                                Write Regularly:

                                                Keep a journal, write essays, or start a blog in English. Regular writing practice will enhance your grammar, sentence structure, and overall writing proficiency.
                                                Join Language Learning Communities:

                                                Online forums, social media groups, or local language exchange meetups can provide opportunities to interact with other learners and native speakers.
                                                Listen to Podcasts:

                                                Listening to English podcasts on topics that interest you is a great way to improve your listening skills and expose yourself to diverse accents and vocabulary.
                                                Take Formal English Classes:

                                                If possible, consider enrolling in English language classes. This can provide structured learning, feedback from instructors, and a supportive environment for improvement.
                                                Set Realistic Goals:

                                                Set achievable language learning goals for yourself. This could be mastering a certain number of new words each week or maintaining a conversation for a specific duration without struggling.
                                                Be Patient and Persistent:

                                                Learning a language takes time and effort. Celebrate your progress, no matter how small, and stay motivated.
                                                Remember, consistency is key. Incorporate these tips into your daily routine, and you'll likely see improvement over time. Good luck with your English language journey!
                                      user   :  whats quantum mechanics?
                                      gemini :  A black hole is a region in space where gravity is so strong that nothing—no particles or even electromagnetic radiation such as light—can escape from it. The boundary surrounding a black hole is called the event horizon. Once anything crosses this boundary, it is pulled inexorably towards the center of the black hole, a point of infinite density called a singularity.
                                                The concept of black holes comes from the theory of general relativity, proposed by Albert Einstein. Black holes can form when massive stars run out of fuel and collapse under their own gravity. There are also supermassive black holes that exist at the centers of most galaxies, including our Milky Way.
                                                The characteristics of black holes can be fascinating and include time dilation (time passing more slowly near a black hole), extreme gravitational forces, and the possibility of spaghettification—a stretching and elongation of objects as they get closer to the singularity due to the increasing gravitational pull.
                                                Despite their name, black holes are not "holes" in space; rather, they are incredibly dense objects with gravity so intense that nothing can escape once it crosses a certain point. While black holes themselves are invisible, their presence can be inferred by observing the effects they have on nearby matter and light.                 


                                      
                                      Now you are supposed to answer like the way gemini is answering to the user  ,where the prompt is ,
                                      user  : {prompt}  """ , stream=True)
    for chunk in response:
        print(chunk.text)
'''
