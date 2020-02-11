import praw, re, time, pytz, yaml, threading, random, requests, base64

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

def imageSearch(memeName):
    result = giphySearch(memeName,"stickers")
    if(len(result) == 0):
        result = giphySearch(memeName,"gifs")
        if(len(result) == 0):
            result = imgurSearch(memeName)
    return result
       

def imgurSearch(searchText):
    print('imgur search started')
    imgurSearchUrl = "https://api.imgur.com/3/gallery/search/top/all/1?q=" 
    imgurAccessHeader = {"Accept": "application/json", "Content-Type": "application/json","Authorization": config['ImgurAuth']}
    imgurQuery = searchText
    imgurSearchUrl = imgurSearchUrl + imgurQuery
    try:
      imgurResponse = requests.get(imgurSearchUrl,headers=imgurAccessHeader)
      data = imgurResponse.json()["data"][0]
      meme = {"title":data["title"], "url": data["link"]}
      print(meme)
      return [meme]
    except:
      print("not found on imgur")
      return []

def giphySearch(searchText,searchType):
    print('giphy search started')
    giphySearchUrl = "https://api.giphy.com/v1/"+searchType+"/search?api_key="+config['GiphyAuth']+"&limit=1&q="
    giphyQuery = searchText
    giphySearchUrl = giphySearchUrl + giphyQuery
    print(giphySearchUrl)
    try:
        giphyResponse = requests.get(giphySearchUrl)
        data = giphyResponse.json()["data"][0]
        meme = {"title":data["title"], "url": data["url"]}
        print(meme)
        return [meme]
    except:
        print("not found on giphy for type: "+ searchType)
        return []

def AddReply(results, comment):    
    reply = "[{}]({})\n\n  ".format(results[0]["title"],results[0]["url"])    
    try:
        if comment is not None:
            comment.reply(reply)      
    except:
        return []

def georgeSubListener():
    print('George is listening now!')
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
    subreddit = reddit.subreddit(sub)
    pattern1 = r"\b(.|\n)*(g|G)eorge (a|A)dd (.)*\b" 
    
    for comment in subreddit.stream.comments():
        if(comment.submission.id != submissionID):
            continue
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
                time.sleep(10)                    
            except:
                return []       


def main():    
    thread = {"georgeSubListener": threading.Thread(target = georgeSubListener)}
    for thread in thread.values():
        thread.start()

if __name__ == "__main__":    
    main()  
