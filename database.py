import mysql.connector


def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="samsang@1982",
        database="personal_expense_tracker",
    )


def add_expense(expense_name, amount, category, expense_date):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        query = (
            "INSERT INTO Expenses (expense_name, amount, category, expense_date) "
            "VALUES (%s, %s, %s, %s)"
        )
        cursor.execute(query, (expense_name, amount, category, expense_date))
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()


def get_all_expenses():
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT expense_id, expense_name, amount, category, expense_date "
            "FROM Expenses ORDER BY expense_date DESC"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_total_spent():
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT SUM(amount) FROM Expenses")
        total = cursor.fetchone()[0]
        return total if total is not None else 0
    finally:
        cursor.close()
        connection.close()


def search_expenses(expense_name):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT expense_id, expense_name, amount, category, expense_date "
            "FROM Expenses WHERE expense_name LIKE %s ORDER BY expense_date DESC",
            (f"%{expense_name}%",),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def update_expense(expense_id, expense_name, amount, category, expense_date):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        query = (
            "UPDATE Expenses SET expense_name = %s, amount = %s, "
            "category = %s, expense_date = %s WHERE expense_id = %s"
        )
        cursor.execute(
            query, (expense_name, amount, category, expense_date, expense_id)
        )
        connection.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        connection.close()


def delete_expense(expense_id):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM Expenses WHERE expense_id = %s", (expense_id,))
        connection.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        connection.close()
