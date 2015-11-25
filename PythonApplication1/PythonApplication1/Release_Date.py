import datetime, os
from urllib.request import urlopen
from bs4 import BeautifulSoup

currentFileDir = os.getcwd()
CurrentDate = datetime.date.today()

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

def parsePageForShowInfo(showID, showName):
    """Pull show information from IMDB"""
    show = {}

    """get show name (doesn't work)"""
    show['Name'] = showName
    mainPageURLString = 'http://www.imdb.com/title/%s' % (showID)
    IMDBShowMainPage = urlopen(mainPageURLString)
    soup = BeautifulSoup(IMDBShowMainPage, 'html.parser')
    #for title in soup.find_all('title'):
    #    titleString = title
    #    titleString = str(titleString[:38])
    #    print(titleString)

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
            day = int(splitDate[0])
            month = monthTranslate(splitDate[1])
            year = int(splitDate[2])
            if len(bestDate) <= 3:
                bestDate = [year, month, day]
                airdates.append(datetime.date(year, month, day))
        elif len(splitDate) == 2:
            month = monthTranslate(splitDate[0])
            year = int(splitDate[1])
            if len(bestDate) <= 2:
                bestDate = [year, month]
                airdates.append(datetime.date(year, month, day))
        elif len(splitDate) == 1:
            year = int(splitDate[0])
            if len(bestDate) <= 1:
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
    print("That is in %s days.\n" % str((show['Air Date'] - CurrentDate).days))
    return show

#def addShowToList(show):
#    return

if 'showlist.txt' in currentFileDir:
    with open('showlist.txt') as savedFile:
        for movie in savedFile:
            movieList.append(movie)

#while True:
#    response = input("Add a new movie or tv show?\n(Doesn't work at the moment)").lower()
#    if response == 'y' or response == 'yes':
#        newMovie = input("What show?  ").lower()
#        break
#    else:
#        break

seriesList = [
    ('tt0944947', 'Game of Thrones'),
    ('tt4159076', 'Dark Matter'),
    ('tt1486217', 'Archer'),
    ('tt3339966', 'Unbreakable Kimmy Schmidt'),
    ('tt1520211', 'The Walking Dead'),
    ('tt2467372', 'Brooklyn Nine-Nine')
    ]

for series in seriesList:
    parsePageForShowInfo(series[0], series[1])

#deltaSort = []

#for show in ShowDates.keys():
#    delta = ShowDates[show] - CurrentDate
#    deltaSort.append((delta, show))

#sortedShows = sorted(deltaSort)

#for show in sortedShows:
#    print('\n', show[1], ': ', ShowDates[show[1]])
#    print('Starts in: ', show[0])