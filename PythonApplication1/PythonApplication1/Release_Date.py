import datetime, os, json, requests
from urllib import request
from bs4 import BeautifulSoup

#duplication of requests and urllib.request modules for testing purposes only

### Create Class ###

class MovieList():
    masterDict = {}
    currentFileDir = os.getcwd()
    CurrentDate = datetime.date.today()
    current_list_exists = False

    def __init__(self):
        """Initialize list, pull information from saved file if it exists"""
        if os.path.isfile('shows.txt'):
            current_list_exists = True
            with open('shows.txt') as savedFile:
                showsJSON = json.load(savedFile)
                print("List of shows to include in search:\n")
                showCount = 1
                for show in showsJSON.keys():
                    print("%d.  %s" % (showCount, showsJSON[show]['Name']))
                    self.masterDict[show] = {
                        'Name': showsJSON[show]['Name'],
                        'Is Movie': showsJSON[show]['Is Movie'],
                        'Show No.': showCount
                        }
                    showCount += 1
            self.askToRemoveShow()
        self.askForNewShow()
        return

    def monthTranslate(self, month):
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

    def getSeriesMainPage(self, showID):
        """Get Series Main Page"""
        URLString = 'http://www.imdb.com/title/%s' % (showID)
        mainPage = request.urlopen(URLString)
        return BeautifulSoup(mainPage, 'html.parser')
    
    def getSeriesSeasonPage(self, showID, season):
        """Get Page of selected season"""
        URLString = 'http://www.imdb.com/title/%s/episodes?season=%d' % (showID, season)
        seasonPage = request.urlopen(URLString)
        return BeautifulSoup(seasonPage, 'html.parser')
    
    def getShowTitle(self, showID):
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

    def getShowID(self, showTitle):
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

    def getMovieOrSeries(self, showID):
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

    def getMovieReleaseDate(self, soupMainPage, showID):
        """Parse IMDB page for release date. Currently looks for 'Release Date' under 'txt-block' div."""
        exactDate = False

        for div in soupMainPage.find_all('div', class_ = 'txt-block'):
            divText = str(div)
            if not "Release Date:" in divText:
                continue
            else:
                """Find the start and end of the date string (begins after the </h4> tag, ends before the next open tag)"""
                dateStart = divText.find('</h4>')
                dateString = divText[(dateStart + 6):]
                dateEnd = dateString.find('<')
                dateString = dateString[:dateEnd]

                """Split the date string by spaces, convert the string to a datetime object"""
                dateStringSplit = dateString.split(' ')
                day = int(dateStringSplit[0])
                month = int(self.monthTranslate(dateStringSplit[1]))
                year = int(dateStringSplit[2])

                exactDate = True

                return (datetime.date(year, month, day), exactDate)

        return (datetime.date(1, 1, 1), exactDate)

    def getSeasons(self, soupMainPage, showID):
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

    def getNextAirDate(self, soupSeasonPage):
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
                month = self.monthTranslate(splitDate[1])
                year = int(splitDate[2])
                formattedDate = datetime.date(year, month, day)

                if formattedDate < self.CurrentDate:
                    continue
                else:
                    exactDate = True
                    airdates.append(datetime.date(year, month, day))
                if bestDate[0] < 3:
                    bestDate[0] = 3
                    bestDate[1] = datetime.date(year, month, day)

            elif len(splitDate) == 2:
                month = self.monthTranslate(splitDate[0])
                year = int(splitDate[1])
                formattedDate = datetime.date(year, month, day)

                if formattedDate < self.CurrentDate:
                    continue
                else:
                    airdates.append(datetime.date(year, month, day))
                if bestDate[0] < 2:
                    bestDate[0] = 2
                    bestDate[1] = datetime.date(year, month, day)

            elif len(splitDate) == 1:
                year = int(splitDate[0])
                formattedDate = datetime.date(year, month, day)

                if formattedDate < self.CurrentDate:
                    continue
                else:
                    airdates.append(datetime.date(year, month, day))
                if bestDate[0] < 1:
                    bestDate[0] = 1
                    bestDate[1] = datetime.date(year, month, day)

        bestDateDelta = self.CurrentDate - bestDate[1]
        showDate = bestDate[1]
        for date in airdates:
            if (self.CurrentDate > date):
                continue
            elif (date - self.CurrentDate) < bestDateDelta:
                delta = date - self.CurrentDate
                bestDateDelta = delta
                showDate = date
                continue

        return (showDate, exactDate)

    def getCurrentSeasonAndNextAirDate(self, soupMainPage, showID):
        """Return tuple of (current season, (next air date, whether it is an exact date))"""
        seasonList = self.getSeasons(soupMainPage, showID)

        if len(seasonList) == 1:
            return (seasonList[0], getSeriesSeasonPage(showID, seasonList[0]))

        soupPriorSeason = self.getSeriesSeasonPage(showID, seasonList[-2])
        priorSeasonAirDate = self.getNextAirDate(soupPriorSeason)
        if priorSeasonAirDate[0] < self.CurrentDate:
            soupLatestSeason = self.getSeriesSeasonPage(showID, seasonList[-1])
            latestSeasonAirDate =  self.getNextAirDate(soupLatestSeason)
            return (seasonList[-1], latestSeasonAirDate)
        else:
            return (seasonList[-1], priorSeasonAirDate)

    def parseIMDBForShowInfo(self, showID, isMovie, name):
        """Parse show information from IMDB"""
        show = {}

        soupMainPage = self.getSeriesMainPage(showID)

        if name:
            show['Name'] = name
        else:
            show['Name'] = getShowTitle(showID)

        if isMovie:
            releaseInfo = self.getMovieReleaseDate(soupMainPage, showID)
            show['Air Date'] = releaseInfo[0]
            show['Exact Date'] = releaseInfo[1]
            show['Is Movie'] = True
        else:
            airDate = self.getCurrentSeasonAndNextAirDate(soupMainPage, showID)
            #Not sure if 'Current Season' is useful - saves current season in show dictionary
            show['Current Season'] = airDate[0]
            show['Air Date'] = airDate[1][0]
            show['Exact Date'] = airDate[1][1]
            show['Is Movie'] = False

        return show

    def loopThroughShows(self):
        """Loop through list of showIDs and pull info"""
        print('\nChecking for show information...')
        status = 0
        for showID in self.masterDict.keys():
            total = len(self.masterDict)
            showInfo = self.parseIMDBForShowInfo(showID, self.masterDict[showID]['Is Movie'], self.masterDict[showID]['Name'])
            self.masterDict[showID] = {
                'Air Date': showInfo['Air Date'],
                'Exact Date': showInfo['Exact Date'],
                'Name': showInfo['Name'],
                'Is Movie': showInfo['Is Movie']
                }
            status += 1
            print(str(int((float(status) / total) * 100)), '%')
        return

    def convertMasterToJSON(self):
        for showID in self.masterDict.keys():
            del self.masterDict[showID]['Air Date']
        return json.dumps(self.masterDict)

    def askForNewShow(self):
        while True:
            response = input("\nAdd a movie or tv show?  ").lower()
            if response.startswith('y') is True:
                newShow = input("What show?  ").lower()
                showID = self.getShowID(newShow)
                showTitle = self.getShowTitle(showID)
                secondResponse = input('Found "%s".  Is that correct?  ' % (showTitle)).lower()
                if secondResponse.startswith('n') is True:
                    continue
                elif secondResponse.startswith('y') is True:
                    isMovieBool = self.getMovieOrSeries(showID).lower()
                    if isMovieBool == 'movie':
                        isMovieBool = True
                    else:
                        isMovieBool = False
                    showInfo = self.parseIMDBForShowInfo(showID, isMovieBool, showTitle)
                    self.masterDict[showID] = {
                        'Air Date': showInfo['Air Date'],
                        'Exact Date': showInfo['Exact Date'],
                        'Name': showInfo['Name'],
                        'Is Movie': isMovieBool
                        }
                    continue
                else:
                    print('Please enter "yes" or "no".')
                    continue
            elif response.startswith('n') is True:
                return
            else:
                print('Please enter "yes" or "no".')

    def askToRemoveShow(self):
        while True:
            response = input("\nRemove a movie or tv show?  ").lower()
            if response.startswith('y') is True:
                while True:
                    show_to_remove = input("\nRemove which show number?  ")
                    try:
                        showNumber = int(show_to_remove)
                        showNumberID = False
                        for show, showInfo in self.masterDict.items():
                            """Find the show in the dictionary that corresponds to the number - May be better to implement show number within dictionary itself?"""
                            if showInfo['Show No.'] == showNumber:
                                showNumberID = show
                        if showNumberID is not False:
                            del self.masterDict[showNumberID]
                            print("Show number %d has been removed." % showNumber)
                        else:
                            print("Please enter a valid show number.\nThe number is located next to the show in the list at the top.")
                        break
                    except:
                        print("Please enter a valid show number.\nThe number is located next to the show in the list at the top.")
                else:
                    break
            else:
                return


### Run Program ###

movieList = MovieList()

movieList.loopThroughShows()

deltaSort = []

for showID, dict in movieList.masterDict.items():
    delta = dict['Air Date'] - movieList.CurrentDate
    deltaSort.append((delta, showID))

sortedShows = sorted(deltaSort)

print('\nAir Dates:\n')
for show in sortedShows:
    showDict = movieList.masterDict[show[1]]
    delta = showDict['Air Date'] - movieList.CurrentDate
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
    file.write(movieList.convertMasterToJSON())

input('Press any key to exit.')