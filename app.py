from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.ext.asyncio import result

app = Flask(__name__)
app.secret_key = "비밀키"
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
        username = request.form.get('username')
        results = db.session.execute(
            text("SELECT passwd FROM userinfo WHERE username = :username"),
            {"username": username}
        ).fetchall()
        if results:
            if results[0][0] != request.form.get('password'):
                return redirect('/login')
            else:
                session['user'] = username
                return redirect('/')
    elif where == 'review':
        review = request.form.get('review')
        id = request.form.get('id')
        db.session.execute(
            text("INSERT INTO review (username, prod_id, review) VALUES (:username, :prod_id, :review)"),
            {"username": session.get('user'), "prod_id": id, "review": review}
        )
        db.session.commit()
        return redirect(f'/product/{id}')
    elif where == 'buy':
        count = request.form.get('count')
        id = request.form.get('id')
        db.session.execute(
            text("INSERT INTO orders (username, prod_id, prod_count) VALUES (:username, :prod_id, :prod_count)"),
            {"username": session.get('user'), "prod_id": id, "prod_count": count}
        )
        db.session.commit()
        return redirect(f'/product/{id}')
    elif where == 'recommend':
        id = request.form.get('id')
        db.session.execute(
            text("UPDATE product SET prod_recommend_count = prod_recommend_count + 1  WHERE prod_id = :prod_id"),
            {"prod_id": id}
        )
        db.session.commit()

        db.session.execute(
            text("INSERT INTO recommend_list (username, prod_id) VALUES (:username, :prod_id)"),
            {"username": session.get('user'), "prod_id": id}
        )
        db.session.commit()
        return redirect(f'/product/{id}')

@app.route('/info')
def info():
    count = db.session.execute(
        text("SELECT * FROM orders WHERE username = :username"),
        {"username": session['user']}
    ).fetchall()
    if count:
        li = []
        for i in range(len(count)):
            prodname = db.session.execute(
                text("SELECT prod_name FROM product WHERE prod_id = :prod"),
                {"prod": count[i][2]}
            ).fetchone()
            li.append([count[i][3], prodname[0]])

        return render_template('info.html', orders = li)
    return render_template('info.html')
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/product/<string:prod>')
def product(prod):
    recommend_list = []
    results = db.session.execute(
        text("SELECT * FROM product WHERE prod_id = :prod"),
        {"prod": prod}
    ).fetchall()

    review = db.session.execute(
        text("SELECT * FROM review WHERE prod_id = :prod"),
        {"prod": prod}
    ).fetchall()
    if session.get('user'):
        recommend_list = db.session.execute(
            text("SELECT prod_id FROM recommend_list WHERE username = :username"),
            {"username": session['user']}
        ).fetchall()
        recommend_list = [item[0] for item in recommend_list]
    return render_template('product.html', id = prod ,location = results[0].prod_img_file_location, name = results[0].prod_name, price = results[0].prod_price, desc = results[0].prod_desc, recommend_count = results[0].prod_recommend_count, reviews = review, recommend_list = recommend_list)


if __name__ == '__main__':
    app.run()
