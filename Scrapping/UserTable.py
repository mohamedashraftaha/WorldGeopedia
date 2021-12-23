from faker import Faker
import pandas as pd
from datetime import date
import os
from pathlib import Path
faker = Faker()



class User:
    def __init__(self):
        self.username = ""
        self.birthdate = ""
        self.emailAddress = ""
        self.gender =""
        self.age = ""
        self.UsersList =[]
        
    def generateUserData(self):
        for _ in range(250):
            
            userData = faker.simple_profile()
            if userData['birthdate'].year < 1960 or userData['birthdate'].year > 2010:
                continue
            
            ## get the age of the person from the generated random date
            DateOfToday = date.today()    
            age = DateOfToday.year - userData["birthdate"].year
            userDict = {"Username":userData['username'], "Birthdate": userData['birthdate'], "emailAddress":userData['mail'], "gender": userData['sex'], "Age":age}
            # get all random user data
            self.UsersList.append(userDict)

        return self.UsersList
