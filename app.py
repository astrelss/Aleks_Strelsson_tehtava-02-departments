from flask import Flask, render_template, request, redirect, url_for
from db import connect

app = Flask(__name__)


# erillinen funktio käyttäjien noutamiselle tietokannasta,
# koska tarvitaan useammassa paikassa
def _get_users(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT users.id, users.name, users.email, departments.name FROM users INNER JOIN departments ON departments.id = users.department_id")
    _users = cur.fetchall()
    return _users


def _get_departments(conn):
    cur = conn.cursor()
    cur.execute('SELECT * FROM departments')
    _departments = cur.fetchall()
    cur.close()
    return _departments


# etusivu
@app.route('/')
def index():
    return render_template('index.html')


# tähän tullaan, kun formiseta painetaan, Delete-nappia
@app.route('/users', methods=['POST'])
def delete_user():
    # request.form-sisältää tiedot, jotka formilla lähetetään palvelimelle
    _body = request.form
    with connect() as connection:
        try:
            # haetaan userid form datasta
            # userid on formin hidden-inputin name-attribuutin arvo
            userid = _body.get('userid')
            if userid is None:
                raise Exception('missing userid')

            # jos tämä epäonnistuu, tulee ValueError
            userid = int(userid)
            cursor = connection.cursor()
            # jos kaikki onnistuu,
            # poistetaan valittu käyttäjä tietokannasta
            # ja ladataan sivu kokonaan uudelleen
            cursor.execute('DELETE FROM users WHERE id = ?', (userid,))
            connection.commit()
            cursor.close()
            return redirect(url_for('get_users'))

        # valueError-exception tulee silloin
        # jos userid-kenttä ei sisällä numeerista arvoa
        # (ei voida muuttaa kentän arvoa integeriksi)
        except ValueError as e:

            connection.rollback()
            # haetaan käyttäjät ja ladataan sivu uudelleen
            _users = _get_users(connection)
            return render_template('users/index.html', error=str(e), users=_users)

        except Exception as e:
            # haetaan käyttäjät ja ladataan sivu uudelleen
            _users = _get_users(connection)
            connection.rollback()
            return render_template('users/index.html', error=str(e), users=_users)


# GET-metodilla haetaan käyttäjät tietokannasta ja palautetaan selaimelle valmis sivu
# jossa käyttäjät listattuna
@app.route('/users', methods=['GET'])
def get_users():
    with connect() as con:
        _users = _get_users(con)

        return render_template('users/index.html', users=_users, error=None)


# GET-metodilla ladataan uuden käyttäjän listäystä varten tehty sivu

@app.route('/users/new', methods=['GET'])
def new_user():
    with connect() as con:
        _departments = _get_departments(con)
        return render_template('users/new.html', departments=_departments, error=None)


# POST-metodilla lisätään käyttäjän tiedot lomakkeelta tietokantaan

@app.route('/users/new', methods=['POST'])
def add_user():
    _body = request.form
    with connect() as con:

        try:
            cur = con.cursor()
            cur.execute('INSERT INTO users (name, email, department_id) VALUES (?, ?, ?)',
                        (_body.get('name'), _body.get('email'), _body.get('department_id')))
            con.commit()
            return redirect(url_for('get_users'))
        except Exception as e:
            con.rollback()
            _departments = _get_departments(con)
            return render_template('users/new.html', error=str(e), departments=_departments)


if __name__ == '__main__':
    app.run(port=4000)
