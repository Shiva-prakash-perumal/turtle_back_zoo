from flask import Flask, render_template,request,redirect,url_for,flash
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Dbmsdb1998'
app.config['MYSQL_DB'] = 'turtlezoo'

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

@app.route('/d_attraction', methods=['GET', 'POST'])
def d_attractions():
    if request.method == 'POST':
        date = request.form['date']
        return redirect(url_for('d_attractions', date=date))

    date = request.args.get('date')

    if date:
        cur = mysql.connection.cursor()

        # Query to get revenue for each showing of each revenue type for the specified date
        cur.execute('''
            SELECT
                re.id AS revenue_type_id,
                re.name AS revenue_type_name,
                DATE(rev.date_time) AS showing_date,
                rev.tickets_sold AS attendance,
                CASE
                    WHEN rev.adult_tickets > 0 THEN rev.adult_price * rev.adult_tickets
                    WHEN rev.child_tickets > 0 THEN rev.child_price * rev.child_tickets
                    WHEN rev.senior_tickets > 0 THEN rev.senior_price * rev.senior_tickets
                    ELSE 0
                END AS total_revenue
            FROM
                revenue_types re
            JOIN
                revenue_event rev ON re.id = rev.r_id
            WHERE
                DATE(rev.date_time) = %s
            ORDER BY
                re.id, DATE(rev.date_time)
        ''', (date,))

        results = cur.fetchall()
        cur.close()

        return render_template('view_d_attracrion_revenue.html', results=results, selected_date=date)

    return render_template('d_attractions.html')

@app.route('/d_concessions')
def d_concessions():
    if request.method == 'POST':
        date = request.form['date']

        # Execute the SQL query
        cur = mysql.connection.cursor()
        query = (
            "SELECT re.id AS revenue_type_id, re.name AS revenue_type_name, re.type, "
            "DATE(rv.date_time), rv.revenue, rv.tickets_sold "
            "FROM revenue_types re "
            "JOIN revenue_event rv ON re.id = rv.r_id "
            "WHERE re.type = 'Conc' AND DATE(rv.date_time) = %s"
        )
        cur.execute(query, (date,))
        result = cur.fetchall()
        cur.close()

        return render_template('daily_revenue_result.html', result=result)

    return render_template('daily_revenue_form.html')

@app.route('/d_attendance')
def d_attendance():
    if request.method == 'POST':
        specific_date = request.form['specific_date']

        # Execute the SQL query
        cur = mysql.connection.cursor()
        query = (
            "SELECT DATE(rv.date_time) AS specific_date, SUM(rv.tickets_sold) AS total_tickets_sold "
            "FROM revenue_event rv "
            "WHERE DATE(rv.date_time) = %s "
            "GROUP BY DATE(rv.date_time)"
        )
        cur.execute(query, (specific_date,))
        result = cur.fetchall()
        cur.close()

        return render_template('tickets_sold_for_date.html', result=result)

    return render_template('tickets_sold_for_date.html', result=None)


@app.route('/management_and_reporting')
def management_and_reporting():
    return "Management and Reporting Page"

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

            print(f"Form Data: id={id}, status={status}, birthyear={birthyear}, s_id={s_id}, b_id={b_id}, enclo_id={enclo_id}")

            cur = mysql.connection.cursor()
            query = "INSERT INTO animal (id, status, birthyear, s_id, b_id, enclo_id) VALUES (%s, %s, %s, %s, %s, %s)"
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

@app.route('/animals/update/<int:animal_id>', methods=['GET', 'POST'])
def update_animal(animal_id):
    if request.method == 'POST':
        status = request.form['status']
        birthyear = request.form['birthyear']
        s_id = request.form['s_id']
        b_id = request.form['b_id']
        enclo_id = request.form['enclo_id']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE animal SET status=%s, birthyear=%s, s_id=%s, b_id=%s, enclo_id=%s WHERE id=%s",
                    (status, birthyear, s_id, b_id, enclo_id, animal_id))
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
    cur.execute("SELECT id, sqft FROM enclosure")
    enclosures = cur.fetchall()
    cur.close()

    return render_template('update_animal.html', animal=animal, species=species, buildings=buildings, enclosures=enclosures)

@app.route('/employees')
def employees():
    return render_template('employees.html')

@app.route('/employees')
def view_employees():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employee")
    employees = cur.fetchall()
    cur.close()
    return render_template('view_employees.html', employees=employees)

@app.route('/insert_employee', methods=['GET', 'POST'])
def insert_employee():
    if request.method == 'POST':
        # Extract data from the form
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

        # Insert data into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO employee (h_id, super_id, job_type, start_date, r_id, "
                    "f_name, m_name, l_name, street, city, state, zip) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (h_id, super_id, job_type, start_date, r_id, f_name, m_name, l_name, street, city, state, zip_code))
        mysql.connection.commit()
        cur.close()

        flash('Employee inserted successfully', 'success')
        return redirect(url_for('view_employees'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, super_id FROM employee")
    supervisor = cur.fetchall()
    cur.execute("SELECT id, rate FROM hourly_rate")
    hourly_rate = cur.fetchall()
    print(hourly_rate)
    cur.execute("SELECT id, name FROM revenue_types")
    revenue_type = cur.fetchall()
    cur.close()

    return render_template('insert_employee.html', supervisors=supervisor , revenue_types=revenue_type, hourly_rates=hourly_rate)

@app.route('/update_employee/<int:employee_id>', methods=['GET', 'POST'])
def update_employee(employee_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employee WHERE id = %s", (employee_id,))
    employee = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        # Extract updated data from the form
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

        # Update data in the database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE employee SET h_id=%s, super_id=%s, job_type=%s, start_date=%s, r_id=%s, "
                    "f_name=%s, m_name=%s, l_name=%s, street=%s, city=%s, state=%s, zip=%s WHERE id=%s",
                    (h_id, super_id, job_type, start_date, r_id, f_name, m_name, l_name, street, city, state, zip_code, employee_id))
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

@app.route('/update_building/<int:building_id>', methods=['GET', 'POST'])
def update_building(building_id):
    # cur = mysql.connection.cursor()
    #
    # # Fetch the building data for the specified ID
    # cur.execute("SELECT * FROM building WHERE id = %s", (building_id,))
    # building_data = cur.fetchone()
    #
    # # Fetch the list of building IDs
    # cur.execute("SELECT id FROM building")
    # building_ids = [result[0] for result in cur.fetchall()]  # Accessing the first element of each tuple

    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE building SET name=%s, type=%s WHERE id=%s", (name, type, building_id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('view_buildings'))

    # cur.close()

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
        # Extract data from the form
        name = request.form['name']
        type = request.form['type']
        b_id = request.form['b_id']
        adult_price = request.form['adult_price']
        child_price = request.form['child_price']
        senior_price = request.form['senior_price']
        perday = request.form['perday']
        product = request.form['product']

        # Insert data into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO revenue_types (name, type, b_id, adult_price, child_price, senior_price, perday, product) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (name, type, b_id, adult_price, child_price, senior_price, perday, product))
        mysql.connection.commit()
        cur.close()

        flash('Revenue type inserted successfully', 'success')
        return redirect(url_for('view_revenue_types'))

    return render_template('insert_revenue_type.html')

@app.route('/update_revenue_type/<int:revenue_type_id>', methods=['GET', 'POST'])
def update_revenue_type(revenue_type_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM revenue_types WHERE id = %s", (revenue_type_id,))
    revenue_type = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        # Extract updated data from the form
        name = request.form['name']
        type = request.form['type']
        b_id = request.form['b_id']
        adult_price = request.form['adult_price']
        child_price = request.form['child_price']
        senior_price = request.form['senior_price']
        perday = request.form['perday']
        product = request.form['product']

        # Update data in the database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE revenue_types SET name=%s, type=%s, b_id=%s, adult_price=%s, child_price=%s, senior_price=%s, "
                    "perday=%s, product=%s WHERE id=%s",
                    (name, type, b_id, adult_price, child_price, senior_price, perday, product, revenue_type_id))
        mysql.connection.commit()
        cur.close()

        flash('Revenue type updated successfully', 'success')
        return redirect(url_for('view_revenue_types'))

    return render_template('update_revenue_type.html', revenue_type=revenue_type)


@app.route('/employee_hourly_rate')
def employee_hourly_rate():
    return  render_template('hourly_rate.html')

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
        # Extract data from the form
        rate = request.form['rate']
        id = request.form['id']

        # Insert data into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO hourly_rate (id, rate) VALUES (%s, %s)", (id, rate))
        mysql.connection.commit()
        cur.close()

        flash('Hourly rate inserted successfully', 'success')
        return redirect(url_for('view_hourly_rate'))

    return render_template('insert_hourly_rate.html')

@app.route('/update_hourly_rate/<int:hourly_rate_id>', methods=['GET', 'POST'])
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
    app.run(debug=True)