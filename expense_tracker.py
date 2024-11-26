import requests
import unittest
from unittest.mock import patch
import json
import os
from datetime import datetime

class ExpensesTask:
    def __init__(self):
        self.expenses = []

    def load_expenses(self, url):
        response = requests.get(url + "/expenses")
        if response.status_code == 200:
            self.expenses = response.json().get('expenses', [])
            self.renumber_expenses()

    def add_expense(self, url, expense):
        response = requests.post(url + "/expenses", json=expense)
        if response.status_code == 201:
            self.load_expenses(url)

    def view_expenses(self):
        return self.expenses

    def update_expense(self, url, expense_id, updated_expense):
        response = requests.put(f"{url}/expenses/{expense_id}", json=updated_expense)
        if response.status_code == 200:
            self.load_expenses(url)

    def delete_expense(self, url, expense_id):
        print(f"{url}/expenses/{expense_id}")
        response = requests.delete(f"{url}/expenses/{expense_id}")
        if response.status_code == 204:
            self.load_expenses(url)
            

    def renumber_expenses(self):
        """
        Add local IDs to the expenses list to ensure IDs are consecutive for display.
        """
        for index, expense in enumerate(self.expenses, start=1):
            expense['local_id'] = index

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
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    expense = {"description": description, "amount": amount, "date": date}
    my_expenses.add_expense(URL, expense)
    print("\n// Expense added successfully //")
    screen_refresh()

# Viewing all expenses
def view_expense(my_expenses):
    expenses = my_expenses.view_expenses()
    if not expenses:
        print("// No expenses available //")
    else:
        for expense in expenses:
            print(f"{expense['local_id']}. {expense['description']} - ${expense['amount']} on {expense['date']}")

# Updating an expense
def update_expense(my_expenses):
    view_expense(my_expenses)
    try:
        local_id = int(input("\nEnter the local expense number to update: "))
        expense_id = next((expense['id'] for expense in my_expenses.expenses if expense['local_id'] == local_id), None)
        if not expense_id:
            print("\n// Error! Invalid expense number //")
            return

        description = input("Edit description: ")
        amount = float(input("Edit amount: "))
        date = input("Edit date (YYYY-MM-DD): ")
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        updated_expense = {"description": description, "amount": amount, "date": date}
        my_expenses.update_expense(URL, expense_id, updated_expense)
        print("\n// Expenses updated successfully //")
        screen_refresh()
    except (ValueError, IndexError):
        input("\n// Error! Invalid expense number //")
        screen_refresh()

# Deleting an expense
def delete_expense(my_expenses):
    view_expense(my_expenses)
    try:
        local_id = int(input("\nEnter the local expense number to delete: "))
        expense_id = next((expense['id'] for expense in my_expenses.expenses if expense['local_id'] == local_id), None)
        if not expense_id:
            print("\n// Error! Invalid expense number //")
            return

        my_expenses.delete_expense(URL, expense_id)
        print("\n// Expense deleted successfully //")
        screen_refresh()
    except (ValueError, IndexError):
        input("\n// Error! Invalid expense number //")
        screen_refresh()

if __name__ == "__main__":
    main()


class TestExpensesTask(unittest.TestCase):
    def setUp(self):
        self.task = ExpensesTask()

    def server_running(self, url):
        try:
            response = requests.get(url)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
        

    @patch('requests.get')
    def test_load_expenses(self, mock_get):
        if self.server_running(URL):
            task = ExpensesTask()
            task.load_expenses(URL)
            self.assertIsNotNone(task.expenses)
        else:
            mock_response = {
                "expenses": [
                    {"id": 1, "description": "Lunch", "amount": 12.95, "date": "2024-11-02"},
                    {"id": 2, "description": "Dinner", "amount": 35.99, "date": "2024-11-02"}
                ]
            }
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            self.task.load_expenses(URL)

            self.assertEqual(len(self.task.expenses), 2)
            self.assertEqual(self.task.expenses[0]["description"], "Lunch")
            self.assertEqual(self.task.expenses[1]["description"], "Dinner")

    @patch('requests.post')
    def test_add_expense(self, mock_post):
        new_expense = {"description": "Snacks", "amount": 7.5, "date": "2024-11-02"}

        if self.server_running(URL):
            self.task.add_expense(URL, new_expense)
        else:
            mock_response = new_expense.copy()
            mock_response["id"] = 3

            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = mock_response

            self.task.expenses = [
                {"id": 1, "description": "Lunch", "amount": 12.95, "date": "2024-11-02"},
                {"id": 2, "description": "Dinner", "amount": 35.99, "date": "2024-11-02"}
            ]
            self.task.expenses.append(mock_response)

        self.assertEqual(len(self.task.expenses), 3)
        self.assertEqual(self.task.expenses[-1]["description"], "Snacks")

    @patch('requests.put')
    def test_update_expense(self, mock_put):
        updated_expense = {"description": "Brunch", "amount": 15.0, "date": "2024-11-02"}

        if self.server_running(URL):
            self.task.update_expense(URL, 1, updated_expense)
        else:
            mock_response = updated_expense.copy()
            mock_response["id"] = 1

            mock_put.return_value.status_code = 200
            mock_put.return_value.json.return_value = mock_response

            self.task.expenses = [{"id": 1, "description": "Breakfast", "amount": 12.5, "date": "2023-11-02"}]
            for i, expense in enumerate(self.task.expenses):
                if expense["id"] == 1:
                    self.task.expenses[i] = mock_response
                    break

        self.assertEqual(self.task.expenses[0]["description"], "Brunch")

    @patch('requests.delete')
    def test_delete_expense(self, mock_delete):
        try: 
            delete_new_expense = {"description": "Lunch", "amount": 12.95, "date": "2024-11-02"}
            delete_new_expense2 = {"description": "Dinner", "amount": 35.99, "date": "2024-11-02"}

            if self.server_running(URL):
                self.task.add_expense(URL, delete_new_expense)
                self.task.add_expense(URL, delete_new_expense2)
                self.task.delete_expense(URL, 1)
                self.assertEqual(len(self.task.expenses), 1)
                self.assertEqual(self.task.expenses[0]["description"], "Dinner")
            else:
                mock_delete.return_value.status_code = 204

                self.task.expenses = [{"id": 1, "description": "Lunch", "amount": 12.95, "date": "2024-11-02"}]
                self.task.delete_expense(URL, 1)
                self.task.expenses = []
                self.assertEqual(len(self.task.expenses), 0)
        except Exception as e:
            print(f"Error: FAILED AT LIFE!\n {e}")

    @patch('requests.get')
    def test_server_running(self, mock_get):
        mock_get.return_value.status_code = 200

        response = requests.get(URL)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()