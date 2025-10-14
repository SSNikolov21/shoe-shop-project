from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Данни в паметта
users = []
products = []
cart = {}
orders = []

# Админ потребител
admin_user = {
    'name': 'Admin',
    'surname': 'Admin',
    'username': 'admin',
    'password': 'admin'
}
users.append(admin_user)

# Функции за проверка
def find_user(username):
    return next((u for u in users if u['username'] == username), None)

def find_product(product_id):
    return next((p for p in products if p['id'] == product_id), None)

# Начална страница
@app.route('/')
def index():
    return render_template('index.html')

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        username = request.form['username']
        password = request.form['password']
        if find_user(username):
            flash('Потребител с това име вече съществува.')
            return redirect(url_for('register'))
        user = {
            'name': name,
            'surname': surname,
            'username': username,
            'password': password
        }
        users.append(user)
        print(f"Потребител {username} е регистриран.")  # Потвърждение в конзолата
        flash('Успешна регистрация! Можете да влезете.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = find_user(username)
        if user and user['password'] == password:
            session['username'] = username
            flash('Влезли сте успешно.')
            return redirect(url_for('catalog'))
        else:
            flash('Грешни данни.')
    return render_template('login.html')

# Изход
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Излезли сте.')
    return redirect(url_for('index'))

# Каталог
@app.route('/catalog')
def catalog():
    return render_template('catalog.html', products=products)

# Добавяне на продукт (само за администратор)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        # CRUD операции
        action = request.form['action']
        if action == 'add':
            new_id = len(products) + 1
            product = {
                'id': new_id,
                'name': request.form['name'],
                'description': request.form['description'],
                'color': request.form['color'],
                'size': request.form['size'],
                'price': float(request.form['price']),
                'stock': int(request.form['stock'])
            }
            products.append(product)
        elif action == 'edit':
            prod_id = int(request.form['id'])
            product = find_product(prod_id)
            if product:
                product.update({
                    'name': request.form['name'],
                    'description': request.form['description'],
                    'color': request.form['color'],
                    'size': request.form['size'],
                    'price': float(request.form['price']),
                    'stock': int(request.form['stock'])
                })
        elif action == 'delete':
            prod_id = int(request.form['id'])
            products[:] = [p for p in products if p['id'] != prod_id]
    return render_template('admin.html', products=products)

# Добавяне към кошницата
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    if username not in cart:
        cart[username] = []
    product = find_product(product_id)
    if product:
        cart[username].append(product)
    return redirect(url_for('catalog'))

# Кошница
@app.route('/cart', methods=['GET', 'POST'])
def view_cart():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    user_cart = cart.get(username, [])
    if request.method == 'POST':
        address = request.form['address']
        payment_method = request.form['payment']
        # Обработка на поръчката
        order = {
            'user': username,
            'products': user_cart,
            'address': address,
            'payment': payment_method
        }
        orders.append(order)
        # Намаляване на наличността
        for p in user_cart:
            prod = find_product(p['id'])
            if prod:
                prod['stock'] -= 1
        cart[username] = []
        flash('Поръчката е финализирана.')
        return redirect(url_for('catalog'))
    return render_template('cart.html', cart=user_cart)

if __name__ == '__main__':
    # Добавяме примерни продукти
    products.extend([
        {'id': 1, 'name': 'Обувка 1', 'description': 'Описание 1', 'color': 'черен', 'size': 42, 'price': 100.0, 'stock': 5},
        {'id': 2, 'name': 'Обувка 2', 'description': 'Описание 2', 'color': 'бял', 'size': 40, 'price': 120.0, 'stock': 3},
        {'id': 3, 'name': 'Обувка 3', 'description': 'Описание 3', 'color': 'кафяв', 'size': 44, 'price': 150.0, 'stock': 2}
    ])
    app.run(debug=True)