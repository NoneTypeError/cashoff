import sqlite3

main_db_name = 'core/db/cafe_zeus.db'

product_tb_name = 'menu_products'
type_name_tb_name = 'type_name'
check_tb_name = 'checks'
user_tb_name = 'user_db'
settings_name = 'settings'

product_tb_sql = '''product_id integer primary key, name text unique, p_type text, about text, price int'''
type_name_tb_sql = '''type_id integer primary key, type_name text unique, name text'''
check_tb_sql = '''check_id integer primary key, table_id int, products text, price int, date_txt date'''
user_tb_sql = 'user_id integer primary key, login text unique, password text, name text unique, validate text'
settings_sql = '''id integer primary key, name text unique, value text'''


class DataBase:
    connect = None
    cur = None

    def __init__(self, db_name, tb_name, sql_execute=None):
        self.db_name = db_name
        self.tb_name = tb_name
        self.sql_execute = sql_execute
        self.connect_to_db()
        self.connect.commit()

    def connect_to_db(self):
        try:
            self.connect = sqlite3.connect(str(self.db_name), check_same_thread=False)
            self.cur = self.connect.cursor()
        except Exception as error:
            print(error)
        else:
            self.create_tb(self.sql_execute)
            self.connect.commit()

    def create_tb(self, sql_execute):
        try:
            self.cur.execute("""CREATE TABLE IF NOT EXISTS """ + self.tb_name + ' (' + sql_execute + ')')
            self.connect.commit()
        except Exception as error:
            print(error)
        else:
            return True

    def insert_date(self, keys, values):
        try:
            self.cur.execute(f'INSERT INTO {self.tb_name} {keys} VALUES {values}')
            self.connect.commit()
        except sqlite3.IntegrityError:
            pass
        except sqlite3.OperationalError as err:
            pass

    def select_all(self):
        try:
            return self.cur.execute(f'''SELECT * FROM {self.tb_name}''').fetchall()
        except AttributeError:
            self.connect_to_db()

    def select_by_type(self, type_key, key):
        return self.cur.execute(
            f"SELECT * FROM {self.tb_name} "
            f"WHERE {type_key}='{key}'"
        )

    def select_by_like(self, like_type, like_str):
        return self.cur.execute(
            f"SELECT * FROM {self.tb_name} "
            f"WHERE {like_type} "
            f"LIKE '{like_str}' "
        )

    def update_by_type(self, type_id, u_id, type_key, key):
        try:
            self.cur.execute(
                f"UPDATE {self.tb_name} "
                f"SET {type_key}={key} "
                f"WHERE {type_id}={u_id}"
            )
            self.connect.commit()
        except Exception as error:
            print(error)
        else:
            return True


class DBInit:
    product_db = DataBase(main_db_name, product_tb_name, product_tb_sql)
    type_name_db = DataBase(main_db_name, type_name_tb_name, type_name_tb_sql)
    check_db = DataBase(main_db_name, check_tb_name, check_tb_sql)
    user_db = DataBase(main_db_name, user_tb_name, user_tb_sql)
    settings_db = DataBase(main_db_name, settings_name, settings_sql)
    # print('product_db', product_db.select_all())
    # print('type_name_db', type_name_db.select_all())
    # print('check_db', check_db.select_all())
    # print('user_db', user_db.select_all())
    # print('settings_db', settings_db.select_all())
