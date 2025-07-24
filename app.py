import os
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId

app = Flask(__name__)

# Configure local MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/quickshop"
mongo = PyMongo(app)

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Initialize with sample data if collection is empty
    if mongo.db.products.count_documents({}) == 0:
        sample_products = [
            {
                'name': 'Sample Product 1',
                'price': 19.99,
                'description': 'This is a sample product description',
                'image': 'sample1.jpg'
            },
            {
                'name': 'Sample Product 2',
                'price': 29.99,
                'description': 'Another sample product for demonstration',
                'image': 'sample2.jpg'
            }
        ]
        mongo.db.products.insert_many(sample_products)
    
    products = list(mongo.db.products.find())
    return render_template('index.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'image' not in request.files:
        return redirect(request.url)
    
    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        product = {
            'name': request.form.get('name'),
            'price': float(request.form.get('price')),
            'description': request.form.get('description'),
            'image': filename
        }
        
        mongo.db.products.insert_one(product)
    
    return redirect(url_for('index'))

@app.route('/mock_checkout/<product_id>')
def mock_checkout(product_id):
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
    return f"""
    <h1>Mock Checkout</h1>
    <p>Thank you for your interest in {product['name']}!</p>
    <p>Price: ${product['price']:.2f}</p>
    <p>This is a mock checkout page. In a real implementation, this would process payments.</p>
    <a href="/">Back to store</a>
    """

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)