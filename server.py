import json
import logging
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import mysql.connector

import database


HOST = "127.0.0.1"
PORT = 8000
PROJECT_DIR = Path(__file__).resolve().parent


def expense_to_dict(expense):
    return {
        "expense_id": expense[0],
        "expense_name": expense[1],
        "amount": float(expense[2]),
        "category": expense[3],
        "expense_date": expense[4].isoformat(),
    }


def validate_expense(data):
    if not isinstance(data, dict):
        raise ValueError("Expected expense details.")

    name = data.get("expense_name")
    category = data.get("category")
    amount = data.get("amount")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Enter an expense name.")
    if not isinstance(category, str) or not category.strip():
        raise ValueError("Enter a category.")
    if isinstance(amount, bool):
        raise ValueError("Enter a valid amount greater than zero.")
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("Enter a valid amount greater than zero.") from None
    if amount <= 0 or amount == float("inf") or amount != amount:
        raise ValueError("Enter a valid amount greater than zero.")

    try:
        expense_date = date.fromisoformat(data.get("expense_date", ""))
    except (TypeError, ValueError):
        raise ValueError("Enter a valid date.") from None

    return name.strip(), amount, category.strip(), expense_date


class ExpenseTrackerHandler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("Invalid request body.") from None
        if content_length <= 0 or content_length > 100_000:
            raise ValueError("Invalid request body.")
        try:
            return json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError("Request body must be valid JSON.") from None

    def handle_database_error(self, error):
        logging.error("Database request failed: %s", error)
        self.send_json(500, {"error": "The database request failed. Check MySQL and credentials."})

    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/api/expenses":
            try:
                search = parse_qs(parsed_url.query).get("search", [""])[0].strip()
                rows = (
                    database.search_expenses(search)
                    if search
                    else database.get_all_expenses()
                )
                self.send_json(
                    200,
                    {
                        "expenses": [expense_to_dict(row) for row in rows],
                        "total": float(database.get_total_spent()),
                    },
                )
            except mysql.connector.Error as error:
                self.handle_database_error(error)
            return

        static_files = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/index.html": ("index.html", "text/html; charset=utf-8"),
            "/styles.css": ("styles.css", "text/css; charset=utf-8"),
            "/script.js": ("script.js", "text/javascript; charset=utf-8"),
        }
        file_info = static_files.get(parsed_url.path)
        if file_info is None:
            self.send_json(404, {"error": "Not found."})
            return

        file_name, content_type = file_info
        body = (PROJECT_DIR / file_name).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlparse(self.path).path != "/api/expenses":
            self.send_json(404, {"error": "Not found."})
            return
        try:
            name, amount, category, expense_date = validate_expense(self.read_json())
            expense_id = database.add_expense(name, amount, category, expense_date)
        except ValueError as error:
            self.send_json(400, {"error": str(error)})
        except mysql.connector.Error as error:
            self.handle_database_error(error)
        else:
            self.send_json(201, {"expense_id": expense_id})

    def do_PUT(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["api", "expenses"]:
            self.send_json(404, {"error": "Not found."})
            return
        try:
            expense_id = int(parts[2])
            if expense_id <= 0:
                raise ValueError
            name, amount, category, expense_date = validate_expense(self.read_json())
            changed = database.update_expense(
                expense_id, name, amount, category, expense_date
            )
            if not changed and not any(
                row[0] == expense_id for row in database.get_all_expenses()
            ):
                self.send_json(404, {"error": "Expense not found."})
                return
        except ValueError as error:
            message = str(error) or "Invalid expense ID."
            self.send_json(400, {"error": message})
        except mysql.connector.Error as error:
            self.handle_database_error(error)
        else:
            self.send_json(200, {"message": "Expense updated."})

    def do_DELETE(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["api", "expenses"]:
            self.send_json(404, {"error": "Not found."})
            return
        try:
            expense_id = int(parts[2])
            if expense_id <= 0:
                raise ValueError
            deleted = database.delete_expense(expense_id)
        except ValueError:
            self.send_json(400, {"error": "Invalid expense ID."})
        except mysql.connector.Error as error:
            self.handle_database_error(error)
        else:
            if deleted:
                self.send_json(200, {"message": "Expense deleted."})
            else:
                self.send_json(404, {"error": "Expense not found."})

    def log_message(self, format_string, *args):
        logging.info("%s - %s", self.address_string(), format_string % args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    server = ThreadingHTTPServer((HOST, PORT), ExpenseTrackerHandler)
    print(f"Expense Tracker is running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
