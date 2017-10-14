import csv
import re
import sys
import texttable as tt
from texttable import Texttable
from operator import attrgetter

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
    def numOfFreeLandlords(self):
        return len(self.landlords) - len(self.cavemen)
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
            hole.landlords.append(ta)
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

# 安排 DEMO 助教，會從時數最多的多餘助教開始拔除。
def arrangeTAs(holes, TAs):
    dutyTable = []
    for TA in TAs:
        num = 0
        for hole in holes:
            def isTA(landlord):
                return landlord == TA
            match = list(filter(isTA, hole.landlords))
            if match:
                num += 1
        dutyTable.append({'TA': TA, 'num': num})
    sortedHoles = list(sorted(holes, key=attrgetter('numOfFreeLandlords')))
    for hole in sortedHoles:
        numOfLandlords = len(hole.landlords)
        numOfCavemen = len(hole.cavemen)
        diff = numOfLandlords - numOfCavemen
        if diff > 0:
            for t in range(diff):
                matchDuty = list(filter(lambda row: row['TA'] in hole.landlords, dutyTable))
                index = max(range(len(matchDuty)), key=lambda index: matchDuty[index]['num'])
                unnecessaryLandlord = matchDuty[index]['TA']
                hole.landlords.remove(unnecessaryLandlord)
                matchDuty[index]['num'] -= 1
    for row in dutyTable:
        print(row['TA'].name, row['num'], '次DEMO')

def printResultTable(holes, notBeAssignStudents, numOfNotBeAssignStudents):
    assignedStudents = []
    tab = tt.Texttable()
    headings = ['時間', '助教', '學生學號', '學生名字']
    tab.set_deco(Texttable.VLINES)
    tab.header(headings)
    for hole in holes:
        for caveman in hole.cavemen:
            assignedStudents.append(caveman)
            landlordNames = []
            for landlord in hole.landlords:
                landlordNames.append(landlord.name)
            tab.add_row([hole.time.sessionStr, ','.join(landlordNames),
                                                 caveman.id, caveman.name])
            
    tableOfNotBeAssignStudents = tt.Texttable()
    headings = ['學生學號', '學生名字']
    tableOfNotBeAssignStudents.set_deco(Texttable.VLINES)
    tableOfNotBeAssignStudents.header(headings)
    for student in assignedStudents:
        notBeAssignStudents.remove(student)
    for student in notBeAssignStudents:
        tableOfNotBeAssignStudents.add_row([student.id, student.name])

    s = tab.draw()
    s2 = tableOfNotBeAssignStudents.draw()
    print(s)
    print('已被分配學生數 / 總學生數 : ', len(assignedStudents), '/', numOfNotBeAssignStudents)
    print()
    print('未被分配學生清單')
    print(s2)

def drawSchedule(filepath, holes, type):
    timeRanges = list(['1010~1035', '1035~1100', '1110~1135', '1135~1200', '1320~1345', '1345~1410', 
    '1420~1445', '1445~1510', '1530~1555', '1555~1620', '1630~1655', '1655~1720', '1830~1855',
    '1855~1920', '1930~1955', '1955~2020', '2030~2055', '2055~2120', '2130~2155', '2155~2220'])
    timeRanges.reverse()
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as csvfile:
        fieldnames = ['節次', '時段', '10/16(一)', '10/17(二)', '10/18(三)', '10/19(四)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        def char_range(c1, c2):
            for c in xrange(ord(c1), ord(c2)+1):
                yield chr(c)
        for session in map(chr, range(*map(ord,['C', 'M']))) :
            for isFirst in [True, False]:
                upOrDown = ('下', '上')[isFirst]
                result = {'節次': session + upOrDown, '時段': timeRanges.pop()}
                for day in range(4):
                    sessionStr = '10/{}({})'.format(16 + day, ('一', '二', '三', '四')[day])
                    hole = next((e for e in holes if e.time.day == day + 1 
                        and e.time.session == session and e.time.isFirst == isFirst), None)
                    body = ''
                    if hole:
                        for person in getattr(hole, type):
                            body += person.id + person.name + '\n'
                    result[sessionStr] = body
                writer.writerow(result)

def __main__():
    # 載入學生資訊為未分配清單。
    notBeAssignStudents = parseCsv('students.csv')
    # 匯入 TA 們有空的時段，並視為「洞」(hole)。
    TAs = parseCsv('tas.csv')
    holes = digHoles(TAs)
    # 計算總學生人數。
    numOfNotBeAssignStudents = len(notBeAssignStudents)
    # 將所有學生放置到他們有空的時段的洞排隊。
    letStudentsQueuing(notBeAssignStudents, holes)
    # 開始安排學生進入洞中。
    while checkin(holes):
        pass
    # 安排 DEMO 助教。
    arrangeTAs(holes, TAs)

    printResultTable(holes, notBeAssignStudents, numOfNotBeAssignStudents)

    drawSchedule('schedule.csv', holes, 'cavemen')
    drawSchedule('duty.csv', holes, 'landlords')

__main__()