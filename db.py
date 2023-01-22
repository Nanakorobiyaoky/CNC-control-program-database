import pymysql

from config_loader import connection_parameters

table = connection_parameters['table']


def open_connection():
    connection = pymysql.connect(
        host=connection_parameters['host'],
        port=connection_parameters['port'],
        user=connection_parameters['user'],
        password=connection_parameters['password'],
        database=connection_parameters['database'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def get_last_program():
    try:
        connection = open_connection()

        with connection.cursor() as cursor:
            sql = "SELECT * FROM programs order by id desc limit 1"
            cursor.execute(sql)
            result = cursor.fetchone()
            try:
                return result['Номер программы']
            except:
                return 'A0000'

    except Exception as e:
        raise

    finally:
        connection.close()


def generate(p_num):
    letter = p_num[0]
    nums = int(p_num[1:])
    if nums == 9999:
        nums = 0
        letter = chr(ord(letter) + 1)
    return letter + str(nums + 1).rjust(4, '0')


def get_all_data():
    try:
        connection = open_connection()

        with connection.cursor() as cursor:
            sql = "SELECT * FROM programs"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    except:
        raise

    finally:
        connection.close()


def get_columns():
    try:
        connection = open_connection()

        with connection.cursor() as cursor:
            sql = "SHOW COLUMNS FROM programs"
            cursor.execute(sql)
            result = cursor.fetchall()
            return [i['Field'] for i in result if i['Field'] != 'id']

    except:
        raise

    finally:
        connection.close()


def add_new_row(request_dict):
    try:
        connection = open_connection()

        q = [
            request_dict['Инженер'],
            request_dict['Шифр детали'],
            request_dict['Станок'],
            request_dict['Тип операции'],
            request_dict['Номер операции'],
            request_dict['Примечание'],
            generate(get_last_program())
        ]

        with connection.cursor() as cursor:
            sql = "insert into programs " \
                  "(`Инженер`, `Шифр детали`, `Станок`, `Тип операции`, `Номер операции`, `Примечание`, `Номер программы`) " \
                  "values (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, q)
            connection.commit()

    except:
        raise

    finally:
        connection.close()


def get_one_row(program_number):
    try:
        connection = open_connection()

        with connection.cursor() as cursor:
            sql = "SELECT * FROM programs where `Номер программы` = %s"
            cursor.execute(sql, program_number)
            result = cursor.fetchone()
            return result

    except:
        raise

    finally:
        connection.close()


def change_data_in_cell(k, v, p_num):
    try:
        connection = open_connection()

        with connection.cursor() as cursor:
            sql = f"update programs set `{k}` = '{v}' where `Номер программы` = '{p_num}'"
            cursor.execute(sql)
            connection.commit()

    except:
        raise

    finally:
        connection.close()


def custom_selection(dct):
    sql = f"select * from programs where "
    a = []
    for k, v in dct.items():
        a.append(f"`{k}` like '%{v}%'")

    sql += ' and '.join(a)

    try:
        connection = open_connection()

        with connection.cursor() as cursor:
            cursor.execute(sql)

        result = cursor.fetchall()
        return result

    except:
        raise

    finally:
        connection.close()
