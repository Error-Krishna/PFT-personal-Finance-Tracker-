from flask import Flask, request, jsonify
from flask_cors import CORS  # Enable CORS for frontend access
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId  # Convert ObjectId to string in responses

app = Flask(__name__)
CORS(app)  # Enable CORS - bakcend can share info with frontend and vice versa

# MongoDB configuration
client = MongoClient("mongodb+srv://iamkrishnagoyal:Krishnamongo@pft.logiw.mongodb.net/?retryWrites=true&w=majority&appName=PFT")
db = client["finance_tracker"]
expenses = db["expenses"]
incomes = db["incomes"]
saving_goals = db["saving_goals"]

# Helper function to calculate total
def calculate_total(collection):
    return sum(item.get('amount', 0) for item in collection.find()) # Sum all amounts in collection default is 0

# Convert MongoDB ObjectId to string
def serialize_document(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

# Route to add an expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    try:
        data = request.json
        print("Received Expense Data:", data)

        expense = {
            "category": data['category'],
            "amount": data['amount'],
            "date": datetime.strptime(data['date'], "%Y-%m-%d"),
            "description": data.get('description', "")
        }

        result = expenses.insert_one(expense)
        print("Inserted Expense ID:", result.inserted_id)

        return jsonify({"message": "Expense added successfully", "id": str(result.inserted_id)}), 201
    except Exception as e:
        print("Error in add_expense:", e)
        return jsonify({"error": str(e)}), 500

# Route to add an income
@app.route('/add_income', methods=['POST'])
def add_income():
    try:
        data = request.json
        income = {
            "source": data['source'],
            "amount": data['amount'],
            "date": datetime.strptime(data['date'], "%Y-%m-%d")
        }
        result = incomes.insert_one(income)
        return jsonify({"message": "Income added successfully", "id": str(result.inserted_id)}), 201
    except Exception as e:
        print("Error in add_income:", e)
        return jsonify({"error": str(e)}), 500

# Route to get spending trends
@app.route('/spending_trends', methods=['GET'])
def spending_trends():
    try:
        pipeline = [{"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}]
        trends = list(expenses.aggregate(pipeline))
        return jsonify({"trends": trends}), 200
    except Exception as e:
        print("Error in spending_trends:", e)
        return jsonify({"error": str(e)}), 500

# Route to calculate budget status
@app.route('/budget_status', methods=['GET'])
def budget_status():
    try:
        total_expenses = calculate_total(expenses)
        total_income = calculate_total(incomes)
        budget = total_income - total_expenses
        return jsonify({
            "total_income": total_income,
            "total_expenses": total_expenses,
            "remaining_budget": budget
        }), 200
    except Exception as e:
        print("Error in budget_status:", e)
        return jsonify({"error": str(e)}), 500

# Route to set and check saving goals
@app.route('/saving_goals', methods=['POST', 'GET'])
def saving_goals_route():
    try:
        if request.method == 'POST':
            data = request.json
            saving_goals.update_one(
                {"goal_name": data['goal_name']},
                {"$set": {
                    "goal_name": data['goal_name'],
                    "target_amount": data['target_amount'],
                    "saved_amount": data['saved_amount']
                }},
                upsert=True
            )
            return jsonify({"message": "Saving goal added/updated successfully"}), 201
        else:  # GET request
            goals = [serialize_document(goal) for goal in saving_goals.find({}, {"_id": 1, "goal_name": 1, "target_amount": 1, "saved_amount": 1})]
            return jsonify({"goals": goals}), 200
    except Exception as e:
        print("Error in saving_goals:", e)
        return jsonify({"error": str(e)}), 500

# Test database connection
@app.route('/test_db', methods=['GET'])
def test_db():
    try:
        test_expense = expenses.find_one()
        if test_expense:
            return jsonify({"message": "Database connected successfully", "test_expense": serialize_document(test_expense)}), 200
        else:
            return jsonify({"message": "Database connected successfully, but no data found"}), 200
    except Exception as e:
        print("Error in test_db:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)