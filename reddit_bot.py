import praw, re, pytz, yaml, threading, requests, json, base64
import os
import psycopg2
from datetime import datetime


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
    imgurSearchUrl = "https://api.imgur.com/3/gallery/search/top/all/1?q=" 
    imgurAccessHeader = {"Accept": "application/json", "Content-Type": "application/json","Authorization": getConfigHeroku('ImgurAuth')}
    imgurQuery = searchText
    imgurSearchUrl = imgurSearchUrl + imgurQuery
    try:
      imgurResponse = requests.get(imgurSearchUrl,headers=imgurAccessHeader)
      data = imgurResponse.json()["data"][0]
      meme = {"title":data["title"], "url": data["link"], "source":"Imgur"}
      return [meme]
    except:
      return []

def giphySearch(searchText,searchType):
    giphySearchUrl = "https://api.giphy.com/v1/"+searchType+"/search?api_key="+getConfigHeroku('GiphyAuth')+"&limit=1&q="
    giphyQuery = searchText
    giphySearchUrl = giphySearchUrl + giphyQuery
    try:        
        giphyResponse = requests.get(giphySearchUrl)        
        data = giphyResponse.json()["data"][0]
        meme = {"title":data["title"], "url": data["url"], "source":"Giphy"}
        return [meme]
    except:
        return []

def AddReply(results, comment, author, searchText):    
    reply = "[{}]({})\n\n ^(Results fetched from {})  ".format(results[0]["title"],results[0]["url"],results[0]["source"])    
    try:
        if comment is not None:
            comment.reply(reply) 
            conn = psycopg2.connect(getConfigHeroku('dbConnString'))
            cur = conn.cursor()
            sql = "INSERT INTO tblcommentsbybot(comment_id,author,reply,added_on,searchtext) VALUES('"+comment.id+"','"+author+"','"+reply+"','"+str(datetime.now())+"','"+searchText+"');"
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

def AddEmptyReply(searchText, comment, author):    
    reply = "Sorry! I could not find anything related to the words *'"+searchText+"'*\n\n Could you try rephrasing please?" 
    try:
        if comment is not None:
            comment.reply(reply)
            conn = psycopg2.connect(getConfigHeroku('dbConnString'))
            cur = conn.cursor()
            sql = "INSERT INTO tblcommentsbybot(comment_id,author,reply,added_on,searchtext) VALUES('"+comment.id+"','"+author+"','"+reply+"','"+str(datetime.now())+"','"+searchText+"');"
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close() 
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

def()

def georgeThreadCommentsListener():
    sub = getConfigHeroku('sub')
    subreddit = reddit.subreddit(sub)
    pattern1 = r"\b(.|\n)*(g|G)eorge (a|A)dd (.)*\b" 
    
    while True:
        for comment in subreddit.stream.comments():
            if((comment.submission.author is None) or (comment.submission.author.name != getConfigHeroku('author'))):
                continue
            try:
                conn = psycopg2.connect(getConfigHeroku('dbConnString'))
                cur = conn.cursor()
                sql = "SELECT comment_id from tblcommentsbybot where comment_id='"+comment.id+"';"
                cur.execute(sql)
                records = cur.fetchone() 
                conn.commit()
                cur.close()
                conn.close()

                if records is None:
                    match1 = re.search(pattern1, comment.body)
                    commentRequest = comment.body.lower()
                    commentTemp = commentRequest.replace("\n\n", " ")
                    comment_token = commentTemp.split(" ")
                    
                    if(match1):
                        memeArray = comment_token[comment_token.index("george") + 2:]
                        memeName = " ".join(memeArray)
                    
                        try:
                            if comment.author is None:
                                continue                        
                            results = imageSearch(memeName)
                            if(len(results) != 0):
                                AddReply(results, comment, comment.author.name, memeName)     
                            else:
                                AddEmptyReply(memeName, comment, comment.author.name)                                      
                            time.sleep(10)                    
                        except:
                            return [] 
            except (Exception, psycopg2.Error) as error :
                print ("Error while fetching data from PostgreSQL", error)      
            except:
                print("Unexpected error:", sys.exc_info()[0])

def main():    
    thread = {"georgeThreadCommentsListener": threading.Thread(target = georgeThreadCommentsListener)}
    for thread in thread.values():
        thread.start()

if __name__ == "__main__":    
    main()  
