## imports
from datetime import date
from numpy import append
import requests
from bs4 import BeautifulSoup, Tag
import re
import pandas as pd
import json
import os
from pathlib import Path
# global variable
continents = [
    'Africa', 'Europe', 'Antartica', 'South_America', 'North_America', 'Asia',
    'Australia'
]
session = requests.Session()

# class for country Table in my DB
class CountryTable:
    def __init__(self): 
        self.countriesList = []
        self.AllRequests =[]
        self.countryCapitalsList =[]
        self.CovidCases =[]
        self.CovidVaccinations =[]

    def WikiCrawler(self,param):
    
        # fetch info from wikipedia
        url = "https://en.wikipedia.org/wiki/{}".format(param)

        req = session.get(url)
        if req.status_code == 200:
            return req.content
        else:
            print(f"Error in the GET request Status_code: {req.status_code}")
        return

    ##########################################################
    def getIdxOfName(self, headerRow):
        ColNames = headerRow.text
        cn = ColNames.split('\n')
        listOfColNames = []
        # to get the col index where the name and the capital are
        listOfColNames = [i for i in cn if len(i) != 0]
        idxOfCountryName = 0
        for colIdx in range(len(listOfColNames)):
            # search for the column where we have the formal country name
            if "English" in listOfColNames[
                    colIdx] and "formal name" in listOfColNames[
                        colIdx] or "English" and "short name" in listOfColNames[
                            colIdx]:
                idxOfCountryName = colIdx
                return idxOfCountryName
        return

    ##########################################################
    def getIdxOfCapital(self, headerRow):
        ColNames = headerRow.text
        cn = ColNames.split('\n')
        listOfColNames = []
        # to get the col index where the name and the capital are
        listOfColNames = [i for i in cn if len(i) != 0]
        idxOfCapital = 0
        for colIdx in range(len(listOfColNames)):
            # search for the column where we have the formal country name
            if "Capital" in listOfColNames[colIdx]:
                idxOfCapital = colIdx
                return idxOfCapital
        return
    ############################################
    ## method to get the country name and continent
    def getCountriesList(self):
        for continent in continents:
            # fetch the info
            url = "https://en.wikipedia.org/wiki/List_of_sovereign_states_and_dependent_territories_in_{}".format(
                continent)
            req = requests.get(url)
            if req.status_code == 200:
                soup = BeautifulSoup(req.content, "html.parser")
                # getting all the tables
                #first instance of the table
                tables = soup.find_all('table',attrs={'class': 'wikitable sortable'})
                r =2
                if continent =="South_America": r = 1
                for i in range(0,r): 
                    tableRows = tables[i].find_all('tr')
                    indexOfCName = self.getIdxOfName(tableRows[0])
                    indexOfCapital = self.getIdxOfCapital(tableRows[0])
                    for row in tableRows[1:]:
                        if indexOfCName is not None:
                            allNames = [
                                name for name in row.find_all('td')[indexOfCName]
                            ]
                        if indexOfCapital is not None:
                            allCapitals = [
                            cap for cap in row.find_all('td')[indexOfCapital]
                        ]
                            for cName in allNames:
                                try:
                                    if cName.name == "a":
                                        country = {"Name": "", "Continent": ""}
                                        countName = cName.text
                                        
                                        ## duplicates handling
                                        if "Bahamas" in cName.text:
                                            countName = "Bahamas"
                                        if continent == "Asia" and countName =="Egypt": continue
                                        if continent ==  "Asia" and countName =="Russia": continue
                                        if continent =="Europe" and countName =="Kazakhstan": continue
                                        if continent =="Asia" and countName =="Georgia": continue
                                        if continent =="Australia" and countName =="Indonesia": continue
                                        if continent =="Asia" and countName =="Armenia": continue
                                        if  countName == "Singapore": continue
                                        if countName == "Vatican City": continue
                                        if countName == "Navassa Island": continue
                                        if countName == "Puerto Rico": continue
                                        if countName == "Apia":continue
                                        if countName =="Samoa": continue
                                        if countName =="Tonga": continue
                                        if countName =="United States Virgin Islands": continue
                                        if countName =="Azerbaijan" and continent == "Asia":continue
                                        if countName =="Turkey" and continent =="Asia":continue
                                        if countName =="Cyprus" and continent =="Asia":continue
                                        if "Kingdom of the Netherlands" in countName: continue                                         
                                        if countName == "Sahrawi Arab Democratic Republic": continue
                                        
                                        country["Name"], country["Continent"] = countName, continent.replace("_", " ")
                                        self.countriesList.append(country)
                                except:
                                    pass

        return self.countriesList

#############################################################################
    def TableToText(self,CountryParam):
        # fetch the data

        data = self.WikiCrawler(CountryParam)       
        soup = BeautifulSoup(data,"html.parser")
        
        #get the main table and the rows
        
        tableRows = list(soup.find(class_ ="infobox").tbody.children)
        
        # contain all info of the table in text format
        textList = []
        for i in range(len(tableRows)):
            row = tableRows[i]
            row_children_list = list(row.children)
            for i in range(len(row_children_list)):
                textList.append(row_children_list[i].text.replace('\xa0',' ') )
                
        return textList
###########################################################
    def getAllCountryAttr(self):
        cl = self.getCountriesList()
        countryList_all = []
        coronaVaccinations =self.getCovidVaccinations()
        coronaCases = self.getCovidCases()
      #  print(coronaCases)
        for country in cl:


            print('#################',country["Name"],'#########################')
            flag = False
            countryy = {"Name": country["Name"],"Population":0.0,"Legislature":None,"HDI":0.0,"Currency":None,
            "Continent":country["Continent"], "GDPNominal":0, "GDPPurchasePower":0, "giniIndex":0.0, 
            "CallingCode":None,"drivingSide":None,"Area":0.0, "waterPercentage":0.0, "timeZone":None,"TotalCovidCases":0.0,"TotalCovidVaccinations":0.0}
            
            

            
            
            cn =country['Name'] 
            
            for data in coronaCases:
                if cn in data["Country"]:
                    countryy["TotalCovidCases"] = data["Cases"]
                    break
            
            
            for data in coronaVaccinations:
                if cn in data["Country"]:
                    countryy["TotalCovidVaccinations"] = data["Vaccinations"]
                    break
            
            
            
            if cn == "Navassa Island" or cn == "Clipperton Island":
                continue
            ## they had different names in wikipedia path
            if cn == "Georgia":
                cn = "Georgia_(country)"

            if cn == "Timor-Leste/East Timor":
                cn = "East Timor"

            if cn =="Ireland":
                cn = "Republic_of_Ireland"
            if cn =="Artsakh":
                cn = "Republic_of_Artsakh"
            if "Transnistria / Trans-Dniester" in cn:
                cn = "Transnistria"
            if "Reunion" in cn:
                cn = "Réunion"

            if "Palestine" in cn:
                cn =  "state_of_Palestine" 
            textList =  self.TableToText(cn)
            
                        ## they had different names in wikipedia path
            if cn == "Georgia_(country)":
                cn = "Georgia"

            if cn ==  "East Timor":
                cn = "Timor-Leste/East Timor"

            if cn =="Republic_of_Ireland":

                cn = "Ireland"
            if cn =="Republic_of_Artsakh":
                cn = "Artsakh"
            if "Transnistria" in cn:
                cn = "Transnistria"
                cn = "Transnistria / Trans-Dniester"
                
            if "Réunion" in cn:
                cn = "Reunion"
                

            if "state_of_Palestine" in cn:
                cn =  "Palestine" 
                
            
            
            counter =0
            for text in range(len(textList)):
                
                # get the Legislature
                if re.search(r'^Legislature',textList[text]):
                    if "Legislature of Liberia" in textList[text]:
                        continue  
                    Legislature = None
                    try:
                        Legislature = self.getLegislature(textList[text+1])
                    except IndexError:
                        Legislature = None
                    
                    if cn =="Germany":
                        Legislature= "Bundesrat"
                    if cn =="Norway":
                        Legislature ="Stortinget"
                    countryy["Legislature"] = Legislature

                                    # get the Legislature
                if re.search(r'^Area',textList[text]):  
                    Area,Water = 0.0,0.0
                    try:
                        a = textList[text+2]
                        if "Pelagie Islands" in cn:
                            a = textList[text+1]


                        Area = self.getArea(a)
                        if  "Water" in textList[text+3]:
                            Water = self.getWaterPerc(textList[text+4])
                        else:
                            Water =0
                    except IndexError:
                        Area = None
                        Water = None
                    try:
                        Water =float(Water)
                    except ValueError:
                        Water = 0
                        
                    if cn == "Madagascar":
                        Water = 0.9
                        
                    countryy["Area"] = float(Area)
                    countryy['waterPercentage'] = float(Water)


                # get the gini
                if  re.search(r'^Population',textList[text]):
                    p = 0.0
                    try:
                        pop = textList[text+2]
                        ## special cases
                        if cn == "Russia":
                            pop = re.search(r"[0-9].*",textList[text+2]).group()

                        if cn == "Eritrea":
                            pop = '3,214,000'
                        p = self.getPopulation(pop)
                    except IndexError:
                        pass
                    try:
                        p =float(p)
                    except ValueError:
                        p = 0
                    countryy["Population"] = p
                # get the gini
                if "Gini" in textList[text]:   
                    Gini = 0.0
                    try:
                        Gini = self.getGini(textList[text+1])
                    except IndexError:
                        Gini = 0.0
                    if Gini != None:
                        try:
                           Gini = float(Gini)
                        except ValueError:
                            Gini = 0.0
                    countryy["giniIndex"] = Gini
                    
                # get the GDP
                if "GDP (PPP)" in textList[text]:   
                    gdpppp = 0.0
                    g = textList[text+3] 
                    if "estimate" in textList[text+3] or   "Unknown" in textList[text+3]:
                        g = '0'
                    else: g = textList[text+3]
                    try:
                        gdpppp = self.getGDP(g)
                    except IndexError:
                        gdpppp= 0.0
                    countryy["GDPPurchasePower"] =int(gdpppp)
                    print(gdpppp)
                
                if "GDP (nominal)" in textList[text]:   
                    gdpnominal = 0.0
                    g = textList[text+3] 
                    if "estimate" in textList[text+3] or   "Unknown" in textList[text+3]:
                            g = '0'
                    try:
                        gdpnominal = self.getGDP(g)
                    except IndexError:
                        gdpnominal= 0.0
                    countryy["GDPNominal"] = int(gdpnominal)
                    print(gdpnominal)
            

                
                # get the HDI
                if "HDI" in textList[text]:   
                    HDI = 0.0
                    try:
                        HDI = self.getHDI(textList[text+1])
                    except IndexError:
                        HDI =0.0
                    countryy["HDI"] = float(HDI)
                
                # get the Currency
                if re.search(r'^Currency',textList[text]):   
                    CURR = None
                    try:
                        CURR = self.getCurrency(textList[text+1])
                    except IndexError:
                        CURR =None
                        
                    if cn == "Tuvalu":
                        CURR = "Tuvaluan dollar"

                    countryy["Currency"] = CURR
                    


                # get the TimeZone
                if "Time zone" in textList[text]:   
                    T = None
                    try:
                        T = self.getTimeZone(textList[text+1])
                    except IndexError:
                        T= None
                    countryy["timeZone"] = T

                # get the Driving Side
                if "Driving" in textList[text]:   
                    DS = None
                    try:
                        DS = self.getdrivingSide(textList[text+1])
                    except IndexError:
                        DS= None
                    countryy["drivingSide"] = DS
                    if cn =="Germany":
                        countryy["CallingCode"] = '+49'


                # get the calling code
                if "Calling" in textList[text]:   
                    CC = None
                    try:
                        CC = self.getCallingCode(textList[text+1])
                    except IndexError:
                        CC= None
                    countryy["CallingCode"] = CC
            print(countryy)
            countryList_all.append(countryy)
                    #return
  
        
        return countryList_all

###########################################################
## get covid cases
    def getCovidCases(self):
        # used pandas in this case since this table has a special format
        # pandas in  this context in much simpler
        
        CasesTable = 9
        table = pd.read_html("https://en.wikipedia.org/wiki/COVID-19_pandemic_by_country_and_territory")[CasesTable]
        # print(table)
        for Country, Cases in zip(table['Country.1'], table["Cases"]):
            Casesinfo = {"Country": "", "Cases": 0.0}
            Casesinfo["Country"]= Country
            Casesinfo["Cases"]= Cases
            #print(Casesinfo)
            self.CovidCases.append(Casesinfo)
          #  print(self.CovidCases)
        return self.CovidCases

###########################################################
#### get covid vaccinations
    def getCovidVaccinations(self):

        # used pandas in this case since this table has a special format
        # pandas in  this context in much simpler
        
        vaccinationTable = 15
        table = pd.read_html("https://en.wikipedia.org/wiki/COVID-19_pandemic_by_country_and_territory")[vaccinationTable]
        # print(table)
        for Country, Vaccinations in zip(table['Location.1'], table["Vaccinated[a]"]):
            Vaccinationinfo = {"Country": "", "Vaccinations": 0.0}
            Vaccinationinfo["Country"]= Country
            Vaccinationinfo["Vaccinations"]= Vaccinations
           # print(Vaccinationinfo)
            self.CovidVaccinations.append(Vaccinationinfo)
        return self.CovidVaccinations

##############################################################
    ## subfunctions
    def getHDI(self,val):  
            HDI =  val.replace(' ','')
            try:
                HDI = re.search(r"[0-9].*?(?=([^0-9|\.]))",HDI).group()
            except AttributeError:
                HDI = val
            return HDI

###############################################################
    def getGini(self,val):
    
            GINI =val.replace(' ','')
            try:
                GINI = re.search(r"[0-9].*?(?=([^0-9|\.]))",val).group()
            except AttributeError:
                GINI = val
            return GINI
###############################################################
    def getdrivingSide(self,val):
    
            DS =val.replace(' ','')
            try:
                DS = re.search(r"[A-Za-z].*?(?=([\[| \()]))",DS).group()
            except AttributeError:
                DS = val
            
            return DS
###############################################################
    def getCallingCode(self,val):
        
            CC =val.replace(' ','')
            try:
                CC = re.search(r".*?(?=([\[| \()]))",CC).group()
            except AttributeError:
                CC = val
            return CC
#############################################################
    def getLegislature(self,val):
        leg =val.replace(' ','')
        try:
            leg = re.search(r"[A-Za-z].*?(?=([\[| \()]))",leg).group()
        except AttributeError:
            leg = val
        return leg
#############################################################
    def getCurrency(self,val):
        Curr =val
        try:
            Curr = re.search(r"[A-Za-z].*?(?=[\[|\(])",Curr).group()
        except AttributeError:
            Curr = val
        return Curr
##################################################################
    def getPopulation(self,val):
        p =val
        p =p.replace(',','')
        try:
            p = re.search(r"[0-9].*?(?=[\[| \(|~])",p).group()
        except AttributeError:
            p = val
        return p

##################################################################
    def getTimeZone(self,val):
        tz = val
        tz =tz.replace(',','')
        if "Central Africa Time" in val: return"GMT+2"
        try:
            tz = re.search(r".*?(?=[\(|\[|t|\;|\/])",tz).group()
        except AttributeError:
            tz = val
        return tz
###############################################################
    def getArea(self,val):
        A = val
        A=A.replace(',','')
        try: A = re.search(r"[0-9].*?(?=[^0-9])",A).group()
        except AttributeError: A = val
        return A
###############################################################
    def getWaterPerc(self,val):
        W = val
        W=W.replace(',','')
        try: W = re.search(r".*?(?=[\[| \(|%])",W).group()
        except AttributeError: W = val
        return W
################################################################
    def getGDP(self,val):
        gdp = val
        gdp = gdp.replace("$",'')
        gdp = gdp.replace("€",'')
        gdp = gdp.replace("£",'')
        gdp = gdp.replace("US",'')
        gdp = gdp.replace("NZ",'')
        gdp= gdp.replace(',','')
        nums ={"billion":1_000_000_000, "million":1_000_000,"trillion":1_000_000_000_000}
        for key in nums:
            try:
                if  key in gdp:
                    gdp =re.search(r".*?(?=[b|m|t])", gdp).group()
                    gdp = float(gdp)
                    return gdp * nums[key]
            except AttributeError:    
                gdp =0
                return float(gdp)
        if re.search(r".*?(?=[\[])", gdp):
            gdp=  re.search(r".*?(?=[\[])", gdp).group()
            return float(gdp)
        return gdp




if __name__ == "__main__":
    

    # Objects of classes

    CountryTableInstance = CountryTable()
    
   
    ## ~~~~~~~~~~~~~~~~~~~~~~~~~countries table    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    c =CountryTableInstance.getAllCountryAttr()
    CountryTable_df = pd.DataFrame(c)
    main_folder_path = os.path.dirname(os.getcwd())
    CountryTable_df.to_csv(os.path.join(main_folder_path,"CSV Files/countryTable_data.csv"), sep=',', encoding='utf-8', index=False)



    