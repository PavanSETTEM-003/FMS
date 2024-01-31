from flask import Flask, render_template, request, jsonify
from datetime import datetime
from pymongo import MongoClient
from dotenv import dotenv_values

config = dotenv_values(".env")
app = Flask(__name__)

def connect_database():
    try:
        app.mongodb_client = MongoClient(config["mongodb_connection_string"])
        app.database = app.mongodb_client[config["DB_NAME"]]
        app.collection = app.database[config["collection_name"]]

        print("Connected to the MongoDB database!")
    except Exception as e:
        print(f"Unable to connect to the database: {e}")


@app.route('/')
def home():
    return render_template('index.html', name='Flask')

@app.route('/insert_expense', methods=['POST'])
def insert_expense():
    try:
        expenses = request.form.to_dict()
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

        return jsonify({'message': 'Added Sucessfully'})
    except Exception as error:
        return jsonify({'message': f'Unsuccessfully -- {error}'})

@app.route("/insert_task", methods = ['POST'])
def insert_task():
    tasks_received = request.form.to_dict()
    print(tasks_received)

    current_date = datetime.now().strftime("%d-%m-%Y")
    existing_document = app.collection.find_one({"Date": current_date})

    if existing_document:
        # Update existing document by adding new tasks
        app.collection.update_one({"Date": current_date}, {"$set": {"Tasks": tasks_received}})

    else:
        # Insert a new document with the specified date and tasks
        document = {
            "Date": current_date,
            "Tasks": tasks_received
        }
        app.collection.insert_one(document)

    return jsonify({'star_count': len(tasks_received)})



if __name__ == '__main__':
    try:
        connect_database()
        app.run(debug=True, port=5000)
    except Exception as error:
        print(error)
        
