import praw, re, time, pytz, yaml, threading, requests, json, base64
import os
from datetime import date
import psycopg2


def getConfigHeroku(key):
    result = os.environ.get(key,'None')
    return result

reddit = praw.Reddit(client_id=getConfigHeroku('clientid'), client_secret=getConfigHeroku('secret'),
                     password=getConfigHeroku('password'), user_agent=getConfigHeroku('agent'),
                     username=getConfigHeroku('username'))


def imageSearch(memeName):
    result = giphySearch(memeName,"gifs")        
    if(len(result) == 0):
        result = imgurSearch(memeName)
        if(len(result) == 0):
         result = giphySearch(memeName,"stickers")           
    return result
       

def imgurSearch(searchText):
    print('imgur search started for text: '+searchText)
    imgurSearchUrl = "https://api.imgur.com/3/gallery/search/top/all/1?q=" 
    imgurAccessHeader = {"Accept": "application/json", "Content-Type": "application/json","Authorization": getConfigHeroku('ImgurAuth')}
    imgurQuery = searchText
    imgurSearchUrl = imgurSearchUrl + imgurQuery
    print(imgurSearchUrl)
    try:
      imgurResponse = requests.get(imgurSearchUrl,headers=imgurAccessHeader)
      data = imgurResponse.json()["data"][0]
      meme = {"title":data["title"], "url": data["link"]}
      print("New Reply: "+json.dumps(meme))
      return [meme]
    except:
      print("not found on imgur: "+searchText)
      return []

def giphySearch(searchText,searchType):
    print('giphy search started for type: '+searchType+" and text: "+searchText)
    giphySearchUrl = "https://api.giphy.com/v1/"+searchType+"/search?api_key="+getConfigHeroku('GiphyAuth')+"&limit=1&q="
    giphyQuery = searchText
    giphySearchUrl = giphySearchUrl + giphyQuery
    print(giphySearchUrl)
    try:        
        giphyResponse = requests.get(giphySearchUrl)        
        data = giphyResponse.json()["data"][0]
        meme = {"title":data["title"], "url": data["url"]}
        print("New Reply: "+json.dumps(meme))
        return [meme]
    except:
        print("not found on giphy for type: "+ searchType)
        return []

def AddReply(results, comment, author):    
    reply = "[{}]({})\n\n  ".format(results[0]["title"],results[0]["url"])    
    try:
        if comment is not None:
            comment.reply(reply) 
            conn = psycopg2.connect(getConfigHeroku('dbConnString'))
            cur = conn.cursor()
            sql = """INSERT INTO tblcommentsbybot(comment_id,author,reply,added_on) VALUES(%s,%s,%s,%s);"""
            record_to_insert = (comment.id, author, reply, now.strftime("%d-%m-%Y %H:%M:%S"))
            cur.execute(sql,record_to_insert)
            conn.commit()
            cur.close()
            conn.close()
    except:
        return []

def AddEmptyReply(searchText, comment):    
    reply = "Sorry! I could not find anything related to the words *'"+searchText+"'*\n\n Could you try rephrasing please?" 
    try:
        if comment is not None:
            comment.reply(reply)
            fh = open("commented.txt","a")
            fh.write(comment.id)
            fh.write("\n")     
            fh.close() 
    except:
        return []

def georgeSubListener():
    print('George is listening now!')
    sub = getConfigHeroku('sub')
    subreddit = reddit.subreddit(sub)
    while True:        
        for submission in subreddit.stream.submissions():
            print(submission.title)
            subToReplyIn = getConfigHeroku('threadTitle')
            author = getConfigHeroku('author')
            matchsub = re.search(subToReplyIn, submission.title)
            if matchsub and submission.author == author: 
                print("submission found!")       
                georgeThreadCommentsListener(submission.id)

def georgeThreadCommentsListener(submissionID):
    sub = getConfigHeroku('sub')
    subreddit = reddit.subreddit(sub)
    pattern1 = r"\b(.|\n)*(g|G)eorge (a|A)dd (.)*\b" 
    
    for comment in subreddit.stream.comments():
        if(comment.submission.id != submissionID):
            continue
        conn = psycopg2.connect(getConfigHeroku('dbConnString'))
            cur = conn.cursor()
            sql = "SELECT comment_id from tblcommentsbybot where comment_id="+comment.id+";"
            cur.execute(sql)
            records = cursor.fetchall() 
            conn.commit()
            cur.close()
            conn.close()

        if comment.id not in records:
            print("comment found!") 
            match1 = re.search(pattern1, comment.body)
            commentRequest = comment.body.lower()
            commentTemp = commentRequest.replace("\n\n", " ")
            comment_token = commentTemp.split(" ")
            
            if(match1):
                print("match found!") 
                memeArray = comment_token[comment_token.index("george") + 2:]
                memeName = " ".join(memeArray)
            
                try:
                    print("attempting to search:"+memeName) 
                    results = imageSearch(memeName)
                    if(len(results) != 0):
                        AddReply(results, comment, comment.author)     
                    else:
                        AddEmptyReply(memeName, comment, comment.author)                                      
                    time.sleep(10)                    
                except:
                    return []       


def main():    
    thread = {"georgeSubListener": threading.Thread(target = georgeSubListener)}
    for thread in thread.values():
        thread.start()

if __name__ == "__main__":    
    main()  
