from urllib.request import urlopen
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/betondb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Betonomehalka(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    specs = db.Column(db.String, nullable=False)
    power = db.Column(db.Float, nullable=False)
    comments = db.relationship('Comment', backref='betonomehalka', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    betonomehalka_id = db.Column(db.Integer, db.ForeignKey('betonomehalka.id'), nullable=False)
    text = db.Column(db.String, nullable=False)


def fetch_data():
    url = 'https://www.agrotreding.ru/catalog/betonomeshalki?categoryID=282&search=1&advanced_search_in_category=1&firm_ids[0]=370&search_price_from=6100&search_price_to=1419900'
    try:
        html_code = str(urlopen(url).read(), 'utf-8')
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}

    soup = BeautifulSoup(html_code, "html.parser")
    names = soup.select("div.prd_brf_product_name")
    prices = soup.select("span.PriceWithUnit")
    opt = soup.select("div.content")

    betonomeshalkers = {}
    for n in range(min(len(names), len(prices), len(opt))):
        try:
            name = ' '.join(names[n].text.split())
            price = ''.join(prices[n].text.split())
            options = opt[n].text.split()
            options_print = ' '.join(options)
            power = int(options[-2]) * 20
            betonomeshalkers[name] = [name, price, options_print, power]
        except Exception as e:
            print(f"Error parsing item {n}: {e}")
            continue
    return betonomeshalkers

def setup():
    with app.app_context():
        db.create_all()
        if Betonomehalka.query.count() == 0:
            data = fetch_data()
            for item in data.values():
                betonomehalka = Betonomehalka(name=item[0], price=item[1], specs=item[2], power=item[3])
                db.session.add(betonomehalka)
            db.session.commit()

with app.app_context():
    setup()

@app.route('/')
def index():
    betonomehalkers = Betonomehalka.query.order_by(Betonomehalka.name).all()
    return render_template('index.html', betonomehalkers=betonomehalkers)


@app.route('/comment', methods=['POST'])
def add_comment():
    betonomehalka_id = request.form.get('betonomehalka_id')
    text = request.form.get('text')
    if betonomehalka_id and text:
        comment = Comment(betonomehalka_id=betonomehalka_id, text=text)
        db.session.add(comment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Comment added!', 'text': comment.text})
    return jsonify({'success': False, 'message': 'Invalid data'})


@app.route('/sort')
def sort_betonomehalkers():
    sort_by = request.args.get('sort_by', 'name')
    if sort_by == 'power':
        betonomehalkers = Betonomehalka.query.order_by(Betonomehalka.power).all()
    elif sort_by == 'price':
        betonomehalkers = Betonomehalka.query.order_by(Betonomehalka.price).all()
    else:
        betonomehalkers = Betonomehalka.query.order_by(Betonomehalka.name).all()

    data = []
    for item in betonomehalkers:
        comments = [{'text': comment.text} for comment in item.comments]
        data.append({
            'id': item.id,
            'name': item.name,
            'specs': item.specs,
            'price': item.price,
            'power': item.power,
            'comments': comments
        })

    return jsonify({'betonomehalkers': data})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)