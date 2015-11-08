import datetime

CurrentDate = datetime.date.today()
print(str(CurrentDate))

ShowDates = []

GameOfThrones = datetime.date(2016, 5, 1)
ShowDates.append(['Game of Thrones', GameOfThrones])

Archer = datetime.date(2016, 1, 1)
ShowDates.append(['Archer', Archer])



for show in ShowDates:
    delta = show[1] - CurrentDate
    print(show[0], ': ', show[1])
    print('Starts in: ', delta)