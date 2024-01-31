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
        app.collection = app.database[config["collection_name"]]

        print("Connected to the MongoDB database!")
    except Exception as e:
        print(f"Unable to connect to the database: {e}")

connect_database()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post('/insert_expense')
async def insert_expense(request: Request):
    try:
        expensess_received = await request.form()
        expenses = {key: value for key, value in expensess_received.items()}
        print(expenses)

        current_date = datetime.now().strftime("%d-%m-%Y")
        Exists = app.collection.find_one({"Date": current_date})

        if(Exists):
            app.collection.update_one({"Date": current_date}, {"$push": {"Expenses": expenses}})
        
        else:
            document = {
                    "Date": current_date,
                    "Expenses": [expenses]}
            app.collection.insert_one(document)

        return ({'message': 'Added Sucessfully'})
    except Exception as error:
        print(error)
        return ({'message': f'Unsuccessfully -- {error}'})

@app.post("/insert_task", response_model=dict)
async def insert_task(request: Request):
    try:
        tasks_received = await request.form()
        tasks_dict = {key: value for key, value in tasks_received.items()}
        print(tasks_dict)

        current_date = datetime.now().strftime("%d-%m-%Y")
        existing_document = app.collection.find_one({"Date": current_date})

        if existing_document:
            # Update existing document by adding new tasks
            app.collection.update_one({"Date": current_date}, {"$set": {"Tasks": tasks_dict}})
        else:
            # Insert a new document with the specified date and tasks
            document = {
                "Date": current_date,
                "Tasks": tasks_dict
            }
            app.collection.insert_one(document)

        return {'star_count': len(tasks_dict)}
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500, detail=f"Unsuccessfully -- {error}")


