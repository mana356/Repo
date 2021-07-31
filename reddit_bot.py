import praw, re, yaml, threading, requests
import os
from datetime import datetime
import urllib.parse


def load_config(config_file):
    with open(config_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

config = load_config('config.yml')

reddit = praw.Reddit(client_id=config['id'], client_secret=config['secret'],
                     password=config['password'], user_agent=config['agent'],
                     username=config['username'])


def splashSearch(searchText, israndom):
    if(israndom):
        splashSearchUrl = "https://api.unsplash.com/photos/random"
    else:
        splashSearchUrl = "https://api.unsplash.com/search/photos?page=1&query="+ searchText
    splashAccessHeader = {"Accept": "application/json", "Content-Type": "application/json","Authorization": "Client-ID "+ config['SplashAuth']}
    try:
      splashResponse = requests.get(splashSearchUrl,headers=splashAccessHeader)
      if(israndom):
          data = splashResponse.json()
      else:
          data = splashResponse.json()["results"][0]

      urls = data['urls']
      meme = {
          "title":  data["description"] if data["description"] is not None else data["alt_description"] , 
          "url": urls["full"], 
          "source":"Splash"
          }
      return [meme]
    except(Exception) as error :
        print (error)
        return []

def imgurSearch(searchText):
    imgurSearchUrl = "https://api.imgur.com/3/gallery/search/top/all/1?q=" 
    imgurAccessHeader = {"Accept": "application/json", "Content-Type": "application/json","Authorization": config['ImgurAuth']}
    imgurQuery = searchText
    imgurSearchUrl = imgurSearchUrl + imgurQuery
    try:
      imgurResponse = requests.get(imgurSearchUrl,headers=imgurAccessHeader)
      data = imgurResponse.json()["data"][0]
      meme = {"title":data["title"], "url": data["link"], "source":"Imgur"}
      return [meme]
    except:
      return []

def AddReply(results, comment, author, searchText, textArray):    
    if results[0]["title"] == "":
        results[0]["title"] = searchText
    comdText = " ".join(textArray)
    reply = ">{} \n\n [{}]({})".format(comdText, results[0]["title"],results[0]["url"])    
    try:
        if comment is not None:
            if("t3" in comment.parent_id):
                comment.reply(reply)                 
            else:
                reddit.comment(comment.parent()).reply(reply)
            with open ("comments_replied_to.txt", "a") as f:
                f.write(comment.id + "\n")            
    except(Exception) as error :
        print (error)

def AddEmptyReply(searchText, comment, author):    
    reply = "Sorry! I could not find anything related to the words *'"+searchText+"'*\n\n Could you try rephrasing please?" 
    try:
        if comment is not None:
            comment.reply(reply)
            
    except(Exception) as error :
        print (error)

def threadCommentsListener():
    sub = config['sub']
    subreddit = reddit.subreddit(sub)
    pattern1 = r"\b(.|\n)*(i|I)nsert (.)*\b" 
    pattern2 = r"\b(.|\n)*(i|I)nsert a random one(.)*\b"
    comments_replied_to = get_saved_comments()
    while True:
        for comment in subreddit.comments(limit=1000):
            if(comment.submission.author is None or comment.submission.author.name != config['author']):
                print(comment.body)
                print(datetime.fromtimestamp(comment.created_utc))
                continue
            try:
                if comment.id not in comments_replied_to:
                    match1 = re.search(pattern1, comment.body)
                    match2 = re.search(pattern2, comment.body)
                    commentRequest = comment.body.lower()
                    commentTemp = commentRequest.replace("\n\n", " ").replace("."," . ").replace("*","")
                    comment_token = commentTemp.split(" ")
                    print(comment.body)
                    print(comment_token)                        
                          
                    if(match2):
                        print('match found')
                        memeArray = comment_token[comment_token.index("insert") + 1:]
                        lastItem = len(comment_token)-1
                        if "." in memeArray:
                            lastItem = memeArray.index(".")
                        
                        memeArray = memeArray[:lastItem]
                        
                        memeName = " ".join(memeArray)
                        print(memeName)
                        try:
                            if comment.author is None:
                                continue       
                            memeName = urllib.parse.quote(memeName)                 
                            results = splashSearch(memeName, True)
                            if(len(results) != 0):
                                AddReply(results, comment, comment.author.name, memeName, memeArray)     
                            # else:
                            #     AddEmptyReply(memeName, comment, comment.author.name)       
                        except(Exception) as error :
                            print (error)      

                    elif(match1):
                        print('match found')
                        memeArray = comment_token[comment_token.index("insert") + 1:]
                        lastItem = len(comment_token)-1
                        if "." in memeArray:
                            lastItem = memeArray.index(".")
                        
                        memeArray = memeArray[:lastItem]
                        
                        memeName = " ".join(memeArray)
                        print(memeName)
                            
                        
                        try:
                            if comment.author is None:
                                continue       
                            memeName = urllib.parse.quote(memeName)                 
                            results = splashSearch(memeName, False)
                            if(len(results) != 0):
                                AddReply(results, comment, comment.author.name, memeName, memeArray)     
                            # else:
                            #     AddEmptyReply(memeName, comment, comment.author.name)       
                        except(Exception) as error :
                            print (error) 
            except (Exception) as error :
                print ("Error while fetching data from PostgreSQL", error)      
            
def get_saved_comments():
	if not os.path.isfile("comments_replied_to.txt"):
		comments_replied_to = []
	else:
		with open("comments_replied_to.txt", "r") as f:
			comments_replied_to = f.read()
			comments_replied_to = comments_replied_to.split("\n")
			comments_replied_to = filter(None, comments_replied_to)

	return comments_replied_to

def main():    
    thread = {"threadCommentsListener": threading.Thread(target = threadCommentsListener)}
    for thread in thread.values():
        thread.start()

if __name__ == "__main__":    
    main()  
