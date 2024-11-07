import requests
import unittest
from unittest.mock import patch
import json
import os

class ExpensesTask:
    def __init__(self):
        self.expenses = []

    def load_expenses(self, url):
        response = requests.get(url + "/expenses")
        if response.status_code == 200:
            self.expenses = response.json().get('expenses', [])

    def add_expense(self, url, expense):
        response = requests.post(url + "/expenses", json=expense)
        if response.status_code == 201:
            self.expenses.append(response.json())

    def view_expenses(self):
        return self.expenses

    def update_expense(self, url, expense_id, updated_expense):
        response = requests.put(f"{url}/expenses/{expense_id}", json=updated_expense)
        if response.status_code == 200:
            for expense in self.expenses:
                if expense['id'] == expense_id:
                    expense.update(updated_expense)
                    break

    def delete_expense(self, url, expense_id):
        response = requests.delete(f"{url}/expenses/{expense_id}")
        if response.status_code == 204:
            self.expenses = [expense for expense in self.expenses if expense['id'] != expense_id]

URL = "http://127.0.0.1:5000"

def main():
    my_expenses = ExpensesTask()
    my_expenses.load_expenses(URL)
    while True:
        print("\nExpenses Menu:")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Update Expense")
        print("4. Delete Expense")
        print("5. Exit")
        choice = int(input("\nEnter option: "))
        while choice not in [1, 2, 3, 4, 5]:
            print("\n// Error! Invalid option. Please try again //")
            choice = int(input("\nEnter option: "))

        if choice == 1:
            add_expense(my_expenses)
        elif choice == 2:
            view_expense(my_expenses)
            input("Press enter to continue")
            screen_refresh()
        elif choice == 3:
            update_expense(my_expenses)
        elif choice == 4:
            delete_expense(my_expenses)
        elif choice == 5:
            break

def screen_refresh():
    os.system("cls" if os.name == "nt" else "clear")

def add_expense(my_expenses):
    description = ""
    while not description:
        description = input("\nEnter expense description: ").title()
        if description == "":
            print("// Error! Invalid description. Please try again //")

    amount = float(input("Enter expense amount: "))
    date = input("Enter expense date (YYYY-MM-DD): ")
    expense = {"description": description, "amount": amount, "date": date}
    my_expenses.add_expense(URL, expense)
    print("\n// Expense added successfully //")
    screen_refresh()

# Viewing all expences
def view_expense(my_expenses):
    expenses = my_expenses.view_expenses()
    if not expenses:
        print("// No expenses available //")
    else:
        for idx, expense in enumerate(expenses, start=1):
            print(f"{idx}. {expense['description']} - ${expense['amount']} on {expense['date']}")

# Updating a expence
def update_expense(my_expenses):
    view_expense(my_expenses)
    try:
        expense_id = int(input("\nEnter the expense number to update: ")) - 1
        while expense_id not in range(len(my_expenses)):
            print("\n// Error! Invalid expense number //")
            expense_id = int(input("\nEnter the expense number to update: ")) - 1

        if expense_id < 0 or expense_id >= len(my_expenses):
            raise IndexError
        description = input("Edit description: ")
        amount = float(input("Edit amount: "))
        date = input("Edit date (YYYY-MM-DD): ")
        if description:
            updated_expense = {"description": description, "amount": amount, "date": date}
        else:
            updated_expense = {"amount": amount, "date": date}
        my_expenses.update_expense(URL, expense_id, updated_expense)
        print("\n// Expenses updated successfully //")
        screen_refresh()
    except (ValueError, IndexError):
        input("\n// Error! Invalid expense number //")
        screen_refresh()

# Deleting an expence
def delete_expense(my_expenses):
    view_expense(my_expenses)
    try:
        expense_id = int(input("\nEnter the expense number to update: ")) - 1
        while expense_id not in range(len(my_expenses)):
            print("\n// Error! Invalid expense number //")
            expense_id = int(input("\nEnter the expense number to update: ")) - 1

        if expense_id < 0 or expense_id >= len(my_expenses):
            raise IndexError
        my_expenses.delete_expense(URL, expense_id)
        print("\n// Expenses deleted successfully //")
        screen_refresh()
    except (ValueError, IndexError):
        input("\n// Error! Invalid expense number //")
        screen_refresh()

if __name__ == "__main__":
    main()

class TestExpensesTask(unittest.TestCase):
    @patch('requests.get')
    def test_load_expenses(self, mock_get):
        mock_response = {
            "expenses": [
                {"description": "Lunch", "amount": 12.95, "date": "2024-11-02"},
                {"description": "Dinner", "amount": 35.99, "date": "2024-11-02"}
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        task = ExpensesTask()
        task.load_expenses(URL)

        self.assertEqual(len(task.expenses), 2)
        self.assertEqual(task.expenses[0]["description"], "Lunch")
        self.assertEqual(task.expenses[1]["description"], "Dinner")

    @patch('requests.post')
    def test_add_expense(self, mock_post):
        new_expense = {"description": "Snacks", "amount": 7.5, "date": "2024-11-02"}
        mock_response = new_expense.copy()
        mock_response["id"] = 1

        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = mock_response

        task = ExpensesTask()
        task.add_expense(URL, new_expense)

        self.assertEqual(len(task.expenses), 1)
        self.assertEqual(task.expenses[0]["description"], "Snacks")

    @patch('requests.put')
    def test_update_expense(self, mock_put):
        updated_expense = {"description": "Brunch", "amount": 15.0, "date": "2024-11-02"}
        mock_response = updated_expense.copy()
        mock_response["id"] = 1

        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = mock_response

        task = ExpensesTask()
        task.expenses = [{"id": 1, "description": "Breakfast", "amount": 12.5, "date": "2023-11-02"}]
        task.update_expense(URL, 1, updated_expense)

        self.assertEqual(task.expenses[0]["description"], "Brunch")

    @patch('requests.delete')
    def test_delete_expense(self, mock_delete):
        mock_delete.return_value.status_code = 204

        task = ExpensesTask()
        task.expenses = [{"id": 1, "description": "Lunch", "amount": 12.95, "date": "2024-11-02"}]
        task.delete_expense(URL, 1)

        self.assertEqual(len(task.expenses), 0)

if __name__ == "__main__":
    unittest.main()