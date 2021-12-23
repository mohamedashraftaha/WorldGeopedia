import re
from flask import Flask,request,render_template,redirect
import flask
import MySQLdb
import json
import datetime
from datetime import date
import phonenumbers
import sys
#constant 
debug = 0 # set 1 to activate

app = Flask(__name__,template_folder='templates')

mydb = None

# wrapper function to attempt to reconnect if the connection failed
def attemptToReconnect(func):
    """  This is a decorator to reconnect when the connection to the server is lost"""
    flag = None
    def wrapper():
       # print("~~~~~~~ WRAPPER Start ~~~~~~~~")
        flag = 0
        try:
            func()
            if debug:
                print("HERE")
            return func()
        except Exception as e:
            exceptionMsg = e.args[1]
            
            print("Waiting to connect")
            print(exceptionMsg)
            
            if "Can't connect to MySQL server" in exceptionMsg:
                print("Error")
                flag = 1
                return flag
            for i in e.args:
                if "MySQL server has gone away" in i:
                    flag = 1
                    print(flag)
                    return flag
            if debug:
                print(exceptionMsg)
            raise exceptionMsg
    
    # avoided stack overflow
    if wrapper() ==1:
        wrapper()
    return wrapper

@attemptToReconnect
def init_db():
    """Initializes the database"""
    global mydb
    mydb = MySQLdb.connect(host = "www.db4free.net", port = 3306, user="mohamedashraf", passwd = "",database = "worldgeo_ashraf")
    # debugging
    if debug:
        print("SUCCESS")
    return 

#creating connection with database
init_db()


########################################################
@app.route('/')
def home():
    """ Function used to gather all the endpoints together """
    return render_template("home.html")
###########################################################
@app.route('/addUser', methods = ["POST","GET"])
def addUser():
    

    """ Function used to register a user to the database """
    msg =''
    if request.method == 'POST' and 'Username' in request.form and 'Birthdate' in request.form and 'email' in request.form \
        and 'Gender' in request.form:
        # taking user input from form in html
        username,birthdate,email,gender,age = "","","","","" 
        username = request.form['Username']
        birthdate = request.form["Birthdate"]
        email = request.form['email']
        gender = request.form['Gender']
        
        # get age from birthdate
        today = date.today()
        born = datetime.datetime.strptime(birthdate, "%Y-%m-%d")
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        
        # debugging
        if debug:
            print(username, birthdate, email, gender, age)
        cursor = mydb.cursor()        
        #if the user already exists
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return render_template('addUser.html', msg = "", status= "Failed! Invalid email address !")
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
            return render_template('addUser.html', msg = "",status="Failed Username must contain only characters and numbers !")
        elif not username or not birthdate or not email  or not gender :
            return render_template('addUser.html', msg = "",status= "Failed! Missing field!, Please fill out the form again!")
        else:
            insertQuery = 'INSERT INTO User VALUES (%s, %s, %s, %s, %s)'
            try:
                cursor.execute(insertQuery, (username, birthdate,email, gender, age, ))
                
                msg = 'You have successfully registered !'
                
                # get the user details and display it on screen to make sure that user registered
                cursor.execute("SELECT * FROM User WHERE Username = %s",(username,))
                
                userdata = [i for i in cursor.fetchone()]
                
                mydb.commit()
                cursor.close()
                if debug:
                    print(msg)
                return render_template('redirect.html', userdata=userdata ,review=0)
            except MySQLdb.OperationalError as e:
                # User already in database
                
                exceptionMsg = e.args[1]
                

                if "Lost connection to MySQL server during query" in exceptionMsg:
                    init_db()
                    addUser()
            except MySQLdb.IntegrityError as e:
                #print(exceptionMsg)
                exceptionMsg = e.args[1]    
                if "Duplicate entry" in exceptionMsg:
                    msg = "User already exist!, Please fill out the form again !"
                    if debug:
                        print(msg)
                return render_template('addUser.html', msg = "", status= "Failed! User already exist!, Please fill out the form again !")
    elif request.method == 'POST':
         return render_template('addUser.html', msg = "",status="Please Fill the form")
        
    return render_template('addUser.html', msg = "")
#######################################################################
@app.route('/CountryByCity', methods= ["GET","POST"])
def getCountrybyCity():
    
    """ Function to get the Country Information from a given City"""
    
    #make connection with DB
    #default
    msg = ""
    caps = []
    if request.method == "GET":
        city = request.args.get('City')     
        cursor = mydb.cursor()
        
        select_query = "SELECT CountryName FROM Capital WHERE Name = %s"
        try:
            cursor.execute('SELECT Name FROM Capital')
            allCapitals = cursor.fetchall()
            caps = [i[0] for i in allCapitals]
            
            
            cursor.execute(select_query, (city,))
            result = cursor.fetchall()[0][0]

            mydb.commit()
            cursor.close()

            return render_template('CountryByCity.html',msg=str(result),status="Success",caps= caps,form = request.form)
        except MySQLdb.OperationalError as e:
            exceptionMsg = e.args[1]
            if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getCountrybyCity()
            return render_template('CountryByCity.html',msg="Invalid",status="Invalid City Name,Please Re-enter the city",form = request.form)
        except IndexError as e:
            pass
    return render_template('CountryByCity.html',msg = "",caps= caps)
        
        # col_names = [i[0] for i in cursor.description]
        
####################################################################
@app.route('/DrivingSide', methods = ["POST","GET"])
def drivingside():
    
    """ Function to retrieve left driving side VS right driving side """

    cursor = mydb.cursor()
    select_Left_D_query = "SELECT Name FROM Country WHERE drivingSide = 'Left'"
    select_Right_D_query = "SELECT Name FROM Country WHERE drivingSide = 'Right'"
    try:
        #getting countries with left driving side
        cursor.execute(select_Left_D_query)
        LeftDrivingSide = cursor.fetchall()
        lds = [i[0] for i in LeftDrivingSide]

        # getting countreis with right driving side
        cursor.execute(select_Right_D_query)
        RighDrivingSide = cursor.fetchall()
        rds = [i[0] for i in RighDrivingSide]

        mydb.commit()
        cursor.close()
        return render_template('drivingSide.html',status="Success",Ldata= lds,Rdata = rds)
    except MySQLdb.OperationalError as e:
        exceptionMsg = e.args[1]
        if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                drivingside()
    return render_template('drivingSide.html',status="Failure",form = request.form)

##########################################################
@app.route('/CountriesByLegislature', methods = ["POST","GET"])
def getCountriesByLegislature():
    
    """ Funtion to retrieve all countries of a given Legislature"""
    
    cursor= mydb.cursor()
    countries = []
    legisTypes= []
    legislature = request.args.get("Legislature")    
    try:
        ## get all distinct legislature
        cursor.execute("SELECT DISTINCT Legislature FROM Country")
        
        ## getting all legislatures
        legisTypes = [i[0] for i in cursor.fetchall() if i[0] != ""]
        #print(legisTypes)
        
        ## getting countries by legislature
        cursor.execute("SELECT Name FROM Country WHERE Legislature = %s",(legislature,))
        countries = [i[0] for i in cursor.fetchall()]
        if not countries:
            raise ValueError
        
        #print(countries)
        mydb.commit()
        cursor.close()
        return render_template('Legislature.html', status = "Success", data=countries, legisData=legisTypes)
    except MySQLdb.OperationalError as e:    
        exceptionMsg = e.args[1]
        if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getCountriesByLegislature()
    except ValueError as e:
        return render_template('Legislature.html',status = "Please Enter a legislature",data=[], legisData=legisTypes)
    
    return render_template('Legislature.html',status = "Failure",data=countries, legisData=legisTypes)
        
###########################################################
@app.route('/CountryInfo', methods = ["POST","GET"])
def getCountryInfo():
    
    
    """ Function to retrieve all the Country information  based on a country user input"""
    
    countries = []
    country = request.args.get("Country")
    CountryInfo =[]
    colNames=[]
    try:
        cursor = mydb.cursor()

        # get all countries
        cursor.execute("SELECT Name FROM Country")
        countries = [i[0] for i in cursor.fetchall()]

        
        #get all data for given country
        cursor.execute("SELECT * FROM Country WHERE Name = %s", (country,))
        
        if country is None:
            raise ValueError

        #country info
        CountryInfo = [i for i in cursor.fetchone()]
        # col names
        colNames = [i[0] for i in cursor.description]
        
        mydb.commit()
        cursor.close()
        return render_template("country.html", status="Success", CountryData = CountryInfo, CountriesData = countries, colData = colNames)        
    except MySQLdb.OperationalError as e:    
        exceptionMsg = e.args[1]
        if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getCountryInfo()
    except ValueError as e:
        return render_template("country.html", status="Please Enter a country",CountryData = [], CountriesData = countries, colData = [])
    except TypeError as e:
        return render_template("country.html", status="Invalid Country Name, Please Re-enter the Country Name",CountryData = [], CountriesData = [], colData = [])
    return render_template('country.html',status = "Please Enter a country",CountryData = [],CountriesData=countries, colData=[])
###############################################################        
@app.route('/CapitalInfo', methods = ["POST","GET"])
def getCapitalInfo():
    
    """ Function to retrieve all the Capital information  based on a Capital user input"""
    
    capitals = []
    capital = request.args.get("Capital")
    CapitalInfo =[]
    colNames=[]
    try:
        cursor = mydb.cursor()

        # get all countries
        cursor.execute("SELECT Name FROM Capital")
        capitals = [i[0] for i in cursor.fetchall()]

        
        #get all data for given country
        cursor.execute("SELECT * FROM Capital WHERE Name = %s", (capital,))
        
        if capital is None:
            raise ValueError

        #country info
        CapitalInfo = [i for i in cursor.fetchone()]
        # col names
        colNames = [i[0] for i in cursor.description]
        
        mydb.commit()
        cursor.close()
        return render_template("capital.html", status="Success", CapitalData = CapitalInfo, CapitalsData = capitals, colData = colNames)        
    except MySQLdb.OperationalError as e:    
        exceptionMsg = e.args[1]
        if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getCapitalInfo()
    except ValueError as e:
        return render_template("capital.html", status="Please Enter a Capital",CapitalData = [], CapitalsData = capitals, colData = [])
    except TypeError as e:
        return render_template("capital.html", status="Invalid Country Name, Please Re-enter the Capital Name",CapitalData = [], CapitalsData = [], colData = [])
    return render_template('capital.html',status = "Please Enter a Capital",CapitalData = [],CapitalsData=capitals, colData=[])
###############################################################        
@app.route('/PresidentInfo', methods = ["POST","GET"])
def getPresidentInfo():
    
    """ Function to retrieve president information  based on a president user input"""
    
    Presidents = []
    president = request.args.get("President")
    presidentInfo =[]
    colNames=[]
    try:
        cursor = mydb.cursor()

        # get all countries
        cursor.execute("SELECT Name FROM President")
        Presidents = [i[0] for i in cursor.fetchall()]

        
        #get all data for given country
        cursor.execute("SELECT * FROM President WHERE Name = %s", (president,))
        
        if president is None:
            raise ValueError

        #country info
        presidentInfo = [i for i in cursor.fetchone()]
        # col names
        colNames = [i[0] for i in cursor.description]
        
        mydb.commit()
        cursor.close()
        return render_template("president.html", status="Success", PresidentData = presidentInfo, PresidentsData = Presidents, colData = colNames)        
    except MySQLdb.OperationalError as e:    
        exceptionMsg = e.args[1]
        if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getCapitalInfo()
    except ValueError as e:
        return render_template("president.html", status="Please Enter the name of the President/Monarch",PresidentData = [], PresidentsData = Presidents, colData = [])
    except TypeError as e:
        return render_template("president.html", status="Invalid  President/Monarch Name, Please Re-enter President/Monarch Name",PresidentData = [], PresidentsData = [], colData = [])
    return render_template('president.html',status = "Please Enter a  President/Monarch",PresidentData = [],PresidentsData=Presidents, colData=[])
###############################################################        
@app.route('/CountryReviews', methods = ["POST","GET"]  )
def getCountryReviews():
        
    """ Function to retrieve all reviews of a given country """
    
    countries = []
    country = request.args.get("Country")
    CountryReviews =[]
    colNames=[]
    try:
        cursor = mydb.cursor()

        # get all countries
        cursor.execute("SELECT DISTINCT CountryName FROM CountryUser")
        countries = [i[0] for i in cursor.fetchall()]

        
        #get all data for given country
        cursor.execute("SELECT Username,textualReview,Rates FROM CountryUser WHERE CountryName = %s", (country,))
        
        if country is None:
            raise ValueError

        #country info
        CountryReviews = [i for i in cursor.fetchall()]
        #print(CountryReviews)

        
        mydb.commit()
        cursor.close()
        return render_template("countryReviews.html", status="Success", CountryData = CountryReviews, CountriesData = countries, colData = colNames)        
    except MySQLdb.OperationalError as e:    
        exceptionMsg = e.args[1]
        if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getCountryInfo()
    except ValueError as e:
        return render_template("countryReviews.html", status="Please Enter a country",CountryData = [], CountriesData = countries, colData = [])
    except TypeError as e:
        return render_template("countryReviews.html", status="Invalid Country Name, Please Re-enter the Country Name",CountryData = [], CountriesData = [], colData = [])
    return render_template('countryReviews.html',status = "Please Enter a country",CountryData = [],CountriesData=countries, colData=[])
###############################################################        
@app.route('/identifyCountryByNum', methods= ["GET","POST"])
def getCountryByPhoneNumber():
    
    """ Function to identiy the country by a given phone number """
    
    ## parsing the phone number
    pn = ""
    cc= ""
    Country = ""
    try:
        phoneNumber = request.args.get("PhoneNumber")
    
        #no phone number entered
        if not phoneNumber:
            raise ValueError
        
        pn = phonenumbers.parse(f'+{phoneNumber}')
        cc = pn.country_code   
        print(cc)
        #cc = f"+{cc}"     
    except ValueError as e:
        render_template("phonenum.html", status="Failed, Invalid Phone Number, Enter Phone Number")
    except phonenumbers.phonenumberutil.NumberParseException as e:
        render_template("phonenum.html", status="Failed, Invalid Phone Number, Enter Phone Number")
    try:
        cursor = mydb.cursor()
        cursor.execute("SELECT Name From Country WHERE CallingCode LIKE %s", (cc,))
        

        Country = [i for i in cursor.fetchone()]
        
        mydb.commit()
        cursor.close()
        return render_template("phonenum.html", status="Success", country = str(Country[0]))  
    except MySQLdb.OperationalError as e:    
        exceptionMsg = e.args[1]
        if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getCountryByPhoneNumber()
    except TypeError as e:
            return render_template("phonenum.html")#, status="Failed, Invalid Phone Number, Enter Phone Number")
    return render_template("phonenum.html", status="Enter Phone Number")
#################################################################
@app.route('/CovidStats')
def getCovidStats():
    """ Function to retrieve top 5 and bottom 5 countries in covid cases for each continent"""
    
    continents = []
    continent = request.args.get("Continent")


    try:
        cursor = mydb.cursor()
        
        ## get all the continents for the drop down list
        cursor.execute("SELECT DISTINCT Continent FROM Country")
        continents = [i[0] for i in cursor.fetchall()]
        
        if not continent:
            return render_template("covid.html",continents = continents)
        
        cursor.execute("SELECT Name,TotalCovidCases FROM Country WHERE Continent = %s ORDER BY TotalCovidCases DESC LIMIT 5",(continent,))
        
        top5CovidCases = [i for i in cursor.fetchall()]
        
        cursor.execute("SELECT Name,TotalCovidCases FROM Country WHERE Continent = %s AND TotalCovidCases != 0 ORDER BY TotalCovidCases ASC LIMIT 5",(continent,))
        
        bottom5CovidCases =   [i for i in cursor.fetchall()]
        
        mydb.commit()
        cursor.close()
        
        return render_template("covid.html",status="Success",continents=continents,top5CovidCases= top5CovidCases,bottom5CovidCases=bottom5CovidCases)#, status="Failed, Invalid Phone Number, Enter Phone Number")
        
    except MySQLdb.OperationalError as e:    
        exceptionMsg = e.args[1]
        if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getCovidStats()
    except TypeError as e:
            return render_template("covid.html",status="Failed")#, status="Failed, Invalid Phone Number, Enter Phone Number")
        
    return render_template("covid.html")#, status="Failed, Invalid Phone Number, Enter Phone Number")
    
        
    
#################################################################
@app.route('/CovidVaccinesStats')
def getCovidVaccinesStats():
    
    """ Function to retrieve top 5 and bottom 5 countries in covid vaccinations for each continent"""
    
    continents = []
    continent = request.args.get("Continent")


    try:
        cursor = mydb.cursor()
        
        ## get all the continents for the drop down list
        cursor.execute("SELECT DISTINCT Continent FROM Country")
        continents = [i[0] for i in cursor.fetchall()]
        
        if not continent:
            return render_template("covidVaccines.html",continents = continents)
        
        cursor.execute("SELECT Name,TotalCovidVaccinations FROM Country WHERE Continent = %s ORDER BY TotalCovidVaccinations DESC LIMIT 5",(continent,))
        
        top5CovidVaccinations = [i for i in cursor.fetchall()]
        
        cursor.execute("SELECT Name,TotalCovidVaccinations FROM Country WHERE Continent = %s AND TotalCovidVaccinations != 0 ORDER BY TotalCovidVaccinations ASC LIMIT 5",(continent,))
        
        bottom5CovidVaccinations =   [i for i in cursor.fetchall()]
        
        mydb.commit()
        cursor.close()
        
        return render_template("covidVaccines.html",status="Success",continents=continents,top5CovidVaccinations= top5CovidVaccinations,bottom5CovidVaccinations=bottom5CovidVaccinations)#, status="Failed, Invalid Phone Number, Enter Phone Number")
        
    except MySQLdb.OperationalError as e:    
        exceptionMsg = e.args[1]
        if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getCovidVaccinesStats()
    except TypeError as e:
            return render_template("covidVaccines.html",status="Failed")#, status="Failed, Invalid Phone Number, Enter Phone Number")
        
    return render_template("covidVaccines.html")#, status="Failed, Invalid Phone Number, Enter Phone Number")
    
        
    
    

#####################################################################
@app.route('/StatsGlobal')
def getStatsGlobal():
    
    """ Function to retrieve top 10 countries globally in GDPNominal , GDPPurchasePower, Population, Area, Density, GDPPerCapita"""
    try: 
        cursor =mydb.cursor()
        

        #get top 10 countries by GDPNominal
        cursor.execute("SELECT Name,GDPNominal FROM Country ORDER BY GDPNominal DESC LIMIT 10")
        GDPNominal = [i for i in cursor.fetchall()]
        
        
        #get top 10 countries by GDPPurchase
        cursor.execute("SELECT Name,GDPPurchasePower FROM Country ORDER BY GDPPurchasePower DESC LIMIT 10")
        GDPPurchasePower = [i for i in cursor.fetchall()]
        
          #get top 10 countries by Population
        cursor.execute("SELECT Name,Population FROM Country ORDER BY Population DESC LIMIT 10")
        Population = [i for i in cursor.fetchall()]
        
        
          #get top 10 countries by Area
        cursor.execute("SELECT Name,area FROM Country ORDER BY area DESC LIMIT 10")
        area = [i for i in cursor.fetchall()]
       
        
        #get top 10 countries by Density
        cursor.execute("SELECT Name, (Population / area) AS Density FROM Country ORDER BY Density DESC LIMIT 10")
        Density = [i for i in cursor.fetchall()]
        
        
        #get top 10 countries by GDPNominal Per Capita
        cursor.execute("SELECT Name, (GDPNominal / Population) AS GDPNominalPerCapita FROM Country ORDER BY GDPNominalPerCapita DESC LIMIT 10")
        GDPNominalPerCapita = [i for i in cursor.fetchall()]
        
        
        #get top 10 countries by Density
        cursor.execute("SELECT Name, (GDPPurchasePower / Population) AS GDPPurchasePowerPerCapita FROM Country ORDER BY GDPPurchasePowerPerCapita DESC LIMIT 10")
        GDPPurchasePowerPerCapita = [i for i in cursor.fetchall()]
        
        mydb.commit()
        cursor.close()
        
        return render_template("StatsGlobal.html",GDPNominal=GDPNominal,GDPPurchasePower=GDPPurchasePower,Population=Population ,\
            area=area,Density=Density, GDPNominalPerCapita=GDPNominalPerCapita, \
            GDPPurchasePowerPerCapita=GDPPurchasePowerPerCapita)
        
    except MySQLdb.OperationalError as e:    
        exceptionMsg = e.args[1]
        if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getStatsGlobal()
    
#############################################################
@app.route('/StatsPerContinent')
def getStatsPerContinent():
    """ Function to retrieve top 10 countries continent in GDPNominal , GDPPurchasePower, Population, Area, Density, GDPPerCapita"""
    continents = []
    continent = request.args.get("Continent")
    try: 
        cursor =mydb.cursor()
        
        ## get all the continents for the drop down list
        cursor.execute("SELECT DISTINCT Continent FROM Country")
        continents = [i[0] for i in cursor.fetchall()]
        
        if not continent:
            return render_template("StatsByContinent.html",continents = continents)

        #get top 10 countries by GDPNominal
        cursor.execute("SELECT Name,GDPNominal FROM Country WHERE Continent = %s ORDER BY GDPNominal DESC LIMIT 10",(continent,))
        GDPNominal = [i for i in cursor.fetchall()]
        
        
        #get top 10 countries by GDPPurchase
        cursor.execute("SELECT Name,GDPPurchasePower FROM Country  WHERE Continent = %s ORDER BY GDPPurchasePower DESC LIMIT 10",(continent,))
        GDPPurchasePower = [i for i in cursor.fetchall()]
        
          #get top 10 countries by Population
        cursor.execute("SELECT Name,Population FROM Country   WHERE Continent = %s ORDER BY Population DESC LIMIT 10",(continent,))
        Population = [i for i in cursor.fetchall()]
        
        
          #get top 10 countries by Area
        cursor.execute("SELECT Name,area FROM Country  WHERE Continent = %s ORDER BY area DESC LIMIT 10",(continent,))
        area = [i for i in cursor.fetchall()]
       
        
        #get top 10 countries by Density
        cursor.execute("SELECT Name, (Population / area) AS Density FROM Country  WHERE Continent = %s ORDER BY Density DESC LIMIT 10",(continent,))
        Density = [i for i in cursor.fetchall()]
        
        
        #get top 10 countries by GDPNominal Per Capita
        cursor.execute("SELECT Name, (GDPNominal / Population) AS GDPNominalPerCapita FROM Country  WHERE Continent = %s ORDER BY GDPNominalPerCapita DESC LIMIT 10",(continent,))
        GDPNominalPerCapita = [i for i in cursor.fetchall()]
        
        
        #get top 10 countries by GDPPurchasePowerPerCapita
        cursor.execute("SELECT Name, (GDPPurchasePower / Population) AS GDPPurchasePowerPerCapita FROM Country  WHERE Continent = %s ORDER BY GDPPurchasePowerPerCapita DESC LIMIT 10",(continent,))
        GDPPurchasePowerPerCapita = [i for i in cursor.fetchall()]
        mydb.commit()
        cursor.close()
        
        
        return render_template("StatsByContinent.html",status="Success",continents = continents,GDPNominal=GDPNominal,GDPPurchasePower=GDPPurchasePower,Population=Population ,\
            area=area,Density=Density, GDPNominalPerCapita=GDPNominalPerCapita, \
            GDPPurchasePowerPerCapita=GDPPurchasePowerPerCapita)
        
    except MySQLdb.OperationalError as e:    
        exceptionMsg = e.args[1]
        if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getStatsGlobal()
        

###############################################
@app.route('/addNewUserReview',methods=["POST","GET"])
def getNewUserReview():
    """Function to add a new user review """
    if request.method =="POST":
        Username= request.form['Username']
        CountryName = request.form["CountryName"]
        Rates = request.form["Rates"]
        travelDate = request.form["travelDate"]
        textualReview =request.form["textualReview"]
        try:
            cursor = mydb.cursor()
            
            msg = 'You have successfully registered !'
            
            # get the user details and display it on screen to make sure that user registered
            cursor.execute("INSERT INTO CountryUser VALUES (%s,%s,%s,%s,%s)",(Username, CountryName, Rates, travelDate, textualReview))
            
            cursor.execute("SELECT * FROM CountryUser WHERE Username = %s AND CountryName = %s",(Username,CountryName))
            userdata = [i for i in cursor.fetchone()]
            print(userdata)
            
            mydb.commit()
            cursor.close()
            if debug:
                print(msg)
            
            return render_template('redirect.html', userdata=userdata ,review=1 )
        except MySQLdb.OperationalError as e:
            # User already in database
            
            exceptionMsg = e.args[1]
            if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                getNewUserReview()
        except MySQLdb.IntegrityError as e:
            print(e)
            #print(exceptionMsg)
            exceptionMsg = e.args[1]    
            if "Duplicate entry" in exceptionMsg:
          
                if debug:
                    print(msg)
    
            return render_template('UserReview.html',status="Failed, Duplicate Entry")
    return render_template('UserReview.html',status = "Please Fill the form")
##################################################
@app.route('/UpdateCountryReview',methods=["POST","GET"])
def UpdateUserReview():
    """Function to update user review on a country"""
    if request.method =="POST":
        Username= request.form['Username']
        CountryName = request.form["CountryName"]
        Rates = request.form["Rates"]
        textualReview =request.form["textualReview"]
        try:
            cursor = mydb.cursor()
            
            
            cursor.execute("SELECT * FROM CountryUser WHERE Username = %s AND CountryName = %s",(Username,CountryName,))
            userdata = [i for i in cursor.fetchone()]
            if not userdata:
                raise TypeError
  
            # else
            #cursor.execute("UPDATE CountryUser SET Rates = %s AND textualReview = %s WHERE Username =%s AND CountryName = %s",(Rates,textualReview,Username,CountryName,))
  

            
            cursor.execute("UPDATE CountryUser SET Rates = %s , textualReview = %s WHERE Username =%s AND CountryName = %s",(Rates,textualReview,Username,CountryName,))
            
            cursor.execute("SELECT Rates,textualReview FROM CountryUser WHERE Username = %s AND CountryName = %s",(Username,CountryName,))
            userdata = [i for i in cursor.fetchone()]
            print(userdata)
            cursor.close()
            mydb.commit()
            return render_template('updatecountryrev.html', status="Review Updated")
        except MySQLdb.OperationalError as e:
            # User already in database
            
            exceptionMsg = e.args[1]
            if "Lost connection to MySQL server during query" in exceptionMsg:
                init_db()
                UpdateUserReview()
        except MySQLdb.IntegrityError as e:
            print(e)
            #print(exceptionMsg)
            exceptionMsg = e.args[1]    
            if "Duplicate entry" in exceptionMsg:
                return render_template('updatecountryrev.html',status="Failed, Duplicate Entry")
                    
        except TypeError as e:
            return render_template('updatecountryrev.html',status="User Didnt visit the country, redirecting to add the new country!", redir=1)
    return render_template('updatecountryrev.html',status = "Please Fill the form")

if __name__ == "__main__":

    app.run(debug=True)
