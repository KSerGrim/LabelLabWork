import psycopg2.pool
import json
from datetime import date

db_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1, maxconn=10,
    dbname="shit",
    user="postgres",
    password="admin",
    host="localhost",
    port="5432",
)


def fetch_all():
    connection = db_pool.getconn()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM customers")
        users = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print(error)
        users = None
    finally:
        db_pool.putconn(connection)
    return users[0] if users else None


def fetch_user_bal(user):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    try:
        command = """
        SELECT balance FROM customers
        WHERE email = %s;
        """
        cursor.execute(command, (user,))
        balance = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print(error)
        balance = [[0]]
    finally:
        db_pool.putconn(connection)
    return balance[0][0] if balance else 0


def set_user_bal(user, bal):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    success = True
    try:
        command = f"""
            UPDATE customers
            SET balance = %s
            WHERE email = %s;
        """
        cursor.execute(command, (bal, user))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        success = False
    finally:
        db_pool.putconn(connection)
    return success


def fetch_user_overall(user):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    try:
        command = """
            SELECT total_deposited FROM customers
            WHERE email = %s;
            """
        cursor.execute(command, (user,))
        balance = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print(error)
        balance = [[0]]
    finally:
        db_pool.putconn(connection)
    return balance[0][0] if balance else 0


def add_to_user_overall(user, amount):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    amount += fetch_user_overall(user) if fetch_user_overall(user) else 0
    success = True
    try:
        command = f"""
                UPDATE customers
                SET total_deposited = %s
                WHERE email = %s;
            """
        cursor.execute(command, (amount, user))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        success = False
    finally:
        db_pool.putconn(connection)
    return success


def fetch_user_orders(user, orderid=None):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    try:
        command = """
        SELECT orders FROM customers
        WHERE email = %s"""
        cursor.execute(command, (user,))
        orders = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print(error)
        orders = [[{}]]
    finally:
        db_pool.putconn(connection)
    if orderid:
        return orders[0][0].get(orderid, None) if orders else None
    return orders[0][0] if orders else None


def add_user_order(order_json, order_id, user):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    success = True
    try:
        cursor.execute("SELECT orders FROM customers WHERE email = %s;", (user,))
        existing_orders_json = cursor.fetchone()[0]
        existing_orders_json[order_id] = order_json
        command = f"""
                UPDATE customers
                SET orders = %s::jsonb
                WHERE email = %s;
            """
        cursor.execute(command, (json.dumps(existing_orders_json), user))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        success = False
    finally:
        db_pool.putconn(connection)
    return success


def fetch_user(user_email):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    try:
        command = """SELECT * FROM customers
        WHERE email = %s;
        """
        cursor.execute(command, (user_email,))
        users = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print(error)
        users = None
    finally:
        db_pool.putconn(connection)
    return users


def add_user(email, name, user_id, password):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    success = True
    try:
        command = f"""
                    INSERT INTO customers (email, name, userid, password, balance, orders)
                    VALUES (%s, %s, %s, %s, %s, %s::json);
                """
        cursor.execute(command, (email, name, user_id, password, 0, json.dumps({})))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        success = False
    finally:
        db_pool.putconn(connection)
    return success


def remove_user(email):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    success = True
    try:
        command = f"""
                DELETE FROM customers
                WHERE email = %s;
            """
        cursor.execute(command, (email,))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        success = False
    finally:
        db_pool.putconn(connection)
    return success


def set_plug_type(plug):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    success = True
    try:
        command = f"""
                UPDATE admin
                SET current_plug = %s;
            """
        cursor.execute(command, (plug,))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        success = False
    finally:
        db_pool.putconn(connection)
    return success


def get_plug():
    connection = db_pool.getconn()
    cursor = connection.cursor()
    try:
        command = """
                SELECT current_plug FROM admin;"""
        cursor.execute(command)
        plug = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print(error)
        plug = [('',)]
    finally:
        db_pool.putconn(connection)
    return plug[0][0]


def get_all_plugs():
    connection = db_pool.getconn()
    cursor = connection.cursor()
    try:
        command = """
            SELECT available_plugs FROM admin"""
        cursor.execute(command)
        plugs = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print(error)
        plugs = [[{}]]
    finally:
        db_pool.putconn(connection)
    return plugs[0][0] if plugs else None


def add_new_plug(plug):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    success = True
    try:
        cursor.execute("SELECT available_plugs FROM admin;")
        existing_plugs = cursor.fetchone()[0]
        if not existing_plugs:
            existing_plugs = {'plugs': []}
        if plug not in existing_plugs['plugs']:
            existing_plugs['plugs'].append(plug)
        command = f"""
                    UPDATE admin
                    SET available_plugs = %s::jsonb;
                """
        cursor.execute(command, (json.dumps(existing_plugs),))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        success = False
    finally:
        db_pool.putconn(connection)
    return success


def remove_plug(plug):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    success = True
    try:
        cursor.execute("SELECT available_plugs FROM admin;")
        existing_plugs = cursor.fetchone()[0]
        if not existing_plugs:
            existing_plugs = {'plugs': []}
        if plug in existing_plugs['plugs']:
            existing_plugs['plugs'].pop(existing_plugs['plugs'].index(plug))
        command = f"""
                        UPDATE admin
                        SET available_plugs = %s::jsonb;
                    """
        cursor.execute(command, (json.dumps(existing_plugs),))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        success = False
    finally:
        db_pool.putconn(connection)
    return success


def get_all_sales():
    connection = db_pool.getconn()
    cursor = connection.cursor()
    try:
        command = """
                SELECT all_sales FROM admin"""
        cursor.execute(command)
        sales = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print(error)
        sales = [[{}]]
    finally:
        db_pool.putconn(connection)
    return sales[0][0] if sales else None


def set_price_per(price):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    success = True
    try:
        command = f"""
                    UPDATE admin
                    SET current_price = %s;
                """
        cursor.execute(command, (price,))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        success = False
    finally:
        db_pool.putconn(connection)
    return success


def get_price_per():
    connection = db_pool.getconn()
    cursor = connection.cursor()
    try:
        command = """
                    SELECT current_price FROM admin;"""
        cursor.execute(command)
        price = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print(error)
        price = [(250,)]
    finally:
        db_pool.putconn(connection)
    return price[0][0]


def add_sale_daily(sale, day):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    success = True
    try:
        cursor.execute("SELECT all_sales FROM admin;")
        all_sales = cursor.fetchone()[0]
        if not all_sales:
            all_sales = {day: sale}
        if not all_sales.get(day):
            all_sales[day] = 0
        all_sales[day] += sale
        command = f"""
                        UPDATE admin
                        SET all_sales = %s::jsonb;
                    """
        cursor.execute(command, (json.dumps(all_sales),))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        success = False
    finally:
        db_pool.putconn(connection)
    return success


def change_user_password(user, password):
    connection = db_pool.getconn()
    cursor = connection.cursor()
    success = True
    try:
        command = f"""
                UPDATE customers
                SET password = %s
                WHERE email = %s;
            """
        cursor.execute(command, (password, user))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        success = False
    finally:
        db_pool.putconn(connection)
    return success


if __name__ == "__main__":
    print(get_all_plugs())
    #add_new_plug('Shipd')
    #print(get_all_plugs())
    #print(fetch_user_orders('adminemail'))
    #print(fetch_user_orders('poohead@d.com'))
    #print(fetch_user_bal('poohead@d.com'))
    #print(fetch_user_overall('poohead@d.com'))
    #set_user_bal('poohead@d.com', 2000)
    #add_user('adminemail', 'admin','adminemail', 'adminpassword')
    #print(fetch_user('adminemail'))
    #print(fetch_all())
    #print(get_all_plugs())
    #print(get_plug())
    #print(get_price_per())
    #set_price_per(200)
    #print(get_price_per())
    #print(get_all_sales())
    #add_sale_daily(10, str(date.today()))
    #print(get_all_sales())


    #set_plug_type('Cheaplabels')
    #print(get_plug())

    #remove_plug('Cheaplabels')
    #print(add_new_plug('Cheaplabels'))
    #print(get_all_plugs())
    #set_user_bal('poohead@d.com', 1000)
    #add_to_user_overall('poohead@d.com', 1000)
    #print(fetch_user_overall('poohead@d.com'))
    #set_user_bal('poohead@d.com', 100)
    #print(fetch_user_overall('poohead@d.com'))
    #set_user_bal('poohead@d.com', 1000)
    #add_to_user_overall('poohead@d.com', 1000)
    #print(fetch_user_overall('poohead@d.com'))
    # print(fetch_all())
    # print(fetch_user('johndoe@example.com'))
    # print(fetch_user_bal('johndoe@example.com'))
    # print(set_user_bal('johndoe@example.com', 200))
    # print(fetch_user_orders('johndoe@example.com', orderid='order1'))
    # print(fetch_user_orders('johndoe@example.com'))
    # print(add_user_order({'product' : 'whatever'}, 'orderawdawd', 'johndoe@example.com'))
    # print(fetch_user('johndoe@example.com'))
    # print(fetch_user_orders('johndoe@example.com'))
    # print(add_user('poohead@d.com', 'poo D head', 'poohead@d.com', 'fakepassword'))
    # print(fetch_all())
    # add_user_order({'tracking': 333}, 'newordind1', 'poohead@d.com')
    # print(fetch_user('poohead@d.com'))
    # print(remove_user('poohead@d.com'))
    # print(remove_user('aaaaaa'))
    # print(fetch_user('poorhead@d.com'))
    # print(add_user('poohead@d.com', 'poo D head', 'poohead@d.com'))
    # print(fetch_user('poohead@d.com'))
