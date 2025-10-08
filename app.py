# from flask import Flask, render_template, request, jsonify
# import mysql.connector

# app = Flask(__name__)

# # Database connection
# def get_db_connection():
#     conn = mysql.connector.connect(
#         host="127.0.0.1",
#         user="root",          # your MySQL user
#         password="Aditimy@16",   # your MySQL password
#         database="agritwo"     # your DB name (create with your schema)
#     )
#     return conn

# #Serve frontend
# @app.route('/')
# def index():
#     return render_template("index.html")

# # API: Add Farmer
# @app.route('/add_farmer', methods=['POST'])
# def add_farmer():
#     data = request.json
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     sql = """INSERT INTO Farmers (name, location, language, field_size, contact_info) 
#              VALUES (%s, %s, %s, %s, %s)"""
#     cursor.execute(sql, (data['name'], data['location'], data['language'], data['field_size'], data['contact']))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return jsonify({"message": "Farmer added successfully"})

# # API: Get Farmers
# @app.route('/get_farmers', methods=['GET'])
# def get_farmers():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM Farmers")
#     farmers = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return jsonify(farmers)

# # API: Add Crop Type
# @app.route('/add_crop', methods=['POST'])
# def add_crop():
#     data = request.json
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     sql = "INSERT INTO CropTypes (name, category) VALUES (%s, %s)"
#     cursor.execute(sql, (data['name'], data['category']))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return jsonify({"message": "Crop added successfully"})

# # API: Get Crops
# @app.route('/get_crops', methods=['GET'])
# def get_crops():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM CropTypes")
#     crops = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return jsonify(crops)

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import mysql.connector

app = Flask(__name__, static_folder='public', static_url_path='')

# ------------------ File Upload Config ------------------
UPLOAD_SUBDIR = os.path.join('public', 'uploads')
UPLOAD_DIR = os.path.join(app.root_path, 'public', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def is_allowed_image_filename(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS

# ------------------ DB Connection ------------------
def get_db_connection():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",          # your MySQL user
        password="Aditimy@16",  # your MySQL password
        database="agritwo"    # your DB schema
    )
    return conn


# ------------------ Serve Frontend ------------------
@app.route('/')
def index():
    return render_template("index.html")


# ------------------ FARMERS ------------------
@app.route('/add_farmer', methods=['POST'])
def add_farmer():
    data = request.get_json(silent=True) or {}
    try:
        required = ['name', 'location', 'language', 'field_size', 'contact_info']
        for field in required:
            if field not in data or data[field] in (None, ""):
                return jsonify({"message": f"{field} is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO Farmers (name, location, language, field_size, contact_info) 
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (
            data['name'],
            data['location'],
            data['language'],
            data['field_size'],
            data['contact_info']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Farmer added successfully"})
    except Exception as e:
        return jsonify({"message": f"Error adding farmer: {str(e)}"}), 500


@app.route('/get_farmers', methods=['GET'])
def get_farmers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Farmers")
    farmers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(farmers)


# ------------------ CROPS ------------------
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


@app.route('/get_crops', methods=['GET'])
def get_crops():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CropTypes")
    crops = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(crops)


# ------------------ QUERIES ------------------
@app.route('/add_query', methods=['POST'])
def add_query():
    try:
        # Support JSON or multipart form-data (FormData)
        if request.content_type and 'multipart/form-data' in request.content_type:
            form = request.form
            FarmerID = int(form.get('FarmerID')) if form.get('FarmerID') else None
            title = form.get('title')
            description = form.get('description')
            crop_type = int(form.get('crop_type')) if form.get('crop_type') else None
            # Optional image handling: accept uploaded file or URL in image_url
            image_url = form.get('image_url')
            file = request.files.get('image')
            if file and file.filename:
                if not is_allowed_image_filename(file.filename):
                    return jsonify({"message": "Unsupported image type"}), 400
                filename = secure_filename(file.filename)
                # Ensure unique filename to avoid collisions
                base, ext = os.path.splitext(filename)
                unique_name = filename
                counter = 1
                while os.path.exists(os.path.join(UPLOAD_DIR, unique_name)):
                    unique_name = f"{base}_{counter}{ext}"
                    counter += 1
                file.save(os.path.join(UPLOAD_DIR, unique_name))
                # Public URL path served via Flask static from 'public'
                image_url = f"/uploads/{unique_name}"
        else:
            data = request.get_json(silent=True) or {}
            FarmerID = int(data.get('FarmerID')) if data.get('FarmerID') is not None else None
            title = data.get('title')
            description = data.get('description')
            crop_type = int(data.get('crop_type')) if data.get('crop_type') is not None else None
            image_url = data.get('image_url')

        if not FarmerID or not title:
            return jsonify({"message": "FarmerID and title are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO Queries (FarmerID, title, description, image_url, crop_type) 
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (FarmerID, title, description, image_url, crop_type))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Query added successfully"})
    except Exception as e:
        return jsonify({"message": f"Error adding query: {str(e)}"}), 500


@app.route('/get_queries', methods=['GET'])
def get_queries():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Queries")
    queries = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(queries)


# ------------------ RESPONSES ------------------
@app.route('/add_response', methods=['POST'])
def add_response():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """INSERT INTO Responses (QueryID, ResponderID, response_text, is_expert, votes) 
             VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(sql, (data['QueryID'], data['ResponderID'], data['response_text'],
                         data.get('is_expert', False), data.get('votes', 0)))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Response added successfully"})


@app.route('/get_responses', methods=['GET'])
def get_responses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Responses")
    responses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(responses)


# ------------------ EQUIPMENT ------------------
@app.route('/add_equipment', methods=['POST'])
def add_equipment():
    try:
        data = request.get_json(silent=True) or {}

        required = ['OwnerID', 'name', 'type', 'condition', 'hourly_rate']
        for field in required:
            if field not in data or data[field] in (None, ""):
                return jsonify({"message": f"{field} is required"}), 400

        owner_id = int(data['OwnerID'])
        hourly_rate = float(data['hourly_rate'])
        availability = data.get('availability_status', 'Available')
        if availability not in ['Available', 'Unavailable']:
            return jsonify({"message": "availability_status must be 'Available' or 'Unavailable'"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Validate that the owner exists to satisfy FK
        cursor.execute("SELECT FarmerID FROM Farmers WHERE FarmerID = %s", (owner_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return jsonify({"message": "OwnerID does not exist"}), 400

        sql = """INSERT INTO Equipment (OwnerID, name, type, `condition`, hourly_rate, availability_status) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (
            owner_id,
            data['name'],
            data['type'],
            data['condition'],
            hourly_rate,
            availability
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Equipment added successfully"})
    except Exception as e:
        return jsonify({"message": f"Error adding equipment: {str(e)}"}), 500


@app.route('/get_equipment', methods=['GET'])
def get_equipment():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Equipment")
    equipment = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(equipment)


# ------------------ LENDING REQUESTS ------------------
@app.route('/add_lending_request', methods=['POST'])
def add_lending_request():
    try:
        data = request.json

        # Validate required fields
        required_fields = ['EquipmentID', 'LenderID', 'BorrowerID', 'start_date', 'duration']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"message": f"{field} is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Always set LenderID to the equipment owner (ignore client-passed LenderID)
        cursor.execute("SELECT OwnerID FROM Equipment WHERE EquipmentID = %s", (int(data['EquipmentID']),))
        row = cursor.fetchone()
        if row is None:
            cursor.close(); conn.close()
            return jsonify({"message": "Equipment not found"}), 400
        owner_id = int(row[0])

        if int(data['BorrowerID']) == owner_id:
            cursor.close(); conn.close()
            return jsonify({"message": "Owner cannot borrow own equipment"}), 400

        sql = """INSERT INTO LendingRequests 
                 (EquipmentID, LenderID, BorrowerID, start_date, duration, status) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""

        cursor.execute(sql, (
            int(data['EquipmentID']),
            owner_id,
            int(data['BorrowerID']),
            data['start_date'],          # YYYY-MM-DD format
            int(data['duration']),
            data.get('status', 'Pending')
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Lending request added successfully"})

    except Exception as e:
        print("Error adding lending request:", e)
        return jsonify({"message": f"Error adding lending request: {str(e)}"}), 500


@app.route('/get_lending_requests', methods=['GET'])
def get_lending_requests():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT lr.*, e.name AS equipment_name, f1.name AS lender_name, f2.name AS borrower_name
            FROM LendingRequests lr
            JOIN Equipment e ON lr.EquipmentID = e.EquipmentID
            JOIN Farmers f1 ON lr.LenderID = f1.FarmerID
            JOIN Farmers f2 ON lr.BorrowerID = f2.FarmerID
        """)
        requests = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(requests)
    except Exception as e:
        print("Error fetching lending requests:", e)
        return jsonify({"message": f"Error fetching lending requests: {str(e)}"}), 500



@app.route('/update_lending_request_status', methods=['POST'])
def update_lending_request_status():
    try:
        data = request.get_json(silent=True) or {}
        request_id = data.get('RequestID')
        new_status = data.get('status')

        if not request_id or not new_status:
            return jsonify({"message": "RequestID and status are required"}), 400

        # Align with DB enum: Pending, Approved, Rejected, Completed
        if new_status not in ['Pending', 'Approved', 'Rejected', 'Completed']:
            return jsonify({"message": "Invalid status"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE LendingRequests SET status = %s WHERE RequestID = %s", (new_status, int(request_id)))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Lending request updated"})
    except Exception as e:
        print("Error updating lending request:", e)
        return jsonify({"message": f"Error updating lending request: {str(e)}"}), 500


# ------------------ REVIEWS ------------------
@app.route('/add_review', methods=['POST'])
def add_review():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """INSERT INTO Reviews (FromFarmerID, ToFarmerID, rating, feedback, type) 
             VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(sql, (data['FromFarmerID'], data['ToFarmerID'], data['rating'],
                         data['feedback'], data['type']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Review added successfully"})


@app.route('/get_reviews', methods=['GET'])
def get_reviews():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Reviews")
    reviews = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(reviews)


# ------------------ MAIN ------------------
if __name__ == '__main__':
    app.run(debug=True)
