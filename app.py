from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.ext.asyncio import result

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost:3306/shoppingmall'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def main():
    products = db.session.execute(
        text("SELECT * FROM product ORDER BY prod_recommend_count desc limit 10")
    ).fetchall()
    return render_template('index.html', products=products)


@app.route('/product')
def product1():
    prod = request.args.get('result')
    return redirect(f'/product/{prod}')

@app.route('/search')
def search():
    prod = request.args.get('result')
    results = db.session.execute(
        text("SELECT prod_id FROM product WHERE prod_name LIKE :prod"),
        {"prod": f"%{prod}%"}
    ).fetchall()

    if results:
        return redirect(f'/product/{results[0][0]}')
    else:
        return render_template('error.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/process', methods=['POST'])
def process():
    where = request.form.get('where')
    if where == 'signup':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password == confirm_password:
            username = request.form.get('username')
            email = request.form.get('email')
            db.session.execute(
                text("INSERT INTO userinfo (username, passwd, email) VALUES (:username, :password, :email)"),
                {"username": username, "password": password, "email": email}
            )
            db.session.commit()
            return redirect('/login')
        else:
            return redirect('/signup')
    elif where == 'login':
        results = db.session.execute(
            text("SELECT passwd FROM userinfo WHERE username = :username"),
            {"username": request.form.get('username')}
        ).fetchall()
        if results:
            if results[0][0] != request.form.get('password'):
                return redirect('/login')
            else:
                return redirect('/')

@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/product/<string:prod>')
def product(prod):
    results = db.session.execute(
        text("SELECT * FROM product WHERE prod_id = :prod"),
        {"prod": prod}
    ).fetchall()
    return render_template('product.html', location = results[0].prod_img_file_location, name = results[0].prod_name, price = results[0].prod_price, desc = results[0].prod_desc, recommend_count = results[0].prod_recommend_count)


if __name__ == '__main__':
    app.run()
