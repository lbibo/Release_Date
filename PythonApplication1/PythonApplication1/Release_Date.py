import datetime, os

currentFileDir = os.getcwd()

movieList = []

if 'showlist.txt' in currentFileDir:
    with open('showlist.txt') as savedFile:
        for movie in savedFile:
            movieList.append(movie)

CurrentDate = datetime.date.today()
print(str(CurrentDate))

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