
import csv
import json
import re
import sys
from datetime import date, datetime

import psycopg2
import psycopg2.extras

from connect import get_connection, init_db


def _validate_phone(phone: str) -> bool:
    """Простая проверка: только цифры, +, пробелы, дефисы; минимум 7 цифр."""
    digits = re.sub(r"[^\d]", "", phone)
    return len(digits) >= 7


def _validate_email(email: str) -> bool:
    """Базовая валидация email."""
    if not email:
        return True          # email необязателен
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def _serialize(obj):
    """JSON-сериализатор для date/datetime."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Тип {type(obj)} не сериализуем")


def _print_contacts(rows, headers=None):
    """Красивый вывод списка контактов."""
    if not rows:
        print("  (нет результатов)")
        return
    if headers is None:
        headers = [desc for desc in rows[0].keys()] if hasattr(rows[0], "keys") else []
    for row in rows:
        parts = []
        if hasattr(row, "_asdict"):
            d = row._asdict()
        elif hasattr(row, "keys"):
            d = dict(row)
        else:
            d = dict(zip(headers, row))
        for k, v in d.items():
            if v is not None:
                parts.append(f"{k}: {v}")
        print("  " + " | ".join(parts))


#функции

def db_add_phone(contact_name: str, phone: str, phone_type: str = "mobile"):
    """Вызывает процедуру add_phone."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s);",
                        (contact_name, phone, phone_type))
    print(f"[OK] Телефон добавлен контакту '{contact_name}'.")


def db_move_to_group(contact_name: str, group_name: str):
    """Вызывает процедуру move_to_group."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s);",
                        (contact_name, group_name))
    print(f"[OK] Контакт '{contact_name}' перемещён в группу '{group_name}'.")


def db_search_contacts(query: str):
    """Вызывает функцию search_contacts (имя + email + телефоны)."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM search_contacts(%s);", (query,))
            rows = cur.fetchall()
    return rows


#поиск фильтр

def get_all_contacts(sort_by: str = "username") -> list:
    """
    Возвращает все контакты с телефонами и группами.
    sort_by: 'username' | 'birthday' | 'date_added'
    """
    allowed_sort = {"username", "birthday", "date_added"}
    if sort_by not in allowed_sort:
        sort_by = "username"

    sql = f"""
        SELECT c.id, c.username AS name, c.email, c.birthday,
               g.name AS group_name,
               ph.phone, ph.type AS phone_type,
               c.date_added
        FROM contacts c
        LEFT JOIN groups g  ON c.group_id  = g.id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        ORDER BY c.{sort_by} NULLS LAST, ph.type
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()


def filter_by_group(group_name: str, sort_by: str = "username") -> list:
    """Фильтрация контактов по группе."""
    allowed_sort = {"username", "birthday", "date_added"}
    if sort_by not in allowed_sort:
        sort_by = "username"

    sql = f"""
        SELECT c.id, c.username AS name, c.email, c.birthday,
               g.name AS group_name,
               ph.phone, ph.type AS phone_type,
               c.date_added
        FROM contacts c
        JOIN  groups g  ON c.group_id  = g.id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        WHERE g.name ILIKE %s
        ORDER BY c.{sort_by} NULLS LAST
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (group_name,))
            return cur.fetchall()


def search_by_email(email_pattern: str) -> list:
    """Частичный поиск по email."""
    sql = """
        SELECT c.id, c.username AS name, c.email, c.birthday,
               g.name AS group_name,
               ph.phone, ph.type AS phone_type,
               c.date_added
        FROM contacts c
        LEFT JOIN groups g  ON c.group_id  = g.id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        WHERE c.email ILIKE %s
        ORDER BY c.username
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (f"%{email_pattern}%",))
            return cur.fetchall()


def paginated_view(page_size: int = 5, sort_by: str = "username"):
    offset = 0
    allowed_sort = {"username", "birthday", "date_added"}
    if sort_by not in allowed_sort:
        sort_by = "username"

    while True:
        sql = f"""
            SELECT c.id, c.username AS name, c.email, c.birthday,
                   g.name AS group_name,
                   string_agg(ph.phone || ' (' || COALESCE(ph.type,'?') || ')', ', ') AS phones,
                   c.date_added
            FROM contacts c
            LEFT JOIN groups g  ON c.group_id  = g.id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            GROUP BY c.id, c.username, c.email, c.birthday, g.name, c.date_added
            ORDER BY c.{sort_by} NULLS LAST
            LIMIT %s OFFSET %s
        """
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, (page_size, offset))
                rows = cur.fetchall()

        if not rows and offset == 0:
            print("  База контактов пуста.")
            break

        page_num = offset // page_size + 1
        print(f"\n─── Страница {page_num} ───")
        _print_contacts(rows)

        if len(rows) < page_size:
            print("  (конец списка)")
            nav = input("  [prev / quit]: ").strip().lower()
        else:
            nav = input("  [next / prev / quit]: ").strip().lower()

        if nav == "next" and len(rows) == page_size:
            offset += page_size
        elif nav == "prev" and offset >= page_size:
            offset -= page_size
        elif nav == "quit" or nav == "q":
            break
        else:
            print("  Недопустимая команда или достигнут конец/начало списка.")



#Экспорт Импорт


def export_to_json(filepath: str = "contacts_export.json"):
    """Экспортирует все контакты (с телефонами и группой) в JSON."""
    sql = """
        SELECT c.id, c.username AS name, c.email,
               c.birthday::text AS birthday,
               g.name AS group_name,
               c.date_added::text AS date_added,
               COALESCE(
                   json_agg(
                       json_build_object('phone', ph.phone, 'type', ph.type)
                   ) FILTER (WHERE ph.id IS NOT NULL),
                   '[]'
               ) AS phones
        FROM contacts c
        LEFT JOIN groups g  ON c.group_id  = g.id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        GROUP BY c.id, c.username, c.email, c.birthday, g.name, c.date_added
        ORDER BY c.username
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

    data = [dict(row) for row in rows]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=_serialize)

    print(f"[OK] Экспортировано {len(data)} контактов в '{filepath}'.")


def import_from_json(filepath: str = "contacts_export.json"):
    """
    Импортирует контакты из JSON.
    При дубликате (совпадение имени) спрашивает: skip / overwrite.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[ERR] Файл '{filepath}' не найден.")
        return

    inserted = skipped = overwritten = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            for contact in data:
                name      = contact.get("name", "").strip()
                email     = contact.get("email") or None
                birthday  = contact.get("birthday") or None
                group_name = contact.get("group_name") or "Other"
                phones    = contact.get("phones", [])

                if not name:
                    print("[WARN] Пропуск записи без имени.")
                    continue

                cur.execute("SELECT id FROM contacts WHERE username ILIKE %s LIMIT 1;", (name,))
                existing = cur.fetchone()

                if existing:
                    choice = input(
                        f"  Контакт '{name}' уже существует. "
                        "[s]кип / [o]верврайт? "
                    ).strip().lower()
                    if choice.startswith("o"):
                        # Удалить старый (телефоны удалятся каскадом)
                        cur.execute("DELETE FROM contacts WHERE id = %s;", (existing[0],))
                        conn.commit()
                        overwritten += 1
                    else:
                        skipped += 1
                        continue

                # Найти/создать группу
                cur.execute(
                    "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
                    (group_name,)
                )
                cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
                group_id = cur.fetchone()[0]

                # Вставить контакт
                cur.execute(
                    """
                    INSERT INTO contacts (username, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (name, email, birthday, group_id)
                )
                contact_id = cur.fetchone()[0]

                # Вставить телефоны
                for ph in phones:
                    p_phone = ph.get("phone", "").strip()
                    p_type  = ph.get("type", "mobile")
                    if p_phone and _validate_phone(p_phone):
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                            (contact_id, p_phone, p_type)
                        )

                conn.commit()
                inserted += 1

    print(
        f"[OK] JSON импорт завершён: добавлено {inserted}, "
        f"перезаписано {overwritten}, пропущено {skipped}."
    )



# 3.3 CSV-импорт 


def import_from_csv(filepath: str = "contacts.csv"):
    """
    Импортирует контакты из CSV.
    Ожидаемые колонки: name, phone, phone_type, email, birthday, group
    Валидирует телефон и email перед вставкой.
    """
    try:
        f = open(filepath, newline="", encoding="utf-8")
    except FileNotFoundError:
        print(f"[ERR] Файл '{filepath}' не найден.")
        return

    inserted = errors = 0
    with f, get_connection() as conn:
        reader = csv.DictReader(f)
        with conn.cursor() as cur:
            for row in reader:
                name       = row.get("name", "").strip()
                phone      = row.get("phone", "").strip()
                phone_type = row.get("phone_type", "mobile").strip() or "mobile"
                email      = row.get("email", "").strip() or None
                birthday   = row.get("birthday", "").strip() or None
                group_name = row.get("group", "Other").strip() or "Other"

                # Валидация
                if not name:
                    print(f"[WARN] Строка без имени пропущена: {dict(row)}")
                    errors += 1
                    continue
                if phone and not _validate_phone(phone):
                    print(f"[WARN] Неверный телефон '{phone}' для '{name}', пропуск строки.")
                    errors += 1
                    continue
                if email and not _validate_email(email):
                    print(f"[WARN] Неверный email '{email}' для '{name}', email сброшен.")
                    email = None
                if phone_type not in ("home", "work", "mobile"):
                    phone_type = "mobile"

                try:
                    # Группа
                    cur.execute(
                        "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
                        (group_name,)
                    )
                    cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
                    group_id = cur.fetchone()[0]

                    # Контакт (upsert по имени — обновляем поля)
                    cur.execute(
                        """
                        INSERT INTO contacts (username, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                        RETURNING id;
                        """,
                        (name, email, birthday, group_id)
                    )
                    result = cur.fetchone()
                    if result is None:
                        cur.execute("SELECT id FROM contacts WHERE username = %s;", (name,))
                        result = cur.fetchone()
                    contact_id = result[0]

                    # Телефон (только если не пустой и не дубликат)
                    if phone:
                        cur.execute(
                            """
                            INSERT INTO phones (contact_id, phone, type)
                            SELECT %s, %s, %s
                            WHERE NOT EXISTS (
                                SELECT 1 FROM phones
                                WHERE contact_id = %s AND phone = %s
                            );
                            """,
                            (contact_id, phone, phone_type, contact_id, phone)
                        )

                    conn.commit()
                    inserted += 1

                except Exception as e:
                    conn.rollback()
                    print(f"[ERR] Ошибка при импорте '{name}': {e}")
                    errors += 1

    print(f"[OK] CSV импорт завершён: добавлено/обновлено {inserted}, ошибок {errors}.")


# ────────────────────────────────────────────────────────────
#  Добавление контакта через консоль
# ────────────────────────────────────────────────────────────

def add_contact_interactive():
    """Диалоговое добавление контакта с расширенными полями."""
    print("\n── Добавление нового контакта ──")
    name = input("Имя: ").strip()
    if not name:
        print("[ERR] Имя не может быть пустым.")
        return

    email = input("Email (Enter — пропустить): ").strip() or None
    if email and not _validate_email(email):
        print("[WARN] Неверный формат email, поле сброшено.")
        email = None

    birthday = input("День рождения (ГГГГ-ММ-ДД, Enter — пропустить): ").strip() or None

    # Группа
    print("Группы: Family, Work, Friend, Other")
    group_name = input("Группа (Enter → Other): ").strip() or "Other"

    # Телефоны
    phones = []
    print("Введите телефоны (пустой ввод — завершить):")
    while True:
        ph = input("  Телефон: ").strip()
        if not ph:
            break
        if not _validate_phone(ph):
            print("  [WARN] Неверный формат телефона, пропуск.")
            continue
        ph_type = input("  Тип (home/work/mobile) [mobile]: ").strip().lower() or "mobile"
        if ph_type not in ("home", "work", "mobile"):
            ph_type = "mobile"
        phones.append((ph, ph_type))

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Группа
            cur.execute(
                "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
                (group_name,)
            )
            cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
            group_id = cur.fetchone()[0]

            # Контакт
            cur.execute(
                """
                INSERT INTO contacts (username, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (name, email, birthday, group_id)
            )
            contact_id = cur.fetchone()[0]

            # Телефоны
            for ph, ph_type in phones:
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                    (contact_id, ph, ph_type)
                )
            conn.commit()

    print(f"[OK] Контакт '{name}' добавлен (id={contact_id}).")


# ────────────────────────────────────────────────────────────
#  Главное меню
# ────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════════╗
║        PhoneBook Extended — TSIS 1       ║
╠══════════════════════════════════════════╣
║  1. Добавить контакт                     ║
║  2. Показать все (с сортировкой)         ║
║  3. Постраничный просмотр                ║
║  4. Фильтр по группе                     ║
║  5. Поиск по email                       ║
║  6. Универсальный поиск (имя/email/тел)  ║
║  7. Добавить телефон к контакту          ║
║  8. Переместить в группу                 ║
║  9. Экспорт в JSON                       ║
║ 10. Импорт из JSON                       ║
║ 11. Импорт из CSV                        ║
║  0. Выход                                ║
╚══════════════════════════════════════════╝
"""


def main():
    init_db()

    while True:
        print(MENU)
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            add_contact_interactive()

        elif choice == "2":
            print("\nСортировка: username / birthday / date_added")
            sort_by = input("Поле сортировки [username]: ").strip() or "username"
            rows = get_all_contacts(sort_by)
            print(f"\n── Все контакты (сортировка: {sort_by}) ──")
            _print_contacts(rows)

        elif choice == "3":
            print("\nСортировка: username / birthday / date_added")
            sort_by = input("Поле сортировки [username]: ").strip() or "username"
            try:
                page_size = int(input("Размер страницы [5]: ").strip() or "5")
            except ValueError:
                page_size = 5
            paginated_view(page_size, sort_by)

        elif choice == "4":
            print("Доступные группы: Family, Work, Friend, Other")
            group = input("Введите группу: ").strip()
            print("\nСортировка: username / birthday / date_added")
            sort_by = input("Поле сортировки [username]: ").strip() or "username"
            rows = filter_by_group(group, sort_by)
            print(f"\n── Контакты группы '{group}' ──")
            _print_contacts(rows)

        elif choice == "5":
            pattern = input("Введите часть email: ").strip()
            rows = search_by_email(pattern)
            print(f"\n── Email-поиск '{pattern}' ──")
            _print_contacts(rows)

        elif choice == "6":
            query = input("Поисковый запрос (имя / email / телефон): ").strip()
            rows = db_search_contacts(query)
            print(f"\n── Результаты поиска '{query}' ──")
            _print_contacts(rows)

        elif choice == "7":
            cname = input("Имя контакта: ").strip()
            phone = input("Новый телефон: ").strip()
            ptype = input("Тип (home/work/mobile) [mobile]: ").strip() or "mobile"
            try:
                db_add_phone(cname, phone, ptype)
            except Exception as e:
                print(f"[ERR] {e}")

        elif choice == "8":
            cname = input("Имя контакта: ").strip()
            group = input("Новая группа: ").strip()
            try:
                db_move_to_group(cname, group)
            except Exception as e:
                print(f"[ERR] {e}")

        elif choice == "9":
            filepath = input("Имя файла [contacts_export.json]: ").strip() or "contacts_export.json"
            export_to_json(filepath)

        elif choice == "10":
            filepath = input("Имя файла [contacts_export.json]: ").strip() or "contacts_export.json"
            import_from_json(filepath)

        elif choice == "11":
            filepath = input("Имя CSV-файла [contacts.csv]: ").strip() or "contacts.csv"
            import_from_csv(filepath)

        elif choice == "0":
            print("До свидания!")
            sys.exit(0)

        else:
            print("[WARN] Неизвестная команда.")


if __name__ == "__main__":
    main()