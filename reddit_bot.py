import praw, re, time, pytz, yaml, threading, requests, logging, json, base64
from datetime import date

today = date.today()
fname = "BotLogFile_" + today.strftime("%b-%d-%Y") + ".log"

logging.basicConfig(filename=fname, 
                    format='%(asctime)s %(message)s', 
                    filemode='w')

logger=logging.getLogger() 
logger.setLevel(logging.DEBUG)

def load_config(config_file):
    with open(config_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.debug("Config not found! | error: "+exc) 

config = load_config('config.yml')

reddit = praw.Reddit(client_id=config['id'], client_secret=config['secret'],
                     password=config['password'], user_agent=config['agent'],
                     username=config['username'])

def imageSearch(memeName):
    result = giphySearch(memeName,"gifs")        
    if(len(result) == 0):
        result = imgurSearch(memeName)
        if(len(result) == 0):
         result = giphySearch(memeName,"stickers")           
    return result
       

def imgurSearch(searchText):
    logger.info('imgur search started for text: '+searchText)
    imgurSearchUrl = "https://api.imgur.com/3/gallery/search/top/all/1?q=" 
    imgurAccessHeader = {"Accept": "application/json", "Content-Type": "application/json","Authorization": config['ImgurAuth']}
    imgurQuery = searchText
    imgurSearchUrl = imgurSearchUrl + imgurQuery
    logger.info(imgurSearchUrl)
    try:
      imgurResponse = requests.get(imgurSearchUrl,headers=imgurAccessHeader)
      data = imgurResponse.json()["data"][0]
      meme = {"title":data["title"], "url": data["link"]}
      logger.info("New Reply: "+json.dumps(meme))
      return [meme]
    except:
      logger.info("not found on imgur: "+searchText)
      return []

def giphySearch(searchText,searchType):
    logger.info('giphy search started for type: '+searchType+" and text: "+searchText)
    giphySearchUrl = "https://api.giphy.com/v1/"+searchType+"/search?api_key="+config['GiphyAuth']+"&limit=1&q="
    giphyQuery = searchText
    giphySearchUrl = giphySearchUrl + giphyQuery
    logger.info(giphySearchUrl)
    try:        
        giphyResponse = requests.get(giphySearchUrl)        
        data = giphyResponse.json()["data"][0]
        meme = {"title":data["title"], "url": data["url"]}
        logger.info("New Reply: "+json.dumps(meme))
        return [meme]
    except:
        logger.info("not found on giphy for type: "+ searchType)
        return []

def AddReply(results, comment):    
    reply = "[{}]({})\n\n  ".format(results[0]["title"],results[0]["url"])    
    try:
        if comment is not None:
            comment.reply(reply) 
            fh = open("commented.txt","a")
            fh.write(comment.id)
            fh.write("\n")     
            fh.close()
    except:
        return []

def AddEmptyReply(searchText, comment):    
    reply = "Sorry! I could not find anything with these words ("+searchText+")\n Could you try re-phrasing?" 
    try:
        if comment is not None:
            comment.reply(reply) 
    except:
        return []

def georgeSubListener():
    logger.info('George is listening now!')
    sub = config['sub']
    subreddit = reddit.subreddit(sub)
    while True:        
        for submission in subreddit.stream.submissions():
            subToReplyIn = config['threadTitle']
            author = config['author']
            matchsub = re.search(subToReplyIn, submission.title)
            if matchsub and submission.author == author:                
                georgeThreadCommentsListener(submission.id)

def georgeThreadCommentsListener(submissionID):
    sub = config['sub']
    subreddit = reddit.subreddit(sub)
    pattern1 = r"\b(.|\n)*(g|G)eorge (a|A)dd (.)*\b" 
    
    for comment in subreddit.stream.comments():
        if(comment.submission.id != submissionID):
            continue
        replied_to = open("commented.txt").read().splitlines()

        if comment.id not in replied_to:
            match1 = re.search(pattern1, comment.body)
            commentRequest = comment.body.lower()
            commentTemp = commentRequest.replace("\n\n", " ")
            comment_token = commentTemp.split(" ")
            
            if(match1):
                memeArray = comment_token[comment_token.index("george") + 2:]
                memeName = " ".join(memeArray)
            
                try:
                    results = imageSearch(memeName)
                    if(len(results) != 0):
                        AddReply(results, comment)     
                    else
                        AddEmptyReply(memeName, comment)                                      
                    time.sleep(10)                    
                except:
                    return []       


def main():    
    thread = {"georgeSubListener": threading.Thread(target = georgeSubListener)}
    for thread in thread.values():
        thread.start()

if __name__ == "__main__":    
    main()  
