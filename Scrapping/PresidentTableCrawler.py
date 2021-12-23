from bs4 import BeautifulSoup
from CountryTableCrawler import CountryTable
import re
import datetime
import pandas as pd
import os
from pathlib import Path
import requests

# inheritance
class PresidentTable(CountryTable):
    def __init__(self):
        self.countryCapitalsList =[]
        self.countriesList = []
        self.returnedL = []
        self.presidents = []
        CountryL = self.getCountriesList()
        self.CountryList = CountryL
#################################################
    def getPresident(self):
        for country in self.CountryList:
            CountryName = country["Name"]

            if CountryName == "Navassa Island" or CountryName == "Clipperton Island":
                continue
            ## they had different names in wikipedia path
            if CountryName == "Georgia":
                CountryName = "Georgia_(country)"

            if CountryName == "Timor-Leste/East Timor":
                CountryName = "East Timor"

            if CountryName =="Ireland":
                CountryName = "Republic_of_Ireland"
            if CountryName =="Artsakh":
                CountryName = "Republic_of_Artsakh"
            if "Transnistria / Trans-Dniester" in CountryName:
                CountryName = "Transnistria"
            if "Reunion" in CountryName:
                CountryName = "Réunion"

            if "Palestine" in CountryName:
                CountryName = "State_of_Palestine"
            textList = self.TableToText(CountryName)
            
            counter =0
            for i in range(len(textList)):
                
                if "Jamaica" in CountryName:
                    counter+=1
                if (
                    "President" in textList[i] or "Monarch" in textList[i] or " Chairman of the Transitional Military Council" in textList[i]
                     or "Chairman of the National Committee of Reconciliation and Development" in textList[i] or "Head of State" in textList[i]
                    or "Chairman of the Presidential Council" in textList[i] or "King" in textList[i] or "Emperor" in textList[i]  

                    ):
                    if counter ==0:
                        if " King " in textList[i] :
                            try:
                                
                                re.search(r"[ |]King.?(?=(\W))",textList[i]).group()
                                counter+=1
                                #print(CountryName)
                                    # print("BREAKING")
                                    # continue
                            except: 
                                counter =0
                                continue
 
                   #print("HERE")
                 #   print(textList[i])
                    if "Jamaica" in CountryName:
                        continue
                    a= textList[i].replace("President",'')
                    a = a.replace("•",'')
                    b = textList[i].replace("Monarch",'')
                    b = b.replace("•",'')
                    if "President" in textList[i] :
                        if len(a) >2:
                            continue
                    if "Monarch" in textList[i]:
                        if  len(b)>2:
                            continue

                    exceptionsList = ["Deputy President","President of the Constitutional Court","President of the Assembly","President of the Senate","Senate President",
                    "Assembly President", "Council President","Vice President","Vice-President","President of the  National Assembly", "Kingdom"," Derg military rule and overthrow of Emperor"
                    ," King\"", "King of the Franks", "the Kingdom of Norway", "Alban Sumana Kingsford Bagbin", "King's Song","Nation Emir  "
                   ,"United Arab Emirates","state","King Christian stood by the lofty mast\"","Kingstown"
                    ,"JamaicaJumieka (Jamaican Patois) Anthem: \"Jamaica, Land We Love\""
                    ]
                    
                    flag = False
                    for ii in exceptionsList:
                        if  ii in textList[i]:
                            flag = True
                            break
                    if (flag): continue                            
                    presidentName= ""
                    try:
                     #   print("HERE")
                        presidentName = re.search(r".*?(?=[\[|\(])",textList[i+1]).group()
                    except:
                        try:
                            presidentName = textList[i+1]
                        except:
                            presidentName =textList[i]                     
                    #exceptions
                    if "Elizabeth II" in presidentName: presidentName = textList[i+3]
                    if "Cook Islands" in CountryName:presidentName = "Mark Brown"    # pn = p.getPresident()
                    if "Eswatini" in CountryName: presidentName = "Cleopas Dlamini"

        
                    
                    #print(CountryName ,presidentName)     
                    #print((presidentName,CountryName))
                                        
                    p = self.ExceptionsHandling(CountryName)
                    if p=="" or ("Jamaica" in CountryName and counter ==2): 
                        print(presidentName,'->',CountryName)
                        self.presidents.append((presidentName,CountryName))
                    
            p = self.ExceptionsHandling(CountryName)
            if p != "":
                presidentName = p
                #print(presidentName,CountryName)
                self.presidents.append((presidentName,CountryName)) 
                
      
        return self.presidents
#########################################################################################
    def getPresidentDetails(self):
        AllNames = open("PresidentsNames.txt","r", encoding='utf-8').readlines()

        for Name in AllNames:
            Name = Name.strip()
            pName = Name.split(',')[0]
            pName = pName.strip()
            cName = Name.split(',')[1]
            cName = cName.strip()
            presidentDict ={"Name":"","CountryName":"","PoliticalParty": "","birthDate":"","assumedOfficeDate":""}
        
## Exceptions in names
            if "Mahmoud Abbasa" in pName:pName = "Mahmoud Abbas"
            if "Sir" in pName: pName = pName.replace("Sir","")
            if "Belgium" in cName:pName = "Philippe_of_Belgium"
            if "Luxembourg" in cName: pName = "Henri,_Grand_Duke_of_Luxembourg"
            if "Antigua and Barbuda" in cName: pName = "Rodney_Williams_(governor-general)"
            if "Bahamas" in cName:pName = "Cornelius_A._Smith"
            if "Costa Rica" in cName:pName = "Carlos_Alvarado_Quesada"  
            if "Bangladesh" in cName: pName = "Abdul_Hamid_(politician)"
            if "Cook Islands" in cName: pName = "Mark_Brown_(Cook_Islands)"
            if "British Virgin Islands" in cName:pName = "John_Rankin_(diplomat)"
            if "Montserrat" in cName:pName = "Andrew_Pearce_(diplomat)"
            if "Puerto Rico" in cName:pName = "Pedro_Pierluisi"
            if "Jamaica" in cName: pName = "Patrick_Allen_(governor-general)"
            if "Morocco" in cName: pName = "Mohammed_VI_of_Morocco"
            if "Bosnia and Herzegovina" in cName: pName = "Christian_Schmidt_(politician)"
            if "Malaysia" in cName:pName = "Abdullah_of_Pahang"
            
            textList = self.TableToText(pName)
            if "Belgium" in cName: pName = "Philippe"
            if "Luxembourg" in cName: pName = "Henri"
            if "Antigua and Barbuda" in cName: pName = "Rodney Williams"
            if "Bahamas" in cName: pName = "Sir Cornelius A. Smith"
            if "Costa Rica" in cName: pName = "Carlos Alvarado Quesada"
            if "Cook Islands" in cName: pName = "Mark Brown"
            if "Bangladesh" in cName: pName = "Abdul Hamid"
            if "Montserrat" in cName: pName = "Andrew Pearce"
            if "British Virgin Islands" in cName:pName = "John Rankin"
            if "Morocco" in cName: pName = "Mohammed VI"
            
            
            
            presidentDict["Name"]=pName
            presidentDict["CountryName"]=cName
            counter =0
            for textIdx in range(len(textList)):
                if "Assumed office" in textList[textIdx] or "Reign" in textList[textIdx]:
                    if counter ==0:
                        presidentassumedDate = self.getAssumedOfficeDate(textList=textList,textIdx=textIdx,cName=cName,pName=pName)
                        presidentDict["assumedOfficeDate"]= str(presidentassumedDate)
                    counter+=1
                if "Political party" in textList[textIdx]:
                    pp =""
                    pp = self.getPoliticalParty(textList=textList,textIdx=textIdx)
                    presidentDict["PoliticalParty"]= pp
            
                if "Born" in textList[textIdx]:
                    if "Bornito" in textList[textIdx] or "Bornes"in textList[textIdx] or "Borno State" in textList[textIdx]:
                        continue
                   # print("\n")
                   # print("THE TEXT ",textList[textIdx])
                    dob = self.getDOB(textList=textList,textIdx=textIdx)
                    print(dob)
                    presidentDict["birthDate"]= str(dob)
                    
            if "Georgia_(country)" in cName:
                cName = "Georgia"
                presidentDict["CountryName"]= cName
             
            if  "East Timor" in cName:
                cName = "Timor-Leste/East Timor"
                presidentDict["CountryName"]= cName
            
            if "Republic_of_Ireland" in cName :
                    cName ="Ireland"
                    presidentDict["CountryName"]= cName
                
            if   "Republic_of_Artsakh" in cName:
                cName ="Artsakh"
                presidentDict["CountryName"]= cName
                
            if  "Transnistria"  in cName:
                cName = "Transnistria / Trans-Dniester"
                presidentDict["CountryName"]= cName
                
            if "Réunion"  in cName:
                cName = "Reunion"
                presidentDict["CountryName"]= cName
                
            if "State_of_Palestine"  in cName:

                cName = "Palestine"
                presidentDict["CountryName"]= cName

            print(presidentDict)
            self.returnedL.append(presidentDict)
        return self.returnedL
#################################################
    def getAssumedOfficeDate(self,textList,textIdx,cName,pName):
        assumedOffice = ""
        if "" in textList[textIdx+1]:
            if "South Korea" in cName:
                adate = "2017-05-10"
                assumedOfficeDate = datetime.datetime.strptime(adate, '%Y-%m-%d').date()
                print(pName, "--",cName, "--",assumedOfficeDate)  
                return str(assumedOfficeDate)
            if "State_of_Palestine" in cName:
                adate = "2005-01-15"
                assumedOfficeDate = datetime.datetime.strptime(adate, '%Y-%m-%d').date()
                print(pName, "--",cName, "--",assumedOfficeDate)  
                return str(assumedOfficeDate)
            if "Federated States of Micronesia" in cName:
                adate = "2019-05-11"
                assumedOfficeDate = datetime.datetime.strptime(adate, '%Y-%m-%d').date()
                print(pName, "--",cName, "--",assumedOfficeDate)  
                return str(assumedOfficeDate)
            
            if "San Marino" in cName:
                adate ="2021-10-1"
                assumedOfficeDate = datetime.datetime.strptime(adate, '%Y-%m-%d').date()
                print(pName, "--",cName, "--",assumedOfficeDate)  
                return str(assumedOfficeDate)
            
            if "Bhutan" in cName:
                adate ="2006-12-9"
                assumedOfficeDate = datetime.datetime.strptime(adate, '%Y-%m-%d').date()
                print(pName, "--",cName, "--",assumedOfficeDate)  
                return str(assumedOfficeDate)
            
                                    
            try:
                assumedOffice = textList[textIdx].replace("Assumed office",'')
        #           assumedOffice = textList[textIdx].replace("\n",'')
                ao = assumedOffice.split()
                if "January" in ao[0] or "February" in ao[0] or "March" in ao[0] or  "April" in ao[0] or "June" in ao[0] or "July" in ao[0] or "August" in ao[0] or "September" in ao[0] or "October" in ao[0] or "November"  in ao[0] or "December" in ao[0]:
                 #   print("HERE", ao[0])
                    assumedOffice = f"{ao[1]} {ao[0]} {ao[2]}"
                    assumedOffice = assumedOffice.replace(',','')
                assumedOffice = re.search(r".*?(?=[\[|\(|\-])",assumedOffice).group(0)


                if "Acting" in assumedOffice:
                    idx = assumedOffice.find("Acting")
                    assumedOffice = assumedOffice[:idx]
                assumedOffice = assumedOffice.split()                                
            except AttributeError:
                assumedOffice = textList[textIdx].replace("Assumed office",'')
                
                if "January" in ao[0] or "February" in ao[0] or "March" in ao[0] or  "April" in ao[0] or "June" in ao[0] or "July" in ao[0] or "August" in ao[0] or "September" in ao[0] or "October" in ao[0] or "November"  in ao[0] or "December" in ao[0]:
                  #  print("HERE", ao[0])
                    assumedOffice = f"{ao[1]} {ao[0]} {ao[2]}"
                    assumedOffice = assumedOffice.replace(',','')
        #          
                if "Acting" in assumedOffice:
                    idx = assumedOffice.find("Acting")
                    assumedOffice = assumedOffice[:idx]
                assumedOffice = assumedOffice.split()

        if "Reign" in textList[textIdx]:
            try:
                assumedOffice = textList[textIdx+1].replace("Assumed office",'')
                
                
                ao = assumedOffice.split()
                if "January" in ao[0] or "February" in ao[0] or "March" in ao[0] or  "April" in ao[0] or "June" in ao[0] or "July" in ao[0] or "August" in ao[0] or "September" in ao[0] or "October" in ao[0] or "November"  in ao[0] or "December" in ao[0]:
                  #  print("HERE", ao[0])
                    assumedOffice = f"{ao[1]} {ao[0]} {ao[2]}"
                    assumedOffice = assumedOffice.replace(',','')
        #           assumedOffice = textList[textIdx].replace("\n",'')
                assumedOffice = re.search(r".*?(?=[\[|\(|\-])",assumedOffice).group(0)
                if "Acting" in assumedOffice:
                    idx = assumedOffice.find("Acting")
                    assumedOffice = assumedOffice[:idx]
                assumedOffice = assumedOffice.split()

                
            except AttributeError:
                assumedOffice = textList[textIdx+1].replace("Assumed office",'') 
                if "January" in ao[0] or "February" in ao[0] or "March" in ao[0] or  "April" in ao[0] or "June" in ao[0] or "July" in ao[0] or "August" in ao[0] or "September" in ao[0] or "October" in ao[0] or "November"  in ao[0] or "December" in ao[0]:
                   # print("HERE", ao[0])
                    assumedOffice = f"{ao[1]} {ao[0]} {ao[2]}"
                    assumedOffice = assumedOffice.replace(',','')
        #          
                
                if "Acting" in assumedOffice:
                    idx = assumedOffice.find("Acting")
                    assumedOffice = assumedOffice[:idx]
                assumedOffice = assumedOffice.split()
                
        #          assumedOffice = textList[textIdx].replace("\n",'')
        
       # print(assumedOffice)
        datetime_object = datetime.datetime.strptime(assumedOffice[1], "%B")
        month_number = datetime_object.month
        
        
        adate = f"{assumedOffice[2]}-{month_number}-{assumedOffice[0]}"




        try:
            adate = re.search(r"[0-9|\-].*", adate).group()
        except AttributeError:
            adate = adate
        # if "South Africa" in cName:
        #     adate= "2018-02-14"
        assumedOfficeDate = datetime.datetime.strptime(adate, '%Y-%m-%d').date()
        print(pName, "--",cName, "--",assumedOfficeDate)    
        return str(assumedOfficeDate)
#######################################################################################
    def getPoliticalParty(self,textList,textIdx):
        pp = ""
        try:
            pp = re.search(r".*?(?=([\[|\(]))", textList[textIdx+1]).group(0)
        except AttributeError:
            pp = textList[textIdx+1]
        print(pp)
        return pp
##################################################################################
    def ExceptionsHandling(self,countryName):
        presidentName =""
        if "Mali" in countryName: presidentName = "Assimi Goïta"
        if "Libya" in countryName: presidentName ="Mohamed al-Menfi"
        if "Cuba" in countryName: presidentName ="Miguel Díaz-Canel"
        if "Andorra" in countryName: presidentName ="Xavier Espot Zamora"
        if "Bosnia and Herzegovina" in countryName: presidentName ="Christian Schmidt"
        if "San Marino" in countryName: presidentName ="Francesco Mussoni"
        if "Switzerland" in countryName: presidentName ="Guy Parmelin"
        if "Bhutan" in countryName: presidentName ="Jigme Khesar Namgyel Wangchuck"
        if "China" in countryName: presidentName ="Li Keqiang"
        if "North Korea" in countryName: presidentName ="Kim Jong-un"
        if "Kuwait" in countryName: presidentName ="Nawaf Al-Ahmad Al-Jaber Al-Sabah"
        if "Laos" in countryName: presidentName ="Thongloun Sisoulith"
        if "Oman" in countryName: presidentName ="Haitham bin Tariq"
        if "Qatar" in countryName: presidentName = "Tamim bin Hamad"
        if "Jamaica" in countryName: presidentName = "Patrick Allen"
        if "Afghanistan" in countryName: presidentName = "Hibatullah Akhundzada"
        if "Eswatini" in countryName: presidentName = "Mswati III"
        if "Brunei" in countryName: presidentName = "Hassanal Bolkiah"
        

       # if "Saudi Arabia" in countryName: presidentName =
        
        
        if presidentName!="":
            print(presidentName,'->',countryName)
        return presidentName    

###################################################################################
    def getDOB(self, textList,textIdx):
        dob = ""
        try:
            dob =  re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2})",textList[textIdx+1]).group(0)
            dob = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
        except:
            try:
                dob = re.search(r"[0-9][0-9][0-9][0-9]",textList[textIdx+1]).group()
                dob = f"{dob}-01-01"
                dob = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
            except AttributeError:
                dob = None
        return dob    

          
        
        



########################################################################################
if __name__ == "__main__":
    p = PresidentTable()
    # pres = p.getPresidentDetails()
    # print(pres)
    
    # PresidentTable_df = pd.DataFrame(pres)
    # main_folder_path = os.path.dirname(os.getcwd())
    # PresidentTable_df.to_csv(os.path.join(main_folder_path,"CSV Files/PresidentTable_data.csv"), sep=',', encoding='utf-8', index=False)


    pn = p.getPresident()
    
    # for faster execution I will save the returned list to a file
    with open("PresidentsNames.txt","w") as f:
         for i in pn:
             f.write(str(f"{i[0]},{i[1]}"))
             f.write('\n')
    
    f.close()
