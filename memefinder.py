import requests
from time import time
from bs4 import BeautifulSoup

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}  # defining headers for browser


class KymResult:
    def __init__(self):
        self.about = None
        self.imageurl = None
        self.siteurl = None
        self.soup = None

    def parse(self, content):
        self.soup = BeautifulSoup(content, 'html.parser')  # parsing it
        self.about = self.soup.find('meta', attrs={"property": "og:title"})['content']  # finding description
        self.imageurl = self.soup.find('meta', attrs={"property": "og:image"})['content']  # finding image url
        self.siteurl = self.soup.find('meta', attrs={"property": "og:url"})['content']  # finding site url

    def __repr__(self):
        return self.about['content']  # This is used for you to be able to print object and get definition print(nameofobject)


class KymSearch(KymResult):
    def __init__(self, term: str):  # term is word to be searched
        print("zhere")
        super().__init__()
        self.t1 = time()  # set time on start
        self.term = term
        for i in term:  # change every space to +
            if i == " ":
                i = "+"
        self.url = "http://knowyourmeme.com/search?q=" + self.term  # making a url to be used
        self.page = requests.get(self.url, headers=_HEADERS)  # requesting code
        self.soup = BeautifulSoup(self.page.content, 'html.parser')  # parsing code with Beautiful Soup
        self.list1 = self.soup.findAll("a", href=True)  # Finding all links of search
        self.url2 = "http://knowyourmeme.com" + self.list1[129]['href']  # Picking first result and using its href
        self.page2 = requests.get(self.url2, headers=_HEADERS)  # requesting page again

        self.parse(self.page2.content)

        self.t2 = time()  # getting time on finish
        self.time = self.t2 - self.t1  # time it took to do all this


class KymRandomImage(KymResult):
    def __init__(self):
        super().__init__()
        self.url = "http://knowyourmeme.com/photos/random"
        self.page = requests.get(self.url, headers=_HEADERS)  # requesting code
        self.parse(self.page.content)


if __name__ == '__main__':
    # random_meme = KymRandomImage()
    # print(f"{random_meme.about} ({random_meme.imageurl} at {random_meme.siteurl})")

    searched_meme = KymSearch("pewdiepie")
    print(f"{searched_meme.about} ({searched_meme.imageurl} at {searched_meme.siteurl})")