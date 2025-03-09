import psycopg2

class DBMethods:

    def __init__(self, db_name, db_user, db_pass):
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.conn = None

    def connect_db(self):
        self.conn = psycopg2.connect(database=self.db_name, user=self.db_user, password=self.db_pass)

    # 1. Функция, создающая структуру БД (таблицы).
    def create_init_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS Client (id SERIAL PRIMARY KEY, name VARCHAR(50) NOT NULL,"
                        "surname VARCHAR(50) NOT NULL);")
            cur.execute("CREATE TABLE IF NOT EXISTS Email (id SERIAL PRIMARY KEY, clientid INTEGER NOT NULL "
                        "REFERENCES Client(id), email VARCHAR(50) NOT NULL);")
            cur.execute("CREATE TABLE IF NOT EXISTS Phone (id SERIAL PRIMARY KEY, clientid INTEGER NOT NULL "
                        "REFERENCES Client(id), phone VARCHAR(50) NOT NULL);")
        self.conn.commit()

    # 2. Функция, позволяющая добавить нового клиента.
    def add_new_client(self, name, surname, email):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO Client (name, surname) SELECT %s, %s WHERE NOT EXISTS "
                        "(SELECT 1 FROM Client WHERE name=%s AND surname=%s);", (name, surname, name, surname))

            cur.execute("SELECT id FROM Client WHERE name=%s AND surname=%s", (name, surname))
            client_id = cur.fetchone()

            cur.execute("INSERT INTO Email (clientid, email) SELECT %s, %s WHERE NOT EXISTS "
                        "(SELECT 1 FROM Email WHERE clientid=%s AND email=%s);",
                        (client_id, email, client_id, email))

        self.conn.commit()

    # 3. Функция, позволяющая добавить телефон для существующего клиента.
    def add_phone_to_client(self, client_name, client_surname, phones=None):
        if phones:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM Client WHERE name=%s AND surname=%s", (client_name, client_surname))
                client_id = cur.fetchone()

                if client_id:
                    for phone in phones:
                        cur.execute("INSERT INTO Phone (clientid, phone) SELECT %s, %s WHERE NOT EXISTS "
                                    "(SELECT 1 FROM Phone WHERE clientid=%s AND phone=%s);",
                                    (client_id, phone, client_id, phone))

            self.conn.commit()

    # 4. Функция, позволяющая изменить данные о клиенте.
    def change_client(self, old_name, old_surname, old_email, new_name, new_surname, new_email):
        client_id = self.get_client(old_name, old_surname, old_email)
        if client_id:
            with self.conn.cursor() as cur:
                cur.execute("UPDATE Client SET name=%s, surname=%s WHERE id=%s;", (new_name, new_surname, client_id[0]))
                cur.execute("UPDATE Email SET email=%s WHERE clientid=%s;", (new_email, client_id[0]))
        self.conn.commit()

    # 5. Функция, позволяющая удалить телефон для существующего клиента.
    def delete_phone(self, name, surname, email, phone):
        client_id = self.get_client(name, surname, email)
        if client_id:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM Phone WHERE phone=%s AND clientid=%s;", (phone, client_id[0]))
        self.conn.commit()

    # 6. Функция, позволяющая удалить существующего клиента.
    def delete_client(self, name, surname, email):
        client_id = self.get_client(name, surname, email)
        if client_id:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM Phone WHERE clientid=%s;", (client_id[0],))
                cur.execute("DELETE FROM Email WHERE clientid=%s;", (client_id[0],))
                cur.execute("DELETE FROM Client WHERE id=%s;", (client_id[0],))
        self.conn.commit()

    # 7. Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
    def get_client(self, name=None, surname=None, email=None, phone=None):
        if phone:
            with self.conn.cursor() as cur:
                cur.execute("select c.id from client c inner join email e on c.id = e.clientid "
                            "left outer join (select clientid from phone where phone = %s) p "
                            "on c.id = p.clientid where c.name=%s "
                            "and c.surname =%s and e.email=%s", (phone, name, surname, email))
                return cur.fetchone()
        else:
            with self.conn.cursor() as cur:
                cur.execute("select c.id from client c inner join email e on c.id = e.clientid "
                            "where c.name=%s and c.surname =%s and e.email=%s order by c.id", (name, surname, email))
                return cur.fetchone()