from CountryTableCrawler import *

import os
from pathlib import Path




class LanguagesTable(CountryTable):
    
    def __init__(self):
        self.countryCapitalsList =[]
        self.countriesList = []
        self.Languages = []
        CountryL = self.getCountriesList()
        self.CountryList = CountryL
        
    
    def getOfficialLanguages(self):
         
        table = pd.read_html("https://en.wikipedia.org/wiki/List_of_official_languages_by_country_and_territory")[1]
        
        
        for country,Languages in zip(table['Country'],table['Official language']):
            
            for c in self.CountryList:
                
                try:
                    country = re.search(r".*?(?=([\[|\(]))",country).group()
                except:
                    country = country
                if country in c["Name"]:
                    
                    languages = Languages.split()
                    if languages[0] == "Official":
                        continue

                    if languages[0] =="None":
                        lang = languages[1].replace('(','')
                        languages.remove(languages[0])
                        languages = languages[0].replace('(',"")
                        languages = languages.replace(',','')
                        l =[]
                        l.append(languages)        
                        languages = l       
                    
                    
                    for i in languages:
                        ## Exception
                       
                        if (
                            
                             "Official" in i or "other" in i or  "37" in i or  "languages" in i or "as" in i 
                            or "Sign" in i  or "Language" in i or "language" in i or  "of" in i or  "intercultural" in i or "relation)" in i 
                            or  "official" in i  or  "subsidiary" in i or  "Standard" in i
                            ):
                            continue
                    
                        country_Languages = {"CountryName":"", "Languages":[]}
                        try:
                            country_Languages["CountryName"]= re.search(r".*?(?=([\[|\(]))",country).group()
                        except AttributeError:
                            country_Languages["CountryName"]= country
                    
                        try:
                            i = re.search(r".*?(?=([\[|\(]))",i).group()
                        except AttributeError:
                            i = i
                        if len(i) != 0:
                            country_Languages["Languages"]= i.replace(',','')
                        else:
                            continue
                    # print(country_Languages)
                        self.Languages.append(country_Languages)
                    break
                    country
        return self.Languages
            
            
    
        # for Country, Cases in zip(table['Country.1'], table["Cases"]):
        #     Casesinfo = {"Country": "", "Cases": 0.0}
        #     Casesinfo["Country"]= Country
        #     Casesinfo["Cases"]= Cases
        #     #print(Casesinfo)
        #     self.CovidCases.append(Casesinfo)
        #   #  print(self.CovidCases)
        # return self.CovidCases

        # for i in self.CountryList:
        #     pass
        

if __name__ == "__main__":
    l = LanguagesTable()
    
    lang = l.getOfficialLanguages()

    LanguagesTable_df = pd.DataFrame(lang)
    # generic to work on Windows or Linux
    main_folder_path = os.path.dirname(os.getcwd())
    LanguagesTable_df.to_csv(os.path.join(main_folder_path,"CSV Files/LanguagesTable_data.csv"), sep=',', encoding='utf-8', index=False)


