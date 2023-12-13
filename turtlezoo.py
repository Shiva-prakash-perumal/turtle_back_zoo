from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Dbmsdb1998'
app.config['MYSQL_DB'] = 'turtleback_zoo'

mysql = MySQL(app)


@app.route('/')
def landing_page():
    return render_template('landing_page.html')


@app.route('/asset_management')
def asset_management():
    return render_template('asset_management.html')


@app.route('/daily_zoo_activity')
def daily_zoo_activity():
    return render_template('daily_zoo.html')


def execute_query(query, params=None):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


@app.route('/d_attraction', methods=['GET', 'POST'])
def d_attractions():
    if request.method == 'POST':
        date = request.form['date']
        return redirect(url_for('d_attractions', date=date))

    date = request.args.get('date')

    if date:
        print(date)  # Move the print statement here
        cur = mysql.connection.cursor()
        cur.execute("SELECT re.name AS Attraction_name, rev.date_time AS show_date_time, "
                    "rev.tickets_sold AS attendance, rev.revenue AS Revenue "
                    "FROM revenue_types re "
                    "JOIN revenue_event rev ON re.id = rev.r_id "
                    "WHERE re.type = 'AS' AND DATE(rev.date_time) = DATE(%s) "
                    "ORDER BY DATE(rev.date_time)", (date,))
        results = cur.fetchall()
        print(results)
        cur.close()

        return render_template('view_d_attracrion_revenue.html', results=results, selected_date=date)

    return render_template('d_attractions.html')

@app.route('/d_concessions', methods=['GET', 'POST'])
def d_concessions():
    if request.method == 'POST':
        date = request.form['date']

        cur = mysql.connection.cursor()
        query = (
            "SELECT re.name AS revenue_type_name, re.type as type, "
            "rv.date_time AS Date, rv.revenue as revenue, rv.tickets_sold as Tickets_Sold "
            "FROM revenue_types re "
            "JOIN revenue_event rv ON re.id = rv.r_id "
            "WHERE re.type = 'Conc' AND DATE(rv.date_time) = DATE(%s)"
        )
        cur.execute(query, (date,))
        result = cur.fetchall()
        cur.close()

        return render_template('daily_revenue_result.html', result=result)

    return render_template('daily_revenue_form.html')


@app.route('/d_attendance', methods=['GET', 'POST'])
def d_attendance():
    if request.method == 'POST':
        specific_date = request.form['specific_date']

        cur = mysql.connection.cursor()
        query = (
            "SELECT DATE(rv.date_time) AS specific_date, SUM(rv.tickets_sold) AS total_tickets_sold "
            "FROM revenue_event rv "
            "WHERE DATE(rv.date_time) = DATE(%s) "
            "GROUP BY DATE(rv.date_time)"
        )
        cur.execute(query, (specific_date,))
        result = cur.fetchall()
        cur.close()

        return render_template('tickets_sold_for_date.html', result=result)

    return render_template('tickets_sold_for_date.html', result=None)


@app.route('/management_and_reporting')
def management_and_reporting():
    return render_template('mgmt.html')


@app.route('/revenue_report1', methods=['GET', 'POST'])
def revenue_report1():
    if request.method == 'POST':
        given_date = request.form['given_date']

        cur = mysql.connection.cursor()
        query = (
            "SELECT "
            "re.date_time as date_time, rt.name AS revenue_source, "
            "rt.type AS revenue_type, "
            "re.tickets_sold AS total_tickets_sold, "
            "re.revenue AS total_revenue "
            "FROM "
            "revenue_types rt "
            "JOIN "
            "revenue_event re ON rt.id = re.r_id "
            "WHERE "
            "DATE(re.date_time) = DATE(%s)"
        )

        cur.execute(query, (given_date,))
        results = cur.fetchall()
        print(results)
        cur.close()

        return render_template('revenue_report1.html', results=results)

    return render_template('revenue_report_form1.html')

@app.route('/revenue_report2')
def revenue_report2():

    cur = mysql.connection.cursor()
    query = (
        "SELECT "
        "s.name AS species_name, "
        "COUNT(a.id) AS total_population, "
        "s.food_cost * COUNT(a.id) AS total_monthly_food_cost, "
        "a.status, "
        "COUNT(a.id) AS total_by_status, "
        "COUNT(DISTINCT e.id) * MAX(h.rate) * 160 AS total_veterinarian_cost, "
        "COUNT(DISTINCT f.id) * MAX(i.rate) * 160 AS total_care_specialist_cost "
        "FROM "
        "species s "
        "JOIN "
        "animal a ON s.id = a.s_id "
        "LEFT JOIN "
        "cares_for cf ON s.id = cf.s_id "
        "LEFT JOIN "
        "employee e ON cf.e_id = e.id AND e.job_type = 'Veterinarian' "
        "LEFT JOIN "
        "employee f ON cf.e_id = f.id AND f.job_type = 'Animal care specialist' "
        "LEFT JOIN "
        "hourly_rate h ON h.id = e.h_id "
        "LEFT JOIN "
        "hourly_rate i ON i.id = f.h_id "
        "GROUP BY "
        "s.id, a.status "
        "ORDER BY "
        "s.id, a.status;"
    )
    cur.execute(query)
    result = cur.fetchall()
    print(result)
    cur.close()

    return render_template('report2.html', result=result)


@app.route('/revenue_report3', methods=['GET', 'POST'])
def revenue_report3():
    if request.method == 'POST':
        try:
            cur = mysql.connection.cursor()

            begin_date = request.form['begin_date']
            end_date = request.form['end_date']

            query = (
                "SELECT "
                "rt.name AS attraction_name, "
                "SUM(re.revenue) AS total_revenue "
                "FROM "
                "revenue_types rt "
                "JOIN "
                "revenue_event re ON rt.id = re.r_id "
                "WHERE "
                "rt.type = 'AS' "
                "AND DATE(re.date_time) BETWEEN DATE(%s) AND DATE(%s) "
                "GROUP BY "
                "rt.name "
                "ORDER BY "
                "total_revenue DESC "
                "LIMIT 3;"
            )
            cur.execute(query,(begin_date,end_date,))
            results = cur.fetchall()

            return render_template('revenue_report3.html', results=results)

        except Exception as e:
            print(f"Error: {e}")
            return render_template('error.html', error_message=str(e))

        finally:
            cur.close()

    return render_template('revenue_report3_form.html')

@app.route('/revenue_report4', methods=['GET', 'POST'])
def revenue_report4():
    if request.method == 'POST':
        selected_month = int(request.form['month'])
        selected_year = int(request.form['year'])
        cur = mysql.connection.cursor()
        query = (
            "SELECT "
            "DATE(date_time) AS revenue_date, "
            "SUM(revenue) AS total_revenue "
            "FROM "
            "revenue_event "
            "WHERE "
            "MONTH(date_time) = %s AND YEAR(date_time) = %s "
            "GROUP BY "
            "revenue_date "
            "ORDER BY "
            "total_revenue DESC "
            "LIMIT 5;"
        )

        params = (selected_month, selected_year)
        cur.execute(query, params)
        result = cur.fetchall()
        print(result)

        return render_template('revenue_report4_result.html', result=result)

    return render_template('revenue_report4.html')


@app.route('/revenue_report5', methods=['GET'])
def revenue_report5():
    return render_template('revenue_report5_form.html')


@app.route('/revenue_report5_result', methods=['POST'])
def revenue_report5_result():
    begin_date = request.form['begin_date']
    end_date = request.form['end_date']
    cur = mysql.connection.cursor()
    query = (
        "SELECT "
        "rt.type, "
        "AVG(re.revenue) AS average_revenue "
        "FROM "
        "revenue_event re "
        "JOIN "
        "revenue_types rt ON re.r_id = rt.id "
        "WHERE "
        "DATE(re.date_time) BETWEEN DATE(%s) AND DATE(%s) "
        "AND rt.type IN ('AS', 'Conc', 'ZA') "
        "GROUP BY "
        "rt.type;"
    )


    params = (begin_date, end_date)
    cur.execute(query, params)
    result = cur.fetchall()

    return render_template('revenue_report5_result.html', result=result)


@app.route("/animals")
def main_page():
    return render_template('index.html')


@app.route('/view_animals')
def view_animals():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM animal")
    animals = cur.fetchall()
    cur.close()
    return render_template('view_animals.html', animals=animals)


@app.route('/animals/insert', methods=['GET', 'POST'])
def insert_animal():
    if request.method == 'POST':
        try:
            id = request.form.get('id')
            status = request.form.get('status')
            birthyear = request.form.get('birthyear')
            s_id = request.form.get('s_id')
            b_id = request.form.get('b_id')
            enclo_id = request.form.get('enclo_id')

            print(
                f"Form Data: id={id}, status={status}, birth_year={birthyear}, s_id={s_id}, b_id={b_id}, enclo_id={enclo_id}")

            cur = mysql.connection.cursor()
            query = "INSERT INTO animal (id, status, birth_year, s_id, b_id, enclo_id) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (id, status, birthyear, s_id, b_id, enclo_id)
            print(f"Executing query: {query}, Data: {data}")
            cur.execute(query, data)
            mysql.connection.commit()
            cur.close()

            print("Data inserted successfully")

            return redirect(url_for('view_animals'))
        except Exception as e:
            print(f"Error: {e}")
            mysql.connection.rollback()

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM species")
    species = cur.fetchall()
    cur.execute("SELECT id, name FROM building")
    buildings = cur.fetchall()
    cur.execute("SELECT id, sqft FROM enclosure")
    enclosures = cur.fetchall()
    cur.close()

    return render_template('insert_animals.html', species=species, buildings=buildings, enclosures=enclosures)


@app.route('/animals/update/<string:animal_id>', methods=['GET', 'POST'])
def update_animal(animal_id):
    if request.method == 'POST':
        status = request.form['status']
        birthyear = request.form['birthyear']
        s_id = request.form['s_id']
        b_id = request.form['b_id']
        # enclo_id = request.form['enclo_id']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE animal SET status=%s, birth_year=%s, s_id=%s, b_id=%s WHERE id=%s",
                    (status, birthyear, s_id, b_id, animal_id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('view_animals'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM animal WHERE id=%s", (animal_id,))
    animal = cur.fetchone()

    cur.execute("SELECT id, name FROM species")
    species = cur.fetchall()
    cur.execute("SELECT id, name FROM building")
    buildings = cur.fetchall()
    # cur.execute("SELECT id, sqft FROM enclosure")
    # enclosures = cur.fetchall()
    cur.close()

    return render_template('update_animal.html', animal=animal, species=species, buildings=buildings,
                           )# enclosures=enclosures)

@app.route('/employees')
def employees():
    return render_template('employees.html')


@app.route('/view_employees')
def view_employees():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employee")
    employees = cur.fetchall()
    cur.close()
    return render_template('view_employees.html', employees=employees)


@app.route('/insert_employee', methods=['GET', 'POST'])
def insert_employee():
    if request.method == 'POST':
        id = request.form['id']
        h_id = request.form['h_id']
        super_id = request.form['supervisor_id']
        job_type = request.form['job_type']
        start_date = request.form['start_date']
        r_id = request.form['revenue_type_id']
        f_name = request.form['f_name']
        m_name = request.form['m_name']
        l_name = request.form['l_name']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO employee (id, h_id, super_id, job_type, start_date, r_id, "
                    "f_name, m_name, l_name, street, city, state, zip) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (id, h_id, super_id, job_type, start_date, r_id, f_name, m_name, l_name, street, city, state, zip_code))
        mysql.connection.commit()
        cur.close()

        flash('Employee inserted successfully', 'success')
        return redirect(url_for('view_employees'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, super_id FROM employee")
    supervisor = cur.fetchall()
    cur.execute("SELECT id, id FROM hourly_rate")
    hourly_rate = cur.fetchall()
    print(hourly_rate)
    cur.execute("SELECT id, name FROM revenue_types")
    revenue_type = cur.fetchall()
    cur.close()

    return render_template('insert_employee.html', supervisors=supervisor, revenue_types=revenue_type,
                           hourly_rates=hourly_rate)


@app.route('/update_employee/<string:employee_id>', methods=['GET', 'POST'])
def update_employee(employee_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employee WHERE id = %s", (employee_id,))
    employee = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        h_id = request.form['h_id']
        super_id = request.form['super_id']
        job_type = request.form['job_type']
        start_date = request.form['start_date']
        r_id = request.form['r_id']
        f_name = request.form['f_name']
        m_name = request.form['m_name']
        l_name = request.form['l_name']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip']

        cur = mysql.connection.cursor()

        cur.execute("UPDATE employee SET h_id=%s, super_id=%s, job_type=%s, start_date=%s, r_id=%s, "
                    "f_name=%s, m_name=%s, l_name=%s, street=%s, city=%s, state=%s, zip=%s WHERE id=%s",
                    (h_id, super_id, job_type, start_date, r_id, f_name, m_name, l_name, street, city, state, zip_code,
                     employee_id))
        mysql.connection.commit()
        cur.close()

        flash('Employee updated successfully', 'success')
        return redirect(url_for('view_employees'))

    return render_template('update_employee.html', employee=employee)


@app.route('/buildings')
def buildings():
    return render_template('buildings.html')


@app.route('/insert_building', methods=['GET', 'POST'])
def insert_building():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        type = request.form['type']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO building (id, name, type) VALUES (%s, %s, %s)", (id, name, type))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('view_buildings'))

    return render_template('insert_building.html')


@app.route('/view_buildings')
def view_buildings():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM building")
    columns = [column[0] for column in cur.description]
    buildings = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()

    return render_template('view_buildings.html', buildings=buildings)


@app.route('/update_building/<string:building_id>', methods=['GET', 'POST'])
def update_building(building_id):

    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE building SET name=%s, type=%s WHERE id=%s", (name, type, building_id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('view_buildings'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM building WHERE id=%s", (building_id,))
    building = cur.fetchone()

    return render_template('update_building.html', building=building)


@app.route('/attractions')
def attractions():
    return render_template('attractions.html')


@app.route('/revenue_types')
def view_revenue_types():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM revenue_types")
    revenue_types = cur.fetchall()
    cur.close()
    return render_template('view_revenue_types.html', revenue_types=revenue_types)


@app.route('/insert_revenue_type', methods=['GET', 'POST'])
def insert_revenue_type():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        type = request.form['type']
        b_id = request.form['b_id']
        if 'null_adult_price' in request.form:
            adult_price = None  # Set to NULL
        else:
            adult_price = request.form['adult_price']
        if 'null_child_price' in request.form:
            child_price = None  # Set to NULL
        else:
            child_price = request.form['child_price']
        if 'null_senior_price' in request.form:
            senior_price = None  # Set to NULL
        else:
            senior_price = request.form['senior_price']
        if 'null_perday' in request.form:
            perday = None  # Set to NULL
        else:
            perday = request.form['perday']
        if 'null_product' in request.form:
            product = None  # Set to NULL
        else:
            product = request.form['product']

        # adult_price = request.form['adult_price']
        # child_price = request.form['child_price']
        # senior_price = request.form['senior_price']
        # perday = request.form['perday']
        # product = request.form['product']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO revenue_types (id, name, type, b_id, adult_price, child_price, senior_price, `#perday`, product) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (id ,name, type, b_id, adult_price, child_price, senior_price, perday, product))
        mysql.connection.commit()
        cur.close()

        flash('Revenue type inserted successfully', 'success')
        return redirect(url_for('view_revenue_types'))

    return render_template('insert_revenue_type.html')


@app.route('/update_revenue_type/<string:revenue_type_id>', methods=['GET', 'POST'])
def update_revenue_type(revenue_type_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM revenue_types WHERE id = %s", (revenue_type_id,))
    revenue_type = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        b_id = request.form['b_id']
        # adult_price = request.form['adult_price']
        if 'null_adult_price' in request.form:
            adult_price = None  # Set to NULL
        else:
            adult_price = request.form['adult_price']
        if 'null_child_price' in request.form:
            child_price = None  # Set to NULL
        else:
            child_price = request.form['child_price']
        if 'null_senior_price' in request.form:
            senior_price = None  # Set to NULL
        else:
            senior_price = request.form['senior_price']
        if 'null_perday' in request.form:
            perday = None  # Set to NULL
        else:
            perday = request.form['perday']
        if 'null_product' in request.form:
            product = None  # Set to NULL
        else:
            product = request.form['product']

        # child_price = request.form['child_price']
        # senior_price = request.form['senior_price']
        # perday = request.form['perday']
        # product = request.form['product']

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE revenue_types SET name=%s, type=%s, b_id=%s, adult_price=%s, child_price=%s, senior_price=%s, "
            "`#perday`=%s, product=%s WHERE id=%s",
            (name, type, b_id, adult_price, child_price, senior_price, perday, product, revenue_type_id))
        mysql.connection.commit()
        cur.close()

        flash('Revenue type updated successfully', 'success')
        return redirect(url_for('view_revenue_types'))

    return render_template('update_revenue_type.html', revenue_type=revenue_type)


@app.route('/employee_hourly_rate')
def employee_hourly_rate():
    return render_template('hourly_rate.html')


@app.route('/hourly_rate')
def view_hourly_rate():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM hourly_rate")
    hourly_rate = cur.fetchall()
    cur.close()
    return render_template('view_hourly_rate.html', hourly_rate=hourly_rate)


@app.route('/insert_hourly_rate', methods=['GET', 'POST'])
def insert_hourly_rate():
    if request.method == 'POST':
        rate = request.form['rate']
        id = request.form['id']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO hourly_rate (id, rate) VALUES (%s, %s)", (id, rate))
        mysql.connection.commit()
        cur.close()

        flash('Hourly rate inserted successfully', 'success')
        return redirect(url_for('view_hourly_rate'))

    return render_template('insert_hourly_rate.html')


@app.route('/update_hourly_rate/<string:hourly_rate_id>', methods=['GET', 'POST'])
def update_hourly_rate(hourly_rate_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM hourly_rate WHERE id = %s", (hourly_rate_id,))
    rate_data = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        rate = request.form['rate']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE hourly_rate SET rate=%s WHERE id=%s", (rate, hourly_rate_id))
        mysql.connection.commit()
        cur.close()

        flash('Hourly rate updated successfully', 'success')
        return redirect(url_for('view_hourly_rate'))

    return render_template('update_hourly_rate.html', rate_data=rate_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
