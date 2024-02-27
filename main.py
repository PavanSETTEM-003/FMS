from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from pymongo import MongoClient
from dotenv import dotenv_values

config = dotenv_values(".env")
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def connect_database():
    try:
        app.mongodb_client = MongoClient(config["mongodb_connection_string"])
        app.database = app.mongodb_client[config["DB_NAME"]]
        app.Tracker_Collection = app.database[config["Tracker_collection_name"]]
        app.Summary_Collection = app.database[config["Summary_collection_name"]]

        print("Connected to the MongoDB database!")
    except Exception as e:
        print(f"Unable to connect to the database: {e}")

connect_database()

def Update_Expenses_Summary(current_date, expenses):
    try:
        current_year,current_month = str(current_date[6::]),str(current_date[3:5])

        month_expenses = app.Summary_Collection.find_one({"year."+current_year : {"$exists" : True}})

        if(month_expenses == None):
            app.Summary_Collection.update_one(
                { "id": "65dda2f121377b9e345a32c6"},
                { "$set": { "year."+current_year: [] } })
            
            month_expenses = app.Summary_Collection.find_one({"year."+current_year : {"$exists" : True}})

        month_expenses_list = month_expenses["year"][current_year]

        if(len(month_expenses_list) == int(current_month)):
            month_expenses_list[-1] += int(expenses["price"])

        else:
            month_expenses_list.append(int(expenses["price"]))

        app.Summary_Collection.update_one({"year." + current_year: {"$exists": True}},
                      {"$set": {"year." + current_year: month_expenses_list}})

        return int(month_expenses_list[-1])

    except Exception as error:
        print("Func_'Update_Expenses_Summary' :",error)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/fetch_amount")
async def fetch_amount(request: Request):
    try:
        current_year = str(datetime.now().strftime("%d-%m-%Y"))[6::]      
        month_expenses = app.Summary_Collection.find_one({"year."+current_year : {"$exists" : True}})

        if(month_expenses == None):
            return({"amount_this_month":0})
        
        else:
            return ({"amount_this_month":month_expenses["year"][current_year][-1]})

    except Exception as error:
        print(error)
        return ({"amount_this_month":"uanble to fetch"})

@app.post('/insert_expense')
async def insert_expense(request: Request):
    try:
        expensess_received = await request.form()
        expenses = {key: value for key, value in expensess_received.items()}
        # print(expenses)

        current_date = datetime.now().strftime("%d-%m-%Y")
        Date_Exists = app.Tracker_Collection.find_one({"Date": current_date})

        amount_this_month = Update_Expenses_Summary(current_date, expenses)   ## updating the Summary_Collection of the expenses

        if(Date_Exists):
            app.Tracker_Collection.update_one({"Date": current_date}, {"$push": {"Expenses": expenses}})
        
        else:
            document = {
                    "Date": current_date,
                    "Expenses": [expenses]}
            app.Tracker_Collection.insert_one(document)

        return ({'message': 'Added Sucessfully', 'amount_this_month': amount_this_month})
    
    except Exception as error:
        print(error)
        return ({'message': f'Unsuccessfully -- {error}', 'amount_this_month': "Unable to fetch"})

@app.post("/insert_task", response_model=dict)
async def insert_task(request: Request):
    try:
        tasks_received = await request.form()
        tasks_dict = {key: value for key, value in tasks_received.items()}
        print(tasks_dict)

        current_date = datetime.now().strftime("%d-%m-%Y")
        existing_document = app.Tracker_Collection.find_one({"Date": current_date})

        if existing_document:
            # Update existing document by adding new tasks
            app.Tracker_Collection.update_one({"Date": current_date}, {"$set": {"Tasks": tasks_dict}})
        else:
            # Insert a new document with the specified date and tasks
            document = {
                "Date": current_date,
                "Tasks": tasks_dict
            }
            app.Tracker_Collection.insert_one(document)

        return {'star_count': len(tasks_dict)}
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500, detail=f"Unsuccessfully -- {error}")