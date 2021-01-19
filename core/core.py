import datetime
from fpdf import FPDF
import os


def write_and_print(table_id, table, p_sum, l_sum, worker, id_):
    now = get_date_time()['full_date']
    percent = '15 % Обслуживание'
    sum_1 = "Сумма:" + number_format(str(p_sum))
    sum_2 = "Итог:" + number_format(str(l_sum))
    end_txt = "***************************"
    if table_id == '0':
        table_info = f'Сабой'
    else:
        table_info = f'Стол - {table_id}'
    worker_and_id = "ID:" + id_ + ' :: ' + worker

    pdf = FPDF('P', 'mm', (60, 250))
    pdf.set_left_margin(0)
    pdf.add_page()
    pdf.add_font('Waree', '', 'core/fonts/DejaVuSansCondensed-Bold.ttf', uni=True)
    pdf.image('img/logo.png', x=None, y=None, w=60, h=20, type='png', link='')
    pdf.set_font('Waree', '', 15)
    pdf.cell(0, 10, table_info, 0, 1, 'C')
    pdf.set_font('Waree', '', 11)
    pdf.cell(0, 5, worker_and_id, 0, 1, 'L')
    pdf.cell(0, 5, str(now), 0, 1, 'L')
    pdf.set_font('Waree', '', 15)
    pdf.cell(0, 10, 'Продукты: ', 0, 1, 'C')
    pdf.set_font('Waree', '', 11)
    for i in table.keys():
        if i != 'user':
            product = table.get(i)
            name = product[0] + ' : ' + str(product[1]) + 'x : ' + str(product[3])
            pdf.multi_cell(0, 5, name, 0, 1, 'L')

    pdf.cell(0, 2, '', 0, 1, 'L')
    if table_id != '0':
        pdf.set_font('Waree', '', 11)
        pdf.cell(0, 5, sum_1, 0, 1, 'L')
        pdf.cell(0, 5, percent, 0, 1, 'L')
        pdf.set_font('Waree', '', 15)
        pdf.cell(0, 5, sum_2, 0, 1, 'L')
    else:
        pdf.set_font('Waree', '', 15)
        pdf.cell(0, 8, sum_1, 0, 1, 'L')

    pdf.set_font('Waree', '', 15)
    pdf.cell(0, 10, end_txt, 0, 1, 'C')
    pdf.cell(0, 15, end_txt, 0, 1, 'C')
    file_name = f"d:/ZEVS/checks/{id_}_{now}_{table_id}.pdf"
    pdf.output(file_name)
    os.startfile(file_name, 'print')


def get_date_time():
    now = datetime.datetime.now()
    full_date = now.strftime("%Y-%m-%d_%H-%M")
    date = now.strftime("%Y-%m-%d")
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    hour = now.strftime('%H-%M')
    return {'full_date': full_date, 'date': date,
            'year': year, 'month': month, 'day': day, 'hour': hour}


def number_format(number):
    if len(number) % 3 == 1:
        number = "  " + number
    elif len(number) % 3 == 2:
        number = " " + number
    num = [number[i:i + 3] for i in range(0, len(number), 3)]
    text = ' '.join(num) + ' UZS'
    return text


def get_product(db, product_id):
    response = db.product_db.select_by_type('product_id', product_id).fetchall()
    try:
        p = response[0]
    except IndexError:
        return Product()
    else:
        return Product(*p)


def get_products(db, menu_type):
    response = db.product_db.select_by_type('p_type', menu_type).fetchall()
    product = []
    for i in response:
        product.append(Product(*i))
    return product


class User:
    def __init__(self, login='', password='', name='', validate=''):
        self.name = name
        self.login = login
        self.password = password
        self.validate = validate


class Settings:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class Product:
    # product_id name p_type about price
    def __init__(self, product_id=0, name='None',
                 p_type='NOne', about='None', price='None'):
        self.product_id = product_id
        self.name = name
        self.p_type = p_type
        self.about = about
        self.price = price
