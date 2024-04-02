from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Database connection configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="f1racing"
)

@app.route('/')
def index():
    # Retrieve data from database
    cursor = db.cursor()
    cursor.execute("SELECT Name FROM driver")
    drivers = cursor.fetchall()
    cursor.close()
    return render_template('index.html', drivers=drivers)

if __name__ == '__main__':
    app.run(debug=True)
