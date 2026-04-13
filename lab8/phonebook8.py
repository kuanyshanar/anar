from connect8 import get_connection


def create_table():
    query = """
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50),
        phone VARCHAR(20) NOT NULL
    );
    """

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query)
        conn.commit()
        print("Table created successfully.")
    except Exception as e:
        conn.rollback()
        print("Error creating table:", e)
    finally:
        cur.close()
        conn.close()


def load_sql_file(filename):
    conn = get_connection()
    cur = conn.cursor()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            sql = f.read()
        cur.execute(sql)
        conn.commit()
        print(f"{filename} loaded successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error loading {filename}:", e)
    finally:
        cur.close()
        conn.close()


def insert_from_console():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    phone = input("Enter phone: ")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "CALL insert_or_update_user(%s, %s, %s)",
            (first_name, last_name, phone)
        )
        conn.commit()
        print("User inserted/updated successfully.")
    except Exception as e:
        conn.rollback()
        print("Error inserting user:", e)
    finally:
        cur.close()
        conn.close()


def search_by_pattern():
    pattern = input("Enter search pattern: ")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
        rows = cur.fetchall()

        if rows:
            print("\nMatched contacts:")
            for row in rows:
                print(row)
        else:
            print("No matching contacts found.")
    except Exception as e:
        print("Error searching contacts:", e)
    finally:
        cur.close()
        conn.close()


def get_paginated_contacts():
    limit_count = int(input("Enter limit: "))
    offset_count = int(input("Enter offset: "))

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM get_contacts_paginated(%s, %s)",
            (limit_count, offset_count)
        )
        rows = cur.fetchall()

        if rows:
            print("\nPaginated contacts:")
            for row in rows:
                print(row)
        else:
            print("No contacts found.")
    except Exception as e:
        print("Error fetching contacts:", e)
    finally:
        cur.close()
        conn.close()


def delete_user():
    value = input("Enter name or phone to delete: ")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL delete_user(%s)", (value,))
        conn.commit()
        print("User deleted successfully.")
    except Exception as e:
        conn.rollback()
        print("Error deleting user:", e)
    finally:
        cur.close()
        conn.close()


def insert_many_users():
    print("Enter users (type 'stop' to finish):")

    first_names = []
    last_names = []
    phones = []

    while True:
        first_name = input("First name: ")
        if first_name.lower() == "stop":
            break

        last_name = input("Last name: ")
        phone = input("Phone: ")

        first_names.append(first_name)
        last_names.append(last_name)
        phones.append(phone)

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "CALL insert_many_users(%s, %s, %s)",
            (first_names, last_names, phones)
        )
        conn.commit()
        print("Bulk insert completed.")
    except Exception as e:
        conn.rollback()
        print("Error inserting users:", e)
    finally:
        cur.close()
        conn.close()


def show_all_contacts():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM phonebook ORDER BY id")
        rows = cur.fetchall()

        if rows:
            print("\nAll contacts:")
            for row in rows:
                print(row)
        else:
            print("No contacts.")
    except Exception as e:
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def show_incorrect_data():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM incorrect_data")
        rows = cur.fetchall()

        if rows:
            print("\nIncorrect data:")
            for row in rows:
                print(row)
        else:
            print("No incorrect data.")
    except Exception as e:
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def menu():
    while True:
        print("\n МЕНЮ ТЕЛЕФОННОЙ КНИГИ")
        print("1) Создать таблицу")
        print("2) Загрузить SQL функции")
        print("3) Загрузить SQL процедуры")
        print("4) Добавить контакт")
        print("5) Поиск контактов")
        print("6) Пагинация")
        print("7) Массовое добавление")
        print("8) Удалить контакт")
        print("9) Показать все контакты")
        print("10) Показать ошибки")
        print("0) Выход")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            create_table()
        elif choice == "2":
            load_sql_file("functions.sql")
        elif choice == "3":
            load_sql_file("procedures.sql")
        elif choice == "4":
            insert_from_console()
        elif choice == "5":
            search_by_pattern()
        elif choice == "6":
            get_paginated_contacts()
        elif choice == "7":
            insert_many_users()
        elif choice == "8":
            delete_user()
        elif choice == "9":
            show_all_contacts()
        elif choice == "10":
            show_incorrect_data()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    menu()