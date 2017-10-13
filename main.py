import csv
import re
import sys
import texttable as tt
from texttable import Texttable
from operator import attrgetter
from pprint import pprint

class Person:
    def __init__(self, id, name, freetimes):
        self.id = id
        self.name = name
        self.freetimes = freetimes
    @property
    def lenOfFreetimes(self):
        return len(self.freetimes)
        
class Time:
    def __init__(self, day, sessionStr):
        p = re.compile('([C-L])([上下])')
        m = p.findall(sessionStr)
        if not m:
            raise Exception('spam', 'eggs')
        self.day = day
        self.sessionStr = sessionStr
        self.session = m[0][0]
        self.isFirst = bool(m[0][1] == '上')
        
class Hole:
    def __init__(self, time):
        self.time = time
        self.landlords = []
        self.depth = 1
        self.cavemen = []
        self.students = []
    @property
    def isFull(self):
        if len(self.cavemen) > self.depth:
            raise Exception('Hole ' + self.time.sessionStr +' too many cavemen.')
        return len(self.cavemen) == self.depth
    @property
    def isEmpty(self):
        return len(self.students) == 0
    @property
    def pressure(self):
        if not self.isFull:
            return len(self.students) / (self.depth - len(self.cavemen))
        else:
            return 0

def parseCsv(filepath):
    group = []
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            freetimes = []
            for day in range(1, 5):
                for sessionStr in row[3 + day].split(';'):
                    try:
                        time = Time(day, sessionStr)
                        freetimes.append(time)
                    except:
                        pass
            person = Person(row[3], row[2], freetimes)
            group.append(person)
    return group

def digHoles(group):
    holes = []
    for ta in group:
        for time in ta.freetimes:
            hole = next((e for e in holes if time.day == e.time.day and time.sessionStr == e.time.sessionStr), None)
            if hole == None:
                hole = Hole(time)
                holes.append(hole)
            else:
                hole.depth += 1
            hole.landlords.append(ta.name)
    return holes

def letStudentsQueuing(notBeAssignStudents, holes):
    for student in notBeAssignStudents:
        for time in student.freetimes:
            hole = next((e for e in holes if time.day == e.time.day and time.sessionStr == e.time.sessionStr), None)
            if not (hole == None):
                hole.students.append(student)

def findLeastPressureHole(holes):
    def isFull(hole):
        return not hole.isFull and not hole.isEmpty
    notFullHoles = list(filter(isFull, holes))
    if len(notFullHoles) == 0:
        return False
    return min(notFullHoles, key=attrgetter('pressure'))

def findLeastFreetimeStudent(hole):
    return min(hole.students, key=attrgetter('lenOfFreetimes'))

def checkin(holes):
    leastPressureHole = findLeastPressureHole(holes)
    if leastPressureHole == False:
        return False
    student = findLeastFreetimeStudent(leastPressureHole)
    for hole in holes:
        if student in hole.students:
            hole.students.remove(student)
    leastPressureHole.cavemen.append(student)
    if leastPressureHole.isFull:
        leastPressureHole.students = []
    return True

def __main__():
    notBeAssignStudents = parseCsv('students.csv')
    holes = digHoles(parseCsv('tas.csv'))
    numOfNotBeAssignStudents = len(notBeAssignStudents)

    letStudentsQueuing(notBeAssignStudents, holes)

    while checkin(holes):
        pass

    assignedStudents = []
    tab = tt.Texttable()
    headings = ['時間','助教','學生學號','學生名字']
    tab.set_deco(Texttable.VLINES)
    tab.header(headings)
    for hole in holes:
        for caveman in hole.cavemen:
            assignedStudents.append(caveman)
            tab.add_row([hole.time.sessionStr, ','.join(hole.landlords), caveman.id, caveman.name])
            
    tableOfNotBeAssignStudents = tt.Texttable()
    for student in assignedStudents:
        notBeAssignStudents.remove(student)
    for student in notBeAssignStudents:
        tableOfNotBeAssignStudents.add_row([student.id, student.name])

    s = tab.draw()
    s2 = tableOfNotBeAssignStudents.draw()
    print(s)
    print(str(len(assignedStudents)) + '/' + str(numOfNotBeAssignStudents))
    print(s2)

__main__()