from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost:3306/shoppingmall'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/product')
def product1():
    prod = request.args.get('searchbox')
    return redirect(f'/product/{prod}')

@app.route('/product/<string:name>')
def product(name):
    return {'상품' : name}


if __name__ == '__main__':
    app.run()
