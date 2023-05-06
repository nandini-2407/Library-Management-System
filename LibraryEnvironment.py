# Importing the necessary modules
import simpy
import os
import yaml
import random
from itertools import cycle
from Student import Student
from Book import Book
from Time import Time
from datetime import datetime, timedelta
from colorama import Fore, Back, Style

# `pip install pyyaml`
# Above command to install the PyYAML module

# Get the data of Settings from Settings.yml
configYamlPath = os.path.join(os.path.dirname(__file__), "Settings.yml")
with open(configYamlPath, "r") as configYaml:
    settingsConfig = yaml.load(configYaml, Loader=yaml.FullLoader)

libraryInfo = settingsConfig["library"]
bookInfo = libraryInfo["book"]
studentInfo = settingsConfig["student"]

# List of student's name, roll number & the books to keep the data
studentList = []
bookList = []


def setupStudents(env):
    # Setup the students
    names = studentInfo["studentName"]
    surnames = studentInfo["studentSurname"]

    # Pairing name and roll number lists
    # Then randomizing each pair
    randomNames = list(zip(names, cycle(surnames))) if len(
        names) > len(surnames) else list(zip(cycle(names), surnames))
    random.shuffle(randomNames)

    # Adding students to student list with their membership
    for randomName in randomNames:
        student = Student(env, " ".join(randomName),
                          libraryInfo["membershipOptions"][random.randint(0, 1)])
        studentList.append(student)

# Clear the console screen

def setupLibrary(env):
    # Setting up JUIT LRC
    print(Fore.YELLOW + '\n╔════════════════════════════ ' + Style.BRIGHT + 'WELCOME TO %s' %
          libraryInfo["name"] + Fore.YELLOW + ' ════════════════════════════╗' + Style.RESET_ALL)

    # Displaying the library hours
    close_time = datetime.strptime(libraryInfo["closeHour"], "%H:%M").time()
    now = datetime.now()
    time_left = datetime.combine(now.date(), close_time) - now
    print('\n' + Fore.YELLOW + '║ Library is open until %s ║' %
          libraryInfo["closeHour"] + Fore.GREEN + ' (time left: %s)' % str(time_left).split('.')[0] + Style.RESET_ALL)

    # Displaying the current time
    current_time = datetime.now().strftime("%H:%M:%S")
    print('\n' + Fore.YELLOW + '║ Current time is %s ║\n' %
          current_time + Style.RESET_ALL)

    # Append the books to library's booklist
    for title in bookInfo["titles"]:
        book = Book(env, title, random.randint(1, 3))
        bookList.append(book)

    # Display information about the books
    print(Fore.YELLOW + '\nLibrary Books:' + Style.RESET_ALL)
    print('\n' + Fore.CYAN +
          '{:<35} {:<10}'.format('Title', 'Amount') + Style.RESET_ALL)
    print(Fore.MAGENTA + '-'*125 + Style.RESET_ALL)
    for book in bookList:
        print('{:<90} {:<30}'.format(book.getTitle(), book.getAmount()))

    print(Fore.YELLOW + '\n' + '-'*125 + '\n' + Style.RESET_ALL)


def main():
    # One second in real world is equal to one `env` time
    env = simpy.rt.RealtimeEnvironment(factor=0.5)
    setupLibrary(env)
    setupStudents(env)

    # One `env` time = 1 day in simulation
    t = Time(datetime.now())

    # Students arrive and request books in random order
    studentComeTime = 0
    for student in studentList:
        env.process(student.requestBook(
            env, random.choice(bookList), studentComeTime, t))
        studentComeTime += random.randint(1, 3)

    env.run()


    closing_message = "Farewell and best of luck in all your academic endeavors!"
    closing_message_centered = closing_message.center(
        len(libraryInfo["name"]) + 70)

    print(Fore.YELLOW + '\n\n════════════════════════════ ' +
          Style.BRIGHT + libraryInfo["name"] + ' IS CLOSED!' + ' ════════════════════════════\n')
    print(closing_message_centered)
    print('\n\n╚═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝')


if __name__ == "__main__":
    main()