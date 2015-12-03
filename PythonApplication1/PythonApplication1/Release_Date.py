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
    exactDate = False

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
                exactDate = True
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
    return (showDate, exactDate)

def parsePageForShowInfo(showID, name = 0):
    """Parse show information from IMDB"""
    show = {}

    soupMainPage = getSeriesMainPage(showID)

    if name == 0:
        show['Name'] = getShowTitle(showID)
    else:
        show['Name'] = name

    show['Current Season'] = getCurrentSeason(soupMainPage, showID)

    soupSeasonPage = getSeriesSeasonPage(showID, show['Current Season'])

    airDate = getNextAirDate(soupSeasonPage)
    show['Air Date'] = airDate[0]
    show['Exact Date'] = airDate[1]

    return show

def loopThroughShows(seriesList):
    global masterDict
    """Loop through list of showIDs and pull info"""
    print('\nChecking for show information...')
    status = 0
    for showID in seriesList:
        total = len(seriesList)
        showInfo = parsePageForShowInfo(showID)
        masterDict[showID] = {
            'Air Date': showInfo['Air Date'],
            'Exact Date': showInfo['Exact Date'],
            'Name': showInfo['Name']
            }
        status += 1
        print(str(int((float(status) / total) * 100)), '%')
    return

def convertMasterToJSON(masterDict):
    for showID in masterDict.keys():
        del masterDict[showID]['Air Date']
    return json.dumps(masterDict)

seriesList = []
if os.path.isfile('shows.txt'):
    with open('shows.txt') as savedFile:
        showsJSON = json.load(savedFile)
        print("List of shows to include in search:\n")
        for show in showsJSON.keys():
            print(showsJSON[show]['Name'])
            seriesList.append(show)

while True:
    response = input("\nAdd a new movie or tv show?  ").lower()
    if response == 'y' or response == 'yes':
        newShow = input("What show?  ").lower()
        showID = getShowID(newShow)
        showTitle = getShowTitle(showID)
        secondResponse = input('Found "%s".  Is that correct?  ' % (showTitle)).lower()
        if secondResponse == 'n' or secondResponse == 'no':
            continue
        elif secondResponse == 'y' or secondResponse == 'yes':
            seriesList.append(showID)
            showInfo = parsePageForShowInfo(showID, name = showTitle)
            masterDict[showID] = {
                'Air Date': showInfo['Air Date'],
                'Exact Date': showInfo['Exact Date'],
                'Name': showInfo['Name']
                }
            break
        else:
            print('Please enter "yes" or "no".')
            continue
    elif response == 'n' or response == 'no':
        break
    else:
        print('Please enter "yes" or "no".')

loopThroughShows(seriesList)

deltaSort = []

for showID in seriesList:
    showDict = masterDict[showID]
    delta = showDict['Air Date'] - CurrentDate
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