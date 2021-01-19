import kivy
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout

from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine

import os
import pyautogui
import sys
import sqlite3
import json

from core import const
from core import core
from core import sql_database


d_width, d_height = pyautogui.size()

Window.size = (d_width, d_height)
Window.fullscreen = True


class AskSureModal(ModalView):
    pass


class GetCashModal(ModalView):
    pass


class UserAddModal(ModalView):
    pass


class ModalEdit(ModalView):
    def __init__(self, root):
        super(ModalEdit, self).__init__()
        menu_items = [{"text": str(i[1])} for i in root.DB.type_name_db.select_all()]
        self.root_app = root
        self.menu = MDDropdownMenu(
            caller=self.ids.p_type,
            items=menu_items,
            position="bottom",
            width_mult=4,
        )
        self.menu.bind(on_release=self.set_item)

    def ok_sw(self, root_app):
        name = self.ids.name.text
        p_type = self.ids.p_type.text
        about = self.ids.about.text
        price = self.ids.price.text
        root_app.DB.product_db.insert_date(
            ('name', 'p_type', 'about', 'price'),
            (name, p_type, about, price))
        self.dismiss()

    def set_item(self, instance_menu, instance_menu_item):
        def set_item(interval):
            assert interval == interval
            self.ids.p_type.text = instance_menu_item.text
            instance_menu.dismiss()
        Clock.schedule_once(set_item, 0.5)


class ModalTableCount(ModalView):
    count = 0

    def ok_sw(self, root_app):
        try:
            s = self.count_input.text
        except ValueError:
            s = '0'
        sql_ = "UPDATE settings "\
               f"SET value={s} "\
               'WHERE name="table_count"'
        root_app.DB.settings_db.cur.execute(sql_)
        root_app.DB.settings_db.connect.commit()

        self.dismiss()
        root_app.on_start()


class ModalMenuType(ModalView):
    name = StringProperty()
    short_name = StringProperty()

    def ok_sw(self, root_app):
        name = self.ids.fullname.text
        short_name = self.ids.short_name.text
        root_app.DB.type_name_db.insert_date(
            ('type_name', 'name'),
            (short_name, name)
        )
        self.dismiss()
        root_app.on_start()


class AnswerModal(ModalView):
    price_sum = 0
    count = 0

    def __init__(self, root_app, product, **kwargs):
        super(AnswerModal, self).__init__(**kwargs)
        self.root_app = root_app
        self.product = product
        self.price_sum = 0
        self.reload()

    def reload(self):
        self.price_sum = self.count * self.product.price
        self.count_txt.text = str(self.count)
        self.price_sum_txt.text = str(self.count*self.product.price)
        self.ids.price_sum_txt.text = str(self.price_sum)
        self.ids.product_name.text = self.product.name

    def add_(self):
        self.count += 1
        self.reload()

    def remove_(self):
        if self.count != 0:
            self.count -= 1
            self.reload()

    def ok_sw(self):
        self.root_app.add_table(
            [
                self.product.product_id,
                self.product.name,
                self.count,
                self.product.price,
                self.price_sum
            ]
        )
        self.root_app.load_table_(self.root_app.table_id)
        self.root_app.tb_screen_sw('tb_screen')
        self.root_app.save_json()
        self.dismiss()


class ProductButton(BoxLayout):
    product_id = 0
    name = StringProperty()
    price = StringProperty()
    info = StringProperty()

    def __init__(self, product_id, name, price, about, **kwargs):
        super(ProductButton, self).__init__(**kwargs)
        self.product_id = product_id
        self.name = str(name)
        self.price = str(price)
        self.about = str(about)


class AddProductButton(BoxLayout):
    pass


class MenuButton(MDCard):
    txt = StringProperty()

    def __init__(self, txt, type_name, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        self.txt = txt
        self.type_name = type_name


class AddMenuButton(MDCard):
    pass


class MenuWin(Screen):
    pass


class ScrollListItem(MDCard):
    price = 0
    count = 0
    name = StringProperty('')
    price_sum = 0
    sum_txt = ObjectProperty()

    def __init__(self, root_app, i_id, name=StringProperty(''), price=0, count=0, *args):
        super(ScrollListItem, self).__init__()
        self.args = args
        self.root_app = root_app
        self.i_id = i_id
        self.name = name
        self.price = int(price)
        self.count = int(count)
        self.price_sum = self.price*self.count
        self.sum_txt.text = str(self.price_sum)

    def del_item(self):
        pass


class TableWin(Screen):
    table_id = StringProperty()

    def set_table_id(self, table_id):
        self.table_id = table_id


class TBButton(BoxLayout):
    table_id = StringProperty()
    txt = StringProperty()
    user_name = StringProperty()

    def __init__(self, txt, user_name, table_id, **kwargs):
        super(TBButton, self).__init__(**kwargs)
        self.txt = txt
        self.user_name = user_name
        self.table_id = table_id


class AddTBButton(BoxLayout):
    pass


class TableMain(Screen):
    pass


class Content(MDBoxLayout):
    pass


class ContentNavigationDrawer(BoxLayout):
    pass


class Login(ModalView):
    def __init__(self, table_id, mode):
        super(Login, self).__init__()
        self.table_id = table_id
        self.mode = mode


class UserScreenItem(MDCard):
    def __init__(self, user_id, login, password, name, validate):
        super(UserScreenItem, self).__init__()
        self.user_id = user_id
        self.login = login
        self.password = password
        self.name = name
        self.validate = validate
        self.load_user()

    def load_user(self):
        self.user_id_txt.text = str(self.user_id)
        self.login_txt.text = str(self.login)
        self.password_txt.text = str(self.password)
        self.name_txt.text = str(self.name)
        self.validate_txt.text = str(self.validate)


class AnswerDialog(ModalView):
    def __init__(self, root_app, i_id, ans_type, *args):
        super(AnswerDialog, self).__init__()
        self.i_id = i_id
        self.root_app = root_app
        self.ans_type = ans_type
        self.func = self.root_app.delete_item if ans_type else self.root_app.del_user
        self.args = args


class UserScreen(Screen):
    pass


class MyApp(MDApp):
    dialog = ObjectProperty()
    display = ObjectProperty()
    user = core.User()

    mode = False
    ru_ = const.lang
    win_size = d_width, d_height
    menu_list = None
    menu_type = None
    tables = {}
    users_list = []

    price_sum = {}
    table_id = ''
    from_date = ''
    to_date = ''
    DB = sql_database.DBInit()

    def data_ok_sw(self, root):
        from_ = root.from_input.text
        to_ = root.to_input.text
        if from_ == '' and to_ == '':
            sum_ = self.get_check_sum('2020-01-01', '2040-01-01')
        else:
            sum_ = self.get_check_sum(from_, to_)
        root.title_.text = core.number_format(str(sum_ if sum_ is not None else "0"))

    def add_user(self):
        self.DB.user_db.insert_date(('login', 'password', 'name', 'validate'), ('', '', '', 'User'))
        self.load_workers()

    def edit_users(self, user_id, widget_):
        name = widget_.name_txt.text
        login = widget_.login_txt.text
        password = widget_.password_txt.text
        validate = widget_.validate_txt.text

        sql_ = "UPDATE user_db " \
               "SET name=?, login=?, password=?, validate=? " \
               "WHERE user_id=?"

        self.DB.user_db.cur.execute(
            sql_,
            (name, login, password, validate, user_id)
        )
        self.DB.user_db.connect.commit()
        self.load_workers()

    def del_user(self, user_id):
        self.DB.user_db.cur.execute(
            f'DELETE FROM user_db '
            f'WHERE user_id={user_id}')
        self.DB.user_db.connect.commit()
        self.load_workers()

    def load_workers(self):
        self.users_list = self.DB.user_db.select_all()
        self.tb_screen_sw('workers')
        self.display.ids.user_screen.ids.user_box.clear_widgets()
        for i in self.users_list:
            self.display.ids.user_screen.ids.user_box.add_widget(
                UserScreenItem(*i)
            )

    def get_types(self):
        list_ = {}
        for i in self.DB.type_name_db.select_all():
            list_[i[1]] = i[2]
        return list_

    @staticmethod
    def edit_list(first, second):
        list_ = []
        for i in range(len(first)):
            if i == 0 or i == 2:
                list_.append(first[i])
            else:
                list_.append(first[i] + second[i])
        return list_

    def add_table(self, product):
        if product[2] != 0:
            table = self.tables[self.table_id]
            if table.get(str(product[0])) is None:
                table[str(product[0])] = product[1::]
            else:
                table[str(product[0])] = self.edit_list(
                    table[str(product[0])], product[1::]
                )
        self.reload_item_list()

    def add_win(self, product_id):
        if self.mode:
            self.del_product(product_id)
        else:
            product = core.get_product(self.DB, product_id)
            s = AnswerModal(self, product)
            s.open()

    def tb_screen_sw(self, screen):
        self.display.ids.main.current = screen

    def ask_sure(self):
        pass

    def delete_item(self, i_id):
        self.tables[self.table_id].pop(i_id)
        self.reload_item_list()

    def delete_item_sw(self, i_id, ans_type):
        dialog = AnswerDialog(self, i_id, ans_type)
        dialog.open()

    @staticmethod
    def exit_app(*event):
        sys.exit()

    def login_analyze(self, login_win, table_id=None):

        login = login_win.login_txt.text
        password = login_win.password_txt.text
        modes = [
            'add_table',
            'add_menu',
            'add_type',
            'workers',
            'mode'
        ]
        sql_ = f'SELECT * FROM user_db ' \
               f'WHERE login="{login}" ' \
               f'AND password="{password}"'
        response = self.DB.user_db.cur.execute(sql_).fetchall()
        try:
            self.user = response[0]
        except IndexError:
            login_win.login_txt.error = True
            login_win.password_txt.error = True
            login_win.user_name.text = "Не правилный Login или Password"
        else:
            if login_win.mode == 'table':
                table = self.tables.get(table_id)
                if self.user[-1] == 'admin':
                    return True
                elif (table == {}) or (len(table) == 1):
                    table['user'] = self.user[0]
                    return True
                elif self.user[0] == table['user']:
                    return True
                else:
                    user = self.DB.user_db.select_by_type('user_id', table['user']).fetchall()[0]
                    login_win.user_name.text = f"Стол уже обслуживается {user[3]}"
                    return False
            elif login_win.mode in modes:
                if self.user[-1] == 'admin':
                    return True
                login_win.user_name.text = f"У вас недостаточно привилегий"
                return False
            else:
                return True

    def user_open(self, table_id, login_win):
        if self.login_analyze(login_win, table_id):
            if login_win.mode == 'table':
                self.load_table_(table_id)
            elif login_win.mode == 'mode':
                self.mode_switch_sw()
                if self.mode:
                    self.theme_cls.primary_palette = 'Red'
                    self.display.ids.nav_drawer_.ids.mode_switch.md_bg_color = 1, 0, 0, 1
                else:
                    self.theme_cls.primary_palette = 'Indigo'
                    self.display.ids.nav_drawer_.ids.mode_switch.md_bg_color = 0, 0, 0, 0
            elif login_win.mode == 'add_table':
                self.add_table_sw()
            elif login_win.mode == 'add_menu':
                self.add_menu_sw()
            elif login_win.mode == 'add_type':
                self.add_menu_type_sw()
            elif login_win.mode == 'workers':
                self.load_workers()

            login_win.dismiss()

    def load_table_(self, table_id):
        self.table_id = str(int(table_id))

        if self.table_id == '0':
            self.display.ids.tb_screen.ids.table_name.text = "Сабой"
        else:
            self.display.ids.tb_screen.ids.table_name.text = "Стол - " + str(self.table_id)
        try:
            table, p_sum, l_sum = self.get_sum_str()
            self.display.ids.tb_screen.main_sum.text = core.number_format(l_sum)
        except Exception as err:
            print(err)

        self.display.ids.tb_screen.ids.user_name.text = str(self.user[3])
        self.tb_screen_sw('tb_screen')
        self.reload_item_list()

    def reload_item_list(self):
        self.display.ids.tb_screen.ids.item_list.clear_widgets()

        for i in self.tables.keys():
            self.price_sum[i] = []
            for _ in self.tables[str(i)]:
                if _ != 'user':
                    self.price_sum[i].append(self.tables[str(i)][_][-1])

        if self.tables.get(self.table_id) is None:
            self.tables[str(self.table_id)] = {}

        for i in self.tables[str(self.table_id)]:
            if i == 'user':
                pass
            else:
                self.display.ids.tb_screen.ids.item_list.add_widget(
                    ScrollListItem(self, i, *self.tables.get(self.table_id).get(i))
                )

        table, p_sum, l_sum = self.get_sum_str()
        self.display.ids.tb_screen.main_sum.text = core.number_format(l_sum)
        self.save_json()

    def load_menu(self):
        self.display.ids.menu_screen.ids.box_menu.clear_widgets()
        for i in self.menu_list.keys():
            self.display.ids.menu_screen.ids.box_menu.add_widget(
                MenuButton(txt=self.menu_list[i], type_name=i)
            )
        if self.mode:
            self.display.ids.menu_screen.ids.box_menu.add_widget(AddMenuButton())

    def load_menu_by_type(self, menu_type, mode=None):
        def load():
            for i in core.get_products(self.DB, menu_type):
                self.display.ids.menu_screen.ids.menu_type.add_widget(
                    ProductButton(
                        product_id=i.product_id,
                        name=i.name,
                        price=i.price,
                        about=i.about,
                    )
                )
        self.menu_type = menu_type

        if mode:
            self.display.ids.menu_screen.ids.menu_type.clear_widgets()
            load()
            if self.mode:
                self.display.ids.menu_screen.ids.menu_type.add_widget(AddProductButton())
        else:
            if self.mode:
                self.del_type(menu_type)
                self.display.ids.menu_screen.ids.menu_type.add_widget(AddProductButton())
            else:
                self.display.ids.menu_screen.ids.menu_type.clear_widgets()
                load()

    def load_tables(self):
        self.load_json()
        self.display.ids.tables_screen.ids.table_list.clear_widgets()

        for i in self.tables.keys():
            text = "Стол - " + str(i) if i != '0' else 'Сабой'
            user_id = self.tables[i].get('user')
            try:
                user = self.DB.user_db.select_by_type('user_id', user_id).fetchall()[0]
            except IndexError:
                user_name = 'Свободно '
            else:
                user_name = user[3]

            self.display.ids.tables_screen.ids.table_list.add_widget(
                TBButton(txt=text, user_name=user_name, table_id=i)
            )

        if self.mode:
            self.display.ids.tables_screen.ids.table_list.add_widget(AddTBButton())

    # return sum by date
    def get_check_sum(self, from_, to_):
        sql_ = f"SELECT SUM(price) FROM checks " \
               f"WHERE date_txt >= '{from_}' " \
               f"AND date_txt <= '{to_}'"
        sum_txt = self.DB.check_db.cur.execute(sql_).fetchall()[0][0]
        return sum_txt

    # save check to sql database
    def save_check(self, l_sum):
        date_ = core.get_date_time().get('date')
        self.DB.check_db.insert_date(
            ('table_id', 'price', 'date_txt'),
            (self.table_id, l_sum, date_)
        )

    # return sum (table = some table: p_sum = prise sum table: l_sum = last_sum table
    def get_sum_str(self):
        table = self.tables[self.table_id]
        price = [table[i][-1] if i != 'user' else 0 for i in table.keys()]
        p_sum = int(sum(price))
        if self.table_id != '0':
            l_sum = int((p_sum / 100) * 15) + p_sum
        else:
            l_sum = p_sum
        p_sum = str(p_sum)
        l_sum = str(l_sum)
        return table, p_sum, l_sum

    def print_check(self):
        table = self.tables[self.table_id]
        if table != {}:
            table, p_sum, l_sum = self.get_sum_str()
            response = self.DB.check_db.select_all()
            try:
                check_id = str(response[-1][0] + 1)
            except IndexError:
                check_id = '1'

            try:
                worker = self.DB.user_db.select_by_type('user_id', table['user']).fetchall()[0][3]
            except IndexError:
                worker = ''
            # Here printer error

            try:
                core.write_and_print(self.table_id, table, p_sum, l_sum, worker, check_id)
            except OSError:
                pass

            self.save_check(l_sum)

        self.tables[self.table_id] = {}
        self.price_sum[self.table_id] = []
        self.save_json()
        self.table_id = '0'
        self.tb_screen_sw('main_tb_screen')

    def load_json(self):
        db = int(self.DB.settings_db.select_by_type('name', 'table_count').fetchall()[0][2])
        load = False
        try:
            with open('core/db/tables.json', 'r') as f:
                self.tables = json.load(f)
        except FileNotFoundError:
            load = True

        if len(self.tables) != db+1:
            load = True

        if load:
            self.tables = {
                str(int(i)): {}
                for i in range(db + 1)
            }

    def save_json(self):
        with open('core/db/tables.json', 'w') as f:
            json.dump(self.tables, f, indent=2)
        self.load_tables()

    @staticmethod
    def cash_menu():
        cash = GetCashModal()
        cash.open()

    @staticmethod
    def login_sw(table_id, mode):
        login = Login(table_id, mode)
        login.open()

    @staticmethod
    def add_menu_type_sw():
        message = ModalMenuType()
        message.open()

    def add_menu_sw(self):
        message = ModalEdit(self)
        message.open()

    @staticmethod
    def add_table_sw():
        message = ModalTableCount()
        message.open()

    def load_nav(self):
        self.display.ids.nav_drawer_.nav_list.add_widget(MDExpansionPanel(
            icon="img/logo.png",
            content=Content(),
            panel_cls=MDExpansionPanelOneLine(
                text="Добавить",
                secondary_text="Secondary text",
                tertiary_text="Tertiary text",)
        ))

    def del_product(self, product_id):
        sql_ = f'DELETE FROM menu_products ' \
               f'WHERE product_id={product_id}'
        self.DB.product_db.cur.execute(sql_)
        self.DB.product_db.connect.commit()
        self.on_start()
        self.load_menu_by_type(self.menu_type, True)

    def del_type(self, type_name):
        sql_ = f'DELETE FROM type_name ' \
               f'WHERE type_name="{type_name}"'
        self.DB.product_db.cur.execute(sql_)
        self.DB.product_db.connect.commit()
        self.on_start()

    def mod_switcher(self):
        self.login_sw(None, 'mode')

    def mode_switch_sw(self):
        self.load_menu_by_type(self.menu_type, True)
        if self.mode:
            self.mode = False
            self.display.ids.toolbar_.title = '"ZEVS"'
        else:
            self.mode = True
            self.display.ids.toolbar_.title = '"ZEVS" (edit mode)'
        self.on_start()

    def on_start(self):
        self.menu_list = self.get_types()
        self.load_menu()
        self.load_tables()

    def build(self):
        # self.DB.user_db.insert_date(('login', 'password', 'name', 'validate'), ('admin', 'admin', 'Admin', 'admin'))
        # self.DB.settings_db.insert_date(('name', 'value'), ('table_count', '10'))
        self.theme_cls.primary_palette = 'Indigo'
        self.display = Builder.load_file('style.kv')
        self.load_nav()
        return self.display


def resource_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)
    return os.path.join(os.path.abspath("."))


if __name__ == '__main__':
    kivy.resources.resource_add_path(resource_path())
    my_app = MyApp()
    my_app.run()
