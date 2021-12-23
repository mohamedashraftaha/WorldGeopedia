import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
from CountryTableCrawler import CountryTable
import os
from pathlib import Path

# inheritence to make use of existing functions in other table


class CapitalTable(CountryTable):
    def __init__(self):
        self.CapitalList = []
        self.countriesList = []
        self.returnedList = []
        self.CapitalAreas = []
        CountryL = self.getCountriesList()
        self.CList = CountryL
        

    ###############################################
    def getCapitals(self):
        for country in self.CList:
            cn = country["Name"]
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
                cn =  "State_of_Palestine" 
                print("HERE")
            
            
            textList = self.TableToText(cn)
            
            
            
            
            counter =0
            for i in range(len(textList)):
                if "Capital" in textList[i] or "State_of_Palestine" in cn:
                    if counter ==0:

                        try:
                            cap = re.search(r".*?(?=[0-9|\(|\[])",textList[i+1]).group()
                        except AttributeError:
                            cap = textList[i+1]

                        
                        if "Switzerland" in cn:
                            cap = "Bern"
                            
                        if "Vanuatu" in cn:
                            cap = "Port Villa"
                        if "Israel" in cn:
                            cap =  "Tel Aviv" 

        
                        if "State_of_Palestine" in cn:
                            cn =  "Palestine"
                            cap = "Jerusalem" 
                        print(country["Name"],cap)
                        cn = cn.replace("\n","")
                        cap.replace("\n","")
                        capitalInformation = {"Name":cap, "CountryName": cn}
                    counter+=1
 
               
                

            self.CapitalList.append(capitalInformation)
        return self.CapitalList            
    ###############################################

    def getCapitalInfo(self):
        # textList =self.TableToText("Cairo")
        # for i in textList:
        #     pass          #print(i)
        AllCapitals = open("CapitalNames.txt","r").readlines()
        # get Areas
        # computed once and contains all areas
        Areas = self.getCapitalArea()
        for capital in AllCapitals:
            capital= capital.strip()
            cap = capital.split(',')[0]
            cn = capital.split(',')[1]
            if cn == "Luxembourg":
                cap = "Luxembourg City"

            if cn == "San Marino":
                cap = "City of San Marino"
                
            if "Benin" in cn:
                cap = "Porto-Novo"

            if"Sahrawi Arab Democratic Republic" in cn:
                cap= "Laayoune"  
            
            if "Pristinaa" in cap:
                cap = "Pristina"  
                
            if "Kiribati" in cn:
                cap = "South Tarawa"
                
                
            if "Chile" in cn:
                cap = "Santiago"
            
            cn = cn.replace("\n",'')
            capitalInfo = {"Name": cap, "Coordinates": None, "Population": 0.0,
                           "Area": 0.0, "CountryName": cn, "governor": None}
          
            try:
                temp = requests.get(f"https://en.wikipedia.org/wiki/{cap}")
                soupp = BeautifulSoup(temp.content, "html.parser")  
                list(soupp.find(class_="infobox").tbody.children)
            except AttributeError:
                if "Bahamas" in cn:
                    cn = "Bahamas"
                cap= cap.strip()
                cn = cn.strip()
                cn = cn.replace("\n",'')
                cap = f"{cap},_{cn}"
                
                if "Washington" in cap:
                    cap = "Washington,_D.C."
            if cn == "Navassa Island" or cn == "Clipperton Island":
                continue
            # no capital
            

  
            if "Bouvet Island" in cn:
                continue
            # if "Comoros" in cn:
            #     cap = "Moroni,_Comoros"
            coordinates = self.getCoordinates(cap)
            if coordinates == "":
                coordinates = None
                
            if "Suva" in cap :
                coordinates= "18.1405° S – 178.4233° E"
            capitalInfo["Coordinates"] = coordinates


            #print("AREAS",Areas)
            ar = "NOT FOUND"
            for data in Areas:
                if cap in data["Capital"]:
                    #print(capital["Name"], data["Capital"])
                    #print("EQUAL")
                    ar = data["Area"]
                    capitalInfo["Area"] = ar
                    break
            if ar =="NOT FOUND":
                capitalInfo["Area"]=0.0
            print(cn, "######################", cap)  
            if "Washington,_D.C." in cap:
                cn= "United States"
                cn = cn.replace("\n",'')
            
            try:       
                textList = self.TableToText(cap)
                                        
    
            except:
                print(f"ERROR HERE CHECK {cn}")
            for textIdx in range(len(textList)):
                if "Population" in textList[textIdx]:
                    if "Population by native language" in textList[textIdx] or "Population by age" in textList[textIdx] or "Population by ethnicity" in textList[textIdx] or "Highest Record Population" in textList[textIdx] or "Population rank" in textList[textIdx]:
                        continue
                    Pop = ""
                    Pop = self.getCapitalPopulation(
                        textIdx=textIdx, textList=textList, cap=cap)
                    if Pop == "":
                        Pop = textList[textIdx+2]
                        try:
                            Pop = re.search(r".*?(?=[\[|\(])", Pop).group()
                        except AttributeError:
                            Pop = Pop
                    if cn == "China":
                        Pop = "21893095"
                        continue

                    p = Pop.replace(',', '')
                    if "million" in p:
                        pp = re.search(r"[0-9].*?(?=[million])", p).group()
                        pp = float(pp)
                        p = pp * 1_000_000
                    try:
                        p = float(p)
                    except ValueError:
                        p = 0.0

                    if "Beirut" in cap:
                        p = float(361366)

                    if "Damascus" in cap:
                        p = float(2_079_000)

                    if "Canberra" in cap:
                        p = float(431380)

                    if "South Tarawa" in cap:
                        p = float(63439)
                    capitalInfo["Population"] = p

                    if "Singapore" in cap:
                        p = float(5453600)
                    
                    capitalInfo['Population'] = p

                if (
                "Government" in textList[textIdx] 
                and "Government of the Capital District" not in textList[textIdx] and "Seoul Metropolitan Government" not in textList[textIdx]
                and "Taipei City Government" not in textList[textIdx] and "BudapestInfo OfficialGovernment Official" not in textList[textIdx] 
                and "Chief of Government" not in textList[textIdx] and "Government of Tegucigalpa" not in textList[textIdx]
                ):
                    print("---------------", textList[textIdx],'---------------------')
                    Gov = None
                    Gov = self.getGovernor(
                        textIdx=textIdx, textList=textList, cap=cap)
                    
                    if "London" in cap:
                        Gov = "Sadiq Khan"
                        
                    if "Naypyidaw" in cap:
                        Gov = "Myo Aung"
                    print("~~~~~~~~~~~~~~~~~~~~~",Gov, "~~~~~~~~~~~~~~~~~~~~~","\n")
                    
                    if Gov == "":
                        Gov = None
                    if Gov != None:
                        Gov = Gov.strip()
                        Gov = Gov.replace("\n",'')
                    capitalInfo["governor"]= Gov
                    
  
            if "Georgia_(country)" in cn:
                cn = "Georgia"
                capitalInfo["CountryName"]= cn
             
            if  "East Timor" in cn:
                cn = "Timor-Leste/East Timor"
                capitalInfo["CountryName"]= cn
             
            if "Republic_of_Ireland" in cn :
                cn ="Ireland"
                capitalInfo["CountryName"]= cn
             
            if   "Republic_of_Artsakh" in cn:
                cn ="Artsakh"
                capitalInfo["CountryName"]= cn
             
            if  "Transnistria"  in cn:
                cn = "Transnistria"
                capitalInfo["CountryName"]= cn
             
            if "Réunion"  in cn:
                cn = "Reunion"
                capitalInfo["CountryName"]= cn
             
            if "State_of_Palestine"  in cn:

                cn = "Palestine"
                capitalInfo["CountryName"]= cn
            if "Washington" in cap:
                cn = "United States"
                capitalInfo["CountryName"]= cn   
            print(capitalInfo)
            self.returnedList.append(capitalInfo)
        return self.returnedList

####################################################
    def getCoordinates(self, val):
        xCoordinate = ""
        yCoordinate = ""
        data = self.WikiCrawler(val)
        soup = BeautifulSoup(data, 'html.parser')
       # print(soup)
        tableRows = list(soup.find(class_='infobox').tbody.children)
        for i in range(len(tableRows)):
            row = tableRows[i]
            x = row.find(class_="latitude")
            y = row.find(class_="longitude")
            if x:
                xCoordinate = x.text
            if y:
                yCoordinate = y.text

            if xCoordinate and yCoordinate:
                return f"{xCoordinate} - {yCoordinate}"

####################################################
    def getCapitalPopulation(self, textIdx, textList, cap):
        Pop = ""
        for i in range(textIdx+1, len(textList)):
            #print(textList[i])
            if "city" in textList[i] or "City" in textList[i] and "City website" not in textList[i] and "City of Valletta" not in textList[i] and "Taipei City Government" not in textList[i]:
                #print("HERE CITY")
                if "Nicosia" in cap and "North Nicosia" not in cap:
                    Pop = textList[i+1].split()[1]
                    return Pop
                Pop = textList[i+1]
                try:
                    Pop = re.search(r".*?(?=[\[|\(])", Pop).group()
                    return Pop
                except AttributeError:
                    Pop = Pop
                    return Pop
            if "Total" in textList[i]:
              #  print("HERE TOTAL")
                Pop = textList[i+1]
                try:
                    Pop = re.search(r".*?(?=[\[|\(])", Pop).group()
                    return Pop
                except AttributeError:
                    Pop = Pop
                    return Pop
            if "Metro" in textList[i]:
              #  print("HERE METRO")
                Pop = textList[i+1]
                try:
                    Pop = re.search(r".*?(?=[\[|\(])", Pop).group()
                    return Pop
                except AttributeError:
                    Pop = Pop
                    return Pop

        return Pop
#################################################

    def getCapitalArea(self):
        ar = ""
        # used pandas in this case since this table has a special format
        # pandas in  this context in much simpler
        table = pd.read_html(
            'https://en.wikipedia.org/wiki/List_of_national_capitals_by_area')[1]
        # print(table)
        info = {"Capital": "", "Area": 0.0}
        for capital, Area in zip(table['Capital']['Capital'], table["Area"]['(km2)']):
            cap, a = None, None
            try:
                cap = re.search(r".*?(?=[\[])", str(capital)).group()
            except AttributeError:
                cap = capital

            # print(type(Area))
            if isinstance(Area, str):
               # print("HERE")
                Area = Area.replace(',', '')

            try:
                a = re.search(r".*?(?=[\[])", str(Area)).group()
            except AttributeError:
                a = Area

            info = {"Capital": cap, "Area": float(a)}
            self.CapitalAreas.append(info)

        return self.CapitalAreas
    ###########################################

    def getGovernor(self, textIdx, textList, cap):
        gov = ""

        for i in range(textIdx+1, len(textList)):
            if  ("Governor" in textList[i] or "Minister-President" in textList[i] or "Mayor" in textList[i] or "Sultan" in textList[i] or "Akim" in textList[i] 
            or "General Manager of City Municipality" in textList[i] or "Capitano" in textList[i]
            or "Chief of Government" in textList[i] or "Chairman of Pyongyang People's Committee" in textList[i]
            ):


                if ("Mayor-council government" in textList[i]  or "Mayor–council" in textList[i]
                 or "Mayor–Council" in textList[i] or "Mayor-Council" in textList[i] or "Mayor-council" in textList[i] or "Deputy Mayor"  in textList[i] or "Vice-governor" in textList[i]
                or "Mayor – Council" in textList[i] or "Mayor and council" in textList[i] or "Mayor - Council" in textList[i]): continue
                print("HEREE  ", textList[i])
                gov = textList[i+1]
                try:
                    gov = re.search(r".*?(?=([\[|\(]))", gov).group()
                    return gov
                except AttributeError:
                    gov = gov
                    return gov

        return gov
    ###################################################

    def test(self):
        for i in self.countryCapitalsList:
            print(i["Name"], "        ", i["CountryName"])


#######################################################
if __name__ == '__main__':
    a = CapitalTable()
    
    
    ########## uncomment and run once for faster execution

    # c = a.getCapitals() 
    # # for faster execution I will save the returned list to a file
    # with open("CapitalNames.txt","w") as f:
    #      for i in c:
    #          cap, cn = i["Name"],i["CountryName"]
    #          f.write(str(f"{cap},{cn}"))
    #          f.write('\n')
    
    # f.close()
    
    a = a.getCapitalInfo()
    CapitalTable_df = pd.DataFrame(a)
    main_folder_path = os.path.dirname(os.getcwd())
    CapitalTable_df.to_csv(os.path.join(main_folder_path,"CSV Files/CapitalTable_data.csv"), sep=',', encoding='utf-8', index=False)
