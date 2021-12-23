from CountryTableCrawler import *
from CapitalTableCrawler import *
from UserTable import *
from LanguagesTable import *
from PresidentTableCrawler import *



if __name__ == "__main__":
    

    # Objects of classes

    CountryTableInstance = CountryTable()
    CapitalTableInstance = CapitalTable()
    LanguagesTableInstance = LanguagesTable()
    PresidentTableInstance = PresidentTable()
    UserTableInstance = User()

    main_folder_path = os.path.dirname(os.getcwd())
    
    ## ~~~~~~~~~~~~~~~~~~~~~~~~~countries table    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    c =CountryTableInstance.getAllCountryAttr()
    CountryTable_df = pd.DataFrame(c)
    CountryTable_df.to_csv(os.path.join(main_folder_path,"CSV Files/countryTable_data.csv"), sep=',', encoding='utf-8', index=False)



    
    
#    c = CapitalTableInstance.getCapitals() 
    ########## uncomment and run once for faster execution

    # for faster execution I will save the returned list to a file
    # with open("CapitalNames.txt","w") as f:
    #      for i in c:
    #          cap, cn = i["Name"],i["CountryName"]
    #          f.write(str(f"{cap},{cn}"))
    #          f.write('\n')
    
    # f.close()
    
    ## ~~~~~~~~~~~~~~~~~`capitals table~~~~~~~~~~~~~~~~~~~~~~
    
    CapitalsList = CapitalTableInstance.getCapitalInfo()
    CapitalTable_df = pd.DataFrame(CapitalsList)
    CapitalTable_df.to_csv(os.path.join(main_folder_path,"CSV Files/CapitalTable_data.csv"), sep=',', encoding='utf-8', index=False)







    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`` president table ~~~~~~~~~~~~~~~~~~~~~~~~~
    # pn =PresidentTableInstance.getPresident    
    # # for faster execution I will save the returned list to a file
    # with open("PresidentsNames.txt","w") as f:
    #      for i in pn:
    #          f.write(str(f"{i[0]},{i[1]}"))
    #          f.write('\n')
    
    # f.close()

    
    
    pres = PresidentTableInstance.getPresidentDetails()
    
    PresidentTable_df = pd.DataFrame(pres)
    PresidentTable_df.to_csv(os.path.join(main_folder_path,"CSV Files/PresidentTable_data.csv"), sep=',', encoding='utf-8', index=False)


    #~~~~~~~~~~~~~~~~~  languages table ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~``
    lang = LanguagesTableInstance.getOfficialLanguages()

    LanguagesTable_df = pd.DataFrame(lang)
    LanguagesTable_df.to_csv(os.path.join(main_folder_path,"CSV Files/LanguagesTable_data.csv"), sep=',', encoding='utf-8', index=False)
