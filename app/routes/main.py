from flask import Blueprint,jsonify,request
# from app import db
# from app.models import User
# from sqlalchemy import text
# import cloudinary.uploader
from app import limiter

main=Blueprint('main', __name__, url_prefix='/main')


@main.route('/home')
@limiter.limit("5 per minute")
def index():
    # from app.tasks.location.get_lat_long import geocode_address
    # print(geocode_address(721148))
    # from app.tasks.location.distance_calc import calculate_distance_km
    # # Kolkata → Howrah (known distance ~6.5 km)
    # print(calculate_distance_km(22.5726, 88.3639, 22.5850, 88.3468))

    return jsonify({"message": "Welcome to the Main Blueprint!"})

@main.route("/test_work")
def tests():
    from app.tasks.Registermessaging_task import send_mail_task
    from app.tasks.heavy_task import process_heavy_task
    from app.tasks.log_task import log_task
    send_mail_task.delay("khazra800@gmail.com", 1234, "Kanchan")
    process_heavy_task.delay()
    log_task.delay("User visited test route")

    return jsonify({"status": "tasks queued"})

# @main.route('/testdb')
# def test_db():
#     try:
#         result = db.session.execute(text("SELECT NOW();"))  # ✅ wrap in text()
#         server_time = list(result)[0][0]
#         return jsonify({
#             "message": "Connected to TiDB Cloud!",
#             "server_time": str(server_time)
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)})
    
# @main.route('/add_user')
# def get_users():
#     new_user = User(name="Kanchan", email="kanchan@example.com")
#     db.session.add(new_user)
#     db.session.commit()
#     print('ADDED USER:', new_user.name)
#     return jsonify({"message": "User added successfully!"})


# @main.route('/upload', methods=['POST'])
# def upload_image():
#     if 'image' not in request.files:
#         return jsonify({"error": "No image provided"}), 400

#     image = request.files['image']
    
#     if image.filename == '':
#         return jsonify({"error": "No file selected"}), 400

#     try:
#         upload_result = cloudinary.uploader.upload(image)
#         return jsonify({
#             "message": "Upload successful!",
#             "url": upload_result['secure_url'],
#             "public_id": upload_result['public_id']
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

