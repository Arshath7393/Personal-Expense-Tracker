import mysql.connector

import database


def show_expenses(expenses):
    if not expenses:
        print("No expenses found.")
        return

    print("\nID | Name | Amount | Category | Date")
    print("-" * 55)
    for expense in expenses:
        print(
            f"{expense[0]} | {expense[1]} | {expense[2]:.2f} | "
            f"{expense[3]} | {expense[4]}"
        )


def main():
    while True:
        print("\nPersonal Expense Tracker")
        print("1. Add an expense")
        print("2. View all expenses")
        print("3. Search an expense by name")
        print("4. Update an expense")
        print("5. Delete an expense")
        print("6. Exit")

        choice = input("Enter your choice: ")

        try:
            if choice == "1":
                expense_name = input("Expense name: ")
                try:
                    amount = float(input("Amount: "))
                except ValueError:
                    print("Please enter a valid number for the amount.")
                    continue
                category = input("Category: ")
                expense_date = input("Date (YYYY-MM-DD): ")

                expense_id = database.add_expense(
                    expense_name, amount, category, expense_date
                )
                print(f"Expense added with ID {expense_id}.")

            elif choice == "2":
                expenses = database.get_all_expenses()
                show_expenses(expenses)
                print(f"Total amount spent: {database.get_total_spent():.2f}")

            elif choice == "3":
                expense_name = input("Enter a name to search for: ")
                expenses = database.search_expenses(expense_name)
                show_expenses(expenses)

            elif choice == "4":
                try:
                    expense_id = int(input("Expense ID to update: "))
                    amount = float(input("New amount: "))
                except ValueError:
                    print("Please enter a valid ID and amount.")
                    continue

                expense_name = input("New expense name: ")
                category = input("New category: ")
                expense_date = input("New date (YYYY-MM-DD): ")
                rows_changed = database.update_expense(
                    expense_id, expense_name, amount, category, expense_date
                )
                if rows_changed:
                    print("Expense updated.")
                else:
                    print("No expense was changed. Check the ID and entered values.")

            elif choice == "5":
                try:
                    expense_id = int(input("Expense ID to delete: "))
                except ValueError:
                    print("Please enter a valid expense ID.")
                    continue

                if database.delete_expense(expense_id):
                    print("Expense deleted.")
                else:
                    print("No expense found with that ID.")

            elif choice == "6":
                print("Goodbye!")
                break

            else:
                print("Please choose a number from 1 to 6.")

        except mysql.connector.Error as error:
            print(f"Database error: {error}")


if __name__ == "__main__":
    main()
