﻿import datetime, os, json, requests
from urllib import request
from bs4 import BeautifulSoup

#duplication of requests and urllib.request modules for testing purposes only

currentFileDir = os.getcwd()
CurrentDate = datetime.date.today()

def getSeriesMainPage(showID):
    """Get Series Main Page"""
    URLString = 'http://www.imdb.com/title/%s' % (showID)
    mainPage = request.urlopen(URLString)
    return BeautifulSoup(mainPage, 'html.parser')

def getSeriesSeasonPage(showID, season):
     """Get Page of selected season"""
     URLString = 'http://www.imdb.com/title/%s/episodes?season=%d' % (showID, season)
     seasonPage = request.urlopen(URLString)
     return BeautifulSoup(seasonPage, 'html.parser')

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

def writeToJSONFile(shows):
    """take show dictionary and export to JSON file"""
    #Add code to export show dictionary to JSON file

    return

def getShowTitle(showID):
    """Get show information from OMDB"""
    requestParams = {
        'i': showID,
        'plot': 'short',
        'r': 'json'
        }
    omdbResponse = requests.get('http://www.omdbapi.com/', params = requestParams)
    omdbText = omdbResponse.text
    omdbText = omdbText.replace('\u2013', '-')
    omdbJSON = json.loads(omdbText)
    return omdbJSON['Title']

def getSeasons(soupMainPage, showID):
    """get the number of seasons from the show's main page on IMDB"""
    SeasonList = []
    for link in soupMainPage.find_all('a'):
        linkString = link.get('href')
        if type(linkString) == str:
            if ('/title/%s/episodes?season=' % showID) in linkString:
                linkStringSplit = linkString.split('_')
                SeasonList.append(int(linkStringSplit[-1]))
    SeasonList.sort()
    return SeasonList

def getCurrentSeason(soup, showID):
    numberOfSeasons = getSeasons(soup, showID)
    #Add code to check if current season is last one listed on IMDB

    return numberOfSeasons[-1]

def getNextAirDate(soupSeasonPage):
    """Get the airdate for the next episode"""
    airdates = []
    bestDate = []

    for date in soupSeasonPage.find_all('div', class_ = 'airdate'):
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
    showDate = airdates[0]
    for date in airdates:
        delta = CurrentDate - date
        if (CurrentDate > date):
            continue
        elif (date - CurrentDate) < bestDateDelta:
            bestDateDelta = delta
            showDate = date
            continue
    return showDate

def parsePageForShowInfo(showID):
    """Parse show information from IMDB"""
    show = {}

    soupMainPage = getSeriesMainPage(showID)

    show['Name'] = getShowTitle(showID)

    show['Current Season'] = getCurrentSeason(soupMainPage, showID)

    soupSeasonPage = getSeriesSeasonPage(showID, show['Current Season'])

    show['Air Date'] = getNextAirDate(soupSeasonPage)

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
    'tt0944947',
    'tt4159076',
    'tt1486217',
    'tt3339966',
    'tt1520211',
    'tt2467372',
    ]

for series in seriesList:
    parsePageForShowInfo(series)

#deltaSort = []

#for show in ShowDates.keys():
#    delta = ShowDates[show] - CurrentDate
#    deltaSort.append((delta, show))

#sortedShows = sorted(deltaSort)

#for show in sortedShows:
#    print('\n', show[1], ': ', ShowDates[show[1]])
#    print('Starts in: ', show[0])