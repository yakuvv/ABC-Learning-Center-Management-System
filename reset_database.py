# reset_database.py
import os
import database
from database import DB_NAME, clear_all_data, init_database

BACKUP_NAME = "abc_learning_center_backup.db"


def reset_all():
    """Clear every table in the main DB and backup copy."""
    if not os.path.exists(DB_NAME):
        init_database()
    clear_all_data(DB_NAME)
    print(f"Cleared all data from '{DB_NAME}'.")

    if os.path.exists(BACKUP_NAME):
        clear_all_data(BACKUP_NAME)
        print(f"Cleared all data from '{BACKUP_NAME}'.")


if __name__ == "__main__":
    print("WARNING: This will DELETE ALL data in your database(s)!")
    confirm = input("Type 'YES' to continue and reset database: ")
    if confirm == "YES":
        reset_all()
        print("Database has been reset successfully! Schema kept; all tables are empty.")
    else:
        print("Cancelled.")
