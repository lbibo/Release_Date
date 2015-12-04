import datetime, os, json, requests
from urllib import request
from bs4 import BeautifulSoup

#duplication of requests and urllib.request modules for testing purposes only

masterDict = {}
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
              'January': 1,
              'Feb.': 2,
              'February': 2,
              'Mar.': 3,
              'March': 3,
              'Apr.': 4,
              'April': 4,
              'May': 5,
              'Jun.': 6,
              'June': 6,
              'Jul.': 7,
              'July': 7,
              'Aug.': 8,
              'August': 8,
              'Sep.': 9,
              'September': 9,
              'Oct.': 10,
              'October': 10,
              'Nov.': 11,
              'November': 11,
              'Dec.': 12,
              'December': 12
              }
    return months[month]

def getShowTitle(showID):
    """Get show title from OMDB"""
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

def getShowID(showTitle):
    """Get show ID from OMDB"""
    requestParams = {
        't': showTitle,
        'plot': 'short',
        'r': 'json'
        }
    omdbResponse = requests.get('http://www.omdbapi.com/', params = requestParams)
    omdbText = omdbResponse.text
    omdbText = omdbText.replace('\u2013', '-')
    omdbJSON = json.loads(omdbText)
    return omdbJSON['imdbID']

def getMovieOrSeries(showID):
    """Get type from OMDB"""
    requestParams = {
        'i': showID,
        'plot': 'short',
        'r': 'json'
        }
    omdbResponse = requests.get('http://www.omdbapi.com/', params = requestParams)
    omdbText = omdbResponse.text
    omdbText = omdbText.replace('\u2013', '-')
    omdbJSON = json.loads(omdbText)
    return omdbJSON['Type'].lower()


def getMovieReleaseDate(soupMainPage, showID):
    for title in soupMainPage.find_all('a', title = 'See all release dates'):
        rawDate = title.get_text()
        rawDateSplit = rawDate.split(' ')
        day = int(rawDateSplit[1])
        month = int(monthTranslate(rawDateSplit[2]))
        yearSplit = rawDateSplit[3].split('\n')
        year = int(yearSplit[0])
        return datetime.date(year, month, day)
        
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

def getNextAirDate(soupSeasonPage):
    """Get the air date for the next episode of the given season page"""
    airdates = []
    bestDate = [0, datetime.date(1,1,1)]
    exactDate = False

    rawAirDateList = soupSeasonPage.find_all('div', class_ = 'airdate')

    for date in rawAirDateList:
        year = 1
        month = 1
        day = 1
        dateString = date.string.strip()
        splitDate = dateString.split(' ')

        if len(splitDate) == 3:
            day = int(splitDate[0])
            month = monthTranslate(splitDate[1])
            year = int(splitDate[2])
            formattedDate = datetime.date(year, month, day)

            if formattedDate < CurrentDate:
                continue
            else:
                exactDate = True
                airdates.append(datetime.date(year, month, day))
            if bestDate[0] < 3:
                bestDate[0] = 3
                bestDate[1] = datetime.date(year, month, day)

        elif len(splitDate) == 2:
            month = monthTranslate(splitDate[0])
            year = int(splitDate[1])
            formattedDate = datetime.date(year, month, day)

            if formattedDate < CurrentDate:
                continue
            else:
                airdates.append(datetime.date(year, month, day))
            if bestDate[0] < 2:
                bestDate[0] = 2
                bestDate[1] = datetime.date(year, month, day)

        elif len(splitDate) == 1:
            year = int(splitDate[0])
            formattedDate = datetime.date(year, month, day)

            if formattedDate < CurrentDate:
                continue
            else:
                airdates.append(datetime.date(year, month, day))
            if bestDate[0] < 1:
                bestDate[0] = 1
                bestDate[1] = datetime.date(year, month, day)

    bestDateDelta = CurrentDate - bestDate[1]
    showDate = bestDate[1]
    for date in airdates:
        if (CurrentDate > date):
            continue
        elif (date - CurrentDate) < bestDateDelta:
            delta = date - CurrentDate
            bestDateDelta = delta
            showDate = date
            continue

    return (showDate, exactDate)

def getCurrentSeasonAndNextAirDate(soupMainPage, showID):
    """Return tuple of (current season, (next air date, whether it is an exact date))"""
    seasonList = getSeasons(soupMainPage, showID)

    if len(seasonList) == 1:
        return (seasonList[0], getSeriesSeasonPage(showID, seasonList[0]))

    soupPriorSeason = getSeriesSeasonPage(showID, seasonList[-2])
    priorSeasonAirDate = getNextAirDate(soupPriorSeason)
    if priorSeasonAirDate[0] < CurrentDate:
        soupLatestSeason = getSeriesSeasonPage(showID, seasonList[-1])
        latestSeasonAirDate = getNextAirDate(soupLatestSeason)
        return (seasonList[-1], latestSeasonAirDate)
    else:
        return (seasonList[-1], priorSeasonAirDate)

def parseIMDBForShowInfo(showID, isMovie, name):
    """Parse show information from IMDB"""
    show = {}

    soupMainPage = getSeriesMainPage(showID)

    if name:
        show['Name'] = name
    else:
        show['Name'] = getShowTitle(showID)

    if isMovie:
        show['Air Date'] = getMovieReleaseDate(soupMainPage, showID)
        show['Exact Date'] = True
        show['Is Movie'] = True
    else:
        airDate = getCurrentSeasonAndNextAirDate(soupMainPage, showID)
        #Not sure if 'Current Season' is useful - saves current season in show dictionary
        show['Current Season'] = airDate[0]
        show['Air Date'] = airDate[1][0]
        show['Exact Date'] = airDate[1][1]
        show['Is Movie'] = False

    return show

def loopThroughShows(masterDict):
    """Loop through list of showIDs and pull info"""
    print('\nChecking for show information...')
    status = 0
    for showID in masterDict.keys():
        total = len(masterDict)
        showInfo = parseIMDBForShowInfo(showID, masterDict[showID]['Is Movie'], masterDict[showID]['Name'])
        masterDict[showID] = {
            'Air Date': showInfo['Air Date'],
            'Exact Date': showInfo['Exact Date'],
            'Name': showInfo['Name'],
            'Is Movie': showInfo['Is Movie']
            }
        status += 1
        print(str(int((float(status) / total) * 100)), '%')
    return

def convertMasterToJSON(masterDict):
    for showID in masterDict.keys():
        del masterDict[showID]['Air Date']
    return json.dumps(masterDict)

if os.path.isfile('shows.txt'):
    with open('shows.txt') as savedFile:
        showsJSON = json.load(savedFile)
        print("List of shows to include in search:\n")
        for show in showsJSON.keys():
            print(showsJSON[show]['Name'])
            masterDict[show] = {
                'Name': showsJSON[show]['Name'],
                'Is Movie': showsJSON[show]['Is Movie']
                }

while True:
    response = input("\nAdd a movie or tv show?  ").lower()
    if response == 'y' or response == 'yes':
        newShow = input("What show?  ").lower()
        showID = getShowID(newShow)
        showTitle = getShowTitle(showID)
        secondResponse = input('Found "%s".  Is that correct?  ' % (showTitle)).lower()
        if secondResponse == 'n' or secondResponse == 'no':
            continue
        elif secondResponse == 'y' or secondResponse == 'yes':
            isMovieBool = getMovieOrSeries(showID).lower()
            if isMovieBool == 'movie':
                isMovieBool = True
            else:
                isMovieBool = False
            showInfo = parseIMDBForShowInfo(showID, isMovieBool, showTitle)
            masterDict[showID] = {
                'Air Date': showInfo['Air Date'],
                'Exact Date': showInfo['Exact Date'],
                'Name': showInfo['Name'],
                'Is Movie': isMovieBool
                }
            continue
        else:
            print('Please enter "yes" or "no".')
            continue
    elif response == 'n' or response == 'no':
        break
    else:
        print('Please enter "yes" or "no".')

loopThroughShows(masterDict)

deltaSort = []

for showID, dict in masterDict.items():
    delta = dict['Air Date'] - CurrentDate
    deltaSort.append((delta, showID))

sortedShows = sorted(deltaSort)

print('\nAir Dates:\n')
for show in sortedShows:
    showDict = masterDict[show[1]]
    delta = showDict['Air Date'] - CurrentDate
    if delta.days < 0:
        print('%s:  There are no new episodes set for release.\n' % showDict['Name'])
    elif delta.days == 0:
        print('%s:  The newest episode airs today!\n' % showDict['Name'])
    else:
        if showDict['Exact Date']:
            print('%s:  %s/%s/%s.  That is in %d days.\n' % (showDict['Name'],
                                                             str(showDict['Air Date'].month),
                                                             str(showDict['Air Date'].day),
                                                             str(showDict['Air Date'].year),
                                                             delta.days))
        else:
            print('%s:  No earlier than %s/%s/%s.  There is no exact date set.\n' % (showDict['Name'],
                                                                                     str(showDict['Air Date'].month),
                                                                                     str(showDict['Air Date'].day),
                                                                                     str(showDict['Air Date'].year)
                                                                                     )
                  )

with open('shows.txt', 'w') as file:
    file.write(convertMasterToJSON(masterDict))

print('Press any key to exit.')