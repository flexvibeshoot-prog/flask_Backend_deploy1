import pymysql

try:
    conn = pymysql.connect(
        host='gateway01.ap-southeast-1.prod.aws.tidbcloud.com',
        port=4000,
        user='47vaDr39q2MWZRN.root',   # ✅ use full username exactly like this
        password='0mD5HmOy4Ffzze3O',
        database='test',
        ssl={'ca': r'E:\BackendFolderEcomerse\certs\isrgrootx1.pem'}  # ✅ path to your cert file
    )

    print("✅ Successfully connected to TiDB Cloud!")
    with conn.cursor() as cursor:
        cursor.execute("SELECT NOW();")
        print("Server Time:", cursor.fetchone())

except Exception as e:
    print("❌ Connection failed:", e)

finally:
    if 'conn' in locals() and conn.open:
        conn.close()

# To add product....
import os
import requests

folder_path = r"C:\Users\Kanchan\Music\Downloads\image_folder"
files_name = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# print(len(files))
tshirt_names = [
    "Classic Cotton Tee",
    "Urban Streetwear T-Shirt",
    "Minimalist Crew Neck",
    "Graphic Print Tee",
    "Retro Vibes T-Shirt",
    "Athletic Fit Tee",
    "Oversized Comfort Tee",
    "Vintage Wash Tee",
    "Pocket Style Tee",
    "Striped Casual Tee",
    "Solid Color Basic Tee",
    "Tie-Dye Chill Tee",
    "Logo Printed Tee",
    "V-Neck Classic Tee",
    "Raglan Sleeve Tee",
    "Performance Dry-Fit Tee",
    "Longline Modern Tee",
    "Henley Button Tee",
    "Color Block Tee",
    "Marble Texture Tee",
    "Embroidery Logo Tee",
    "Soft Touch Premium Tee",
    "Summer Breeze Tee",
    "Midnight Black Tee"
]
numbers = [
    415, 428, 439, 452, 467, 489, 503, 519,
    545, 562, 578, 595, 612, 648, 671, 694,
    718, 743, 769, 812, 845, 879, 923, 981
]

url = "http://127.0.0.1:5000/product/add_product"

for i in range(len(files_name)):
    form_data = {
        "name": tshirt_names[i],
        "description": f"Noise-cancelling Bluetooth headphones {tshirt_names[i]}",
        "price": numbers[i],
        "stock_quantity": 50,
        "category_id": 2,
        "brand_id": 1,
        'discount': 10,
    }

    files = {
        "image": open(os.path.join(folder_path, files_name[i]), "rb")
    }

    response = requests.post(url, data=form_data, files=files)
    print("Status Code:", response.status_code)
    print("Raw Response:", response.text)

    try:
        data = response.json()
        print(data)
    except requests.exceptions.JSONDecodeError:
        print("❌ Server did not return JSON.")
        print("Raw text:", response.text)
        continue  # Skip this product

    if not data:
        print("❌ Empty response from server.")
        continue

    product_id = data.get('product_id')
    img_url = data.get('image_urls')

    response1 = requests.post('http://127.0.0.1:5000/product/add_image', json={
        "product_id": product_id,
        "image_urls": img_url
    })

    if response.status_code in [200, 201]:
        print(f"✅ Successfully added product: {tshirt_names[i]}")
        print(response1.json())
    else:
        print(f"❌ Failed to add product: {tshirt_names[i]}, Status Code: {response.status_code}")


# print(isinstance([1,2],list))


# import redis
# print(redis.__version__)



# from flask import Flask, jsonify
# from tasks import long_running_task,send_email_task

# app = Flask(__name__)

# @app.route("/start-task")
# def start_task():
#     long_running_task.delay()
#     return jsonify({"message": "Task started in background"})

# @app.route('/send_mail')
# def send_mail():
#     send_email_task.delay(
#         "khazra800@gmail.com",
#         "Welcome..!!",
#         "This email is send using celery and redis queue."
#     )
#     return jsonify({"message":"Email is being send in background..."})

# if __name__ == "__main__":
#     app.run(debug=True)

