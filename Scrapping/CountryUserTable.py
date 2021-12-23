from CountryTableCrawler import *
from UserTable import *
import random

DateFrom = date(2000,1,1)
DateTo = date(2021,11,9)

class CountryUserTable(CountryTable,User):
    def __init__(self):
        self.countryCapitalsList =[]
        self.countriesList = []
        self.UsersList= []
        self.returnList =[]
        ul = self.generateUserData()
        CountryL = self.getCountriesList()
        self.CountryList = CountryL
        self.UList = ul
    
    def getCountryUserData(self):

        cl=  self.CountryList  
        n = []
        for j in cl:
                              
            if "Georgia_(country)" in j["Name"]:
                j["Name"] = "Georgia"
                
            if  "East Timor" in j["Name"]:
                j["Name"] = "Timor-Leste/East Timor"
            
            if "Republic_of_Ireland" in j["Name"] :
                    j["Name"] ="Ireland"
                
            if   "Republic_of_Artsakh" in j["Name"]:
                j["Name"] ="Artsakh"
                
            if  "Transnistria"  in j["Name"]:
                j["Name"] = "Transnistria / Trans-Dniester"
                
            if "Réunion"  in j["Name"]:
                j["Name"] = "Reunion"
                
            if "State_of_Palestine"  in j["Name"]:

                j["Name"] = "Palestine"
            
            n.append(j["Name"])        
        
        for i in self.UList:
            randomCountryIndex = random.randint(1,7)
            if randomCountryIndex !=0:
                
                Tdate = faker.date_between_dates(DateFrom,DateTo)
                rating = random.randint(0,10)
                
                sizeOfwords = random.randint(2,50)
                tReview = faker.sentence(nb_words=sizeOfwords)
                
                Visitedcountry=random.choice(n)
            
                user ={"username":i["Username"], "CountryName":Visitedcountry,"TravelData":str(Tdate), "Rating":rating, "TextualReview":tReview}
                
                self.returnList.append(user)
                
                
            
        return self.returnList, self.UList
        

if __name__ == "__main__":
    
    
    a= CountryUserTable()
    b,userList =a.getCountryUserData()
    
    CountryUserTable_df = pd.DataFrame(b)
    main_folder_path = os.path.dirname(os.getcwd())
    CountryUserTable_df.to_csv(os.path.join(main_folder_path,"CSV Files/CountryUserTable_data.csv"), sep=',', encoding='utf-8', index=False)
    
    
    userTable_df = pd.DataFrame(userList)
    main_folder_path = os.path.dirname(os.getcwd())
    userTable_df.to_csv(os.path.join(main_folder_path,"CSV Files/UserTable_data.csv"), sep=',', encoding='utf-8', index=False)
    main_folder_path = os.path.dirname(os.getcwd())
    userTable_df.to_csv(os.path.join(main_folder_path,"CSV Files/UserTable_data.csv"), sep=',', encoding='utf-8', index=False)
