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
        {"prod": f"%{prod}%"}   # 여기서 %를 붙여줌
    ).fetchall()
    return redirect(f'/product/{results[0][0]}')

@app.route('/login')
def login():
    return render_template('login.html')

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
