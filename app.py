from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage for expenses
expenses = []

@app.route('/expenses', methods=['GET'])
def get_expenses():
    """Retrieve the list of expenses."""
    return jsonify({'expenses': expenses})

@app.route('/expenses', methods=['POST'])
def add_expense():
    """Add a new expense."""
    expense = request.json
    expense['id'] = len(expenses) + 1  # Simple ID assignment
    expenses.append(expense)
    return jsonify(expense), 201

@app.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update an existing expense."""
    expense = next((exp for exp in expenses if exp['id'] == expense_id), None)
    if expense:
        expense.update(request.json)
        return jsonify(expense)
    return jsonify({'error': 'Expense not found'}), 404

@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense."""
    global expenses
    expenses = [exp for exp in expenses if exp['id'] != expense_id]
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)