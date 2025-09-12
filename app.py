from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

# ✅ Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",          # your MySQL user
        password="Aditimy@16",   # your MySQL password
        database="agritwo"     # your DB name (create with your schema)
    )
    return conn

# ✅ Serve frontend
@app.route('/')
def index():
    return render_template("index.html")

# ✅ API: Add Farmer
@app.route('/add_farmer', methods=['POST'])
def add_farmer():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """INSERT INTO Farmers (name, location, language, field_size, contact_info) 
             VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(sql, (data['name'], data['location'], data['language'], data['field_size'], data['contact']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Farmer added successfully"})

# ✅ API: Get Farmers
@app.route('/get_farmers', methods=['GET'])
def get_farmers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Farmers")
    farmers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(farmers)

# ✅ API: Add Crop Type
@app.route('/add_crop', methods=['POST'])
def add_crop():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO CropTypes (name, category) VALUES (%s, %s)"
    cursor.execute(sql, (data['name'], data['category']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Crop added successfully"})

# ✅ API: Get Crops
@app.route('/get_crops', methods=['GET'])
def get_crops():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CropTypes")
    crops = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(crops)

if __name__ == '__main__':
    app.run(debug=True)
