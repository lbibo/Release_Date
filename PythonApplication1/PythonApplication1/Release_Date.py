import datetime, os
from urllib.request import urlopen
from bs4 import BeautifulSoup

currentFileDir = os.getcwd()
CurrentDate = datetime.date.today()

movieList = []

def monthTranslate(month):
    months = {'Jan.': 1,
              'Feb.': 2,
              'Mar.': 3,
              'Apr.': 4,
              'May': 5,
              'June': 6,
              'July': 7,
              'Aug.': 8,
              'Sep.': 9,
              'Oct.': 10,
              'Nov.': 11,
              'Dec.': 12}
    return months[month]

def parsePageForShowInfo(showID):
    """Pull show information from IMDB"""
    show = {}

    """get show name"""
    show['Name'] = "ShowName"
    mainPageURLString = 'http://www.imdb.com/title/%s' % (showID)
    IMDBShowMainPage = urlopen(mainPageURLString)
    soup = BeautifulSoup(IMDBShowMainPage, 'html.parser')
    #titleString = soup.title.string
    #print(titleString)

    """get the number of seasons/newest season"""
    SeasonList = []
    for link in soup.find_all('a'):
        linkString = link.get('href')
        if type(linkString) == str:
            if ('/title/%s/episodes?season=' % showID) in linkString:
                linkStringSplit = linkString.split('_')
                SeasonList.append(int(linkStringSplit[-1]))
    SeasonList.sort()
    show['Most Recent Season'] = SeasonList[-1]

    """Get the airdate for the next episode"""
    airdates = []
    bestDate = []
    showSeasonURLString = 'http://www.imdb.com/title/%s/episodes?season=%d' % (showID, show['Most Recent Season'])
    IMDBShowSeasonPage = urlopen(showSeasonURLString)
    soup = BeautifulSoup(IMDBShowSeasonPage, 'html.parser')
    for date in soup.find_all('div', class_ = 'airdate'):
        year = 1
        month = 1
        day = 1
        dateString = date.string.strip()
        splitDate = dateString.split(' ')
        if len(splitDate) == 3:
            month = monthTranslate(splitDate[0])
            day = int(splitDate[1])
            year = int(splitDate[2])
            if len(bestDate) < 3:
                bestDate = [year, month, day]
                airdates.append(datetime.date(year, month, day))
        elif len(splitDate) == 2:
            month = monthTranslate(splitDate[0])
            year = int(splitDate[1])
            if len(bestDate) < 2:
                bestDate = [year, month]
                airdates.append(datetime.date(year, month, day))
        elif len(splitDate) == 1:
            year = int(splitDate[0])
            if len(bestDate) < 1:
                bestDate = [year]
                airdates.append(datetime.date(year, month, day))

    bestDateDelta = CurrentDate - airdates[0]
    show['Air Date'] = airdates[0]
    for date in airdates:
        delta = CurrentDate - date
        if (CurrentDate > date):
            continue
        elif (date - CurrentDate) < bestDateDelta:
            bestDateDelta = delta
            show['Air Date'] = date
            continue

    print("The next episode of %s airs on %s." % (show['Name'], str(show['Air Date'])))
    return show

def addShowToList(show):
    return

parsePageForShowInfo('tt0944947')

if 'showlist.txt' in currentFileDir:
    with open('showlist.txt') as savedFile:
        for movie in savedFile:
            movieList.append(movie)


ShowDates = {}

while True:
    response = input("Add a new movie or tv show?\n(Doesn't work at the moment)").lower()
    if response == 'y' or response == 'yes':
        newMovie = input("What show?  ").lower()
        break
    else:
        break


GameOfThrones = datetime.date(2016, 5, 1)
ShowDates['Game of Thrones'] = GameOfThrones

Archer = datetime.date(2016, 1, 1)
ShowDates['Archer'] = Archer

SiliconValley = datetime.date(2016, 4, 1)
ShowDates['Silicon Valley'] = SiliconValley

Unbreakable = datetime.date(2016, 3, 1)
ShowDates['Unbreakable Kimmy Schmidt'] = Unbreakable

DarkMatter = datetime.date(2016, 1, 1)
ShowDates['Dark Matter'] = DarkMatter

StarWars = datetime.date(2015, 12, 14)
ShowDates['Star Wars Ep. VII'] = StarWars

deltaSort = []

for show in ShowDates.keys():
    delta = ShowDates[show] - CurrentDate
    deltaSort.append((delta, show))

sortedShows = sorted(deltaSort)

for show in sortedShows:
    print('\n', show[1], ': ', ShowDates[show[1]])
    print('Starts in: ', show[0])