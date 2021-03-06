import praw, re, pytz, yaml, threading, requests, json, base64
import os
import psycopg2
from datetime import datetime
from bs4 import BeautifulSoup
import random 
import urllib.parse



def getConfigHeroku(key):
    result = os.environ.get(key,'None')
    return result

reddit = praw.Reddit(client_id=getConfigHeroku('clientid'), client_secret=getConfigHeroku('secret'),
                     password=getConfigHeroku('password'), user_agent=getConfigHeroku('agent'),
                     username=getConfigHeroku('username'))


def imageSearch(memeName):
    my_list = [googleSearch]
    result = random.choice(my_list)(memeName)      
    if(len(result)==0):
        result = googleSearch(memeName)      
    return result

def googleSearch(searchText) :
    searchText = searchText.split()
    searchText = ("+").join(searchText)
    url = 'https://www.google.com/search?q=' + searchText + '&tbm=isch'
    try:
        response = requests.get(url)    
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for link in soup.find_all('a'):
            links.append(link.get('href'))

        source = links[14]
        i=1

        while "search" in source or "discover" in source or "pinterest" in source or "metro" in source or "explore" in source:
            source = links[14 + i]
            i=i+1
        
        source=source[7:]
        source_array = source.split('&')
        resurl = source_array[0]
        response = requests.get(resurl)    
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find_all('title')
        titletext = title[0].contents[0].split("GIF")[0].split("gif")[0]
        meme = {"title":titletext, "url":resurl , "source":"Google"}
        return [meme]
    except:
      return []   

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

def giphySearchStickers(searchText):
    giphySearchUrl = "https://api.giphy.com/v1/stickers/search?api_key="+getConfigHeroku('GiphyAuth')+"&limit=1&q="
    giphyQuery = searchText
    giphySearchUrl = giphySearchUrl + giphyQuery
    try:        
        giphyResponse = requests.get(giphySearchUrl)        
        data = giphyResponse.json()["data"][0]
        meme = {"title":data["title"], "url": data["url"], "source":"Giphy"}
        return [meme]
    except:
        return []

def giphySearchGifs(searchText):
    giphySearchUrl = "https://api.giphy.com/v1/gifs/search?api_key="+getConfigHeroku('GiphyAuth')+"&limit=1&q="
    giphyQuery = searchText
    giphySearchUrl = giphySearchUrl + giphyQuery
    try:        
        giphyResponse = requests.get(giphySearchUrl)        
        data = giphyResponse.json()["data"][0]
        meme = {"title":data["title"], "url": data["url"], "source":"Giphy"}
        return [meme]
    except:
        return []

def AddReply(results, comment, author, searchText, textArray):    
    if results[0]["title"] == "":
        results[0]["title"] = searchText
    comdText = " ".join(textArray)
    reply = ">{} \n\n [{}]({}) by u/{}  ".format(comdText, results[0]["title"],results[0]["url"],author)    
    try:
        if comment is not None:
            if("t3" in comment.parent_id):
                comment.reply(reply)                 
            else:
                reddit.comment(comment.parent()).reply(reply)
            conn = psycopg2.connect(getConfigHeroku('dbConnString'))
            cur = conn.cursor()
            sql = "INSERT INTO tblcommentsbybot(comment_id,author,reply,added_on,searchtext) VALUES('"+comment.id+"','"+author+"','"+reply+"','"+str(datetime.now())+"','"+searchText+"');"
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
    except(Exception) as error :
        print (error)

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
    except(Exception) as error :
        print (error)

def georgeThreadCommentsListener():
    sub = getConfigHeroku('sub')
    subreddit = reddit.subreddit(sub)
    pattern1 = r"\b(.|\n)*(i|I)nsert (.)*\b" 
    
    while True:
        for comment in subreddit.stream.comments():
            if(comment.submission.author is None):
            # or (comment.submission.author.name != getConfigHeroku('author'))):
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
                    commentTemp = commentRequest.replace("\n\n", " ").replace("."," . ").replace("*","")
                    comment_token = commentTemp.split(" ")
                    
                    if(match1):
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
                            results = imageSearch(memeName)
                            if(len(results) != 0):
                                AddReply(results, comment, comment.author.name, memeName, memeArray)     
                            # else:
                            #     AddEmptyReply(memeName, comment, comment.author.name)       
                        except(Exception) as error :
                            print (error)
            except (Exception, psycopg2.Error) as error :
                print ("Error while fetching data from PostgreSQL", error)     
            

def main():    
    thread = {"georgeThreadCommentsListener": threading.Thread(target = georgeThreadCommentsListener)}
    for thread in thread.values():
        thread.start()

if __name__ == "__main__":    
    main()  
