from flask import Flask, render_template, url_for, request, session, redirect, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user:
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            session.pop('user', None)

            Username = request.form['username']
            Password = request.form['pass']

            userlist = User.query.filter_by(username=Username, password=Password).first()
            
            if userlist:
                session['user'] = request.form['username']
                return redirect(url_for('home'))
            else:
                return render_template('index.html', status="login yoki parolda xatolik")

        return render_template('index.html')


@app.route('/home')
def home():
    if g.user:
        return render_template('home.html', user=session['user'])

    return redirect(url_for('index'))


@app.route('/user-list')
def list_user():
    userlist = User.query.order_by(User.date).all()
    return render_template('user-list.html',userlist=userlist)


@app.route('/user-list/<int:id>')
def list_detail(id):
    userlist = User.query.get(id)
    return render_template('user-add.html',userlist=userlist)


@app.route('/user-list/<int:id>/del')
def list_detail_delete(id):
    userlist = User.query.get_or_404(id)
    
    try:
        db.session.delete(userlist)
        db.session.commit()
        return redirect('/user-list')
    except:
        return "error with delete"



@app.route('/user-list/<int:id>/update', methods=['POST', 'GET'])
def user_update(id):
    if g.user:
        user = User.query.get(id)

        if request.method == 'POST':
            user.username = request.form['username']
            user.password = request.form['password']
        
            try:
                db.session.commit()
                return redirect('/user-list')
            except:
                return "error on add user"
        else:
            return render_template('user-update.html', user=user)

    return redirect(url_for('index'))


@app.route('/user-add', methods=['POST', 'GET'])
def add_user():
    if g.user:
        if request.method == 'POST':
            username = request.form['username']
            password1 = request.form['password1']
            password2 = request.form['password2']

            if password1 == password2:
                useradd = User(username=username, password=password2)

                try:
                    db.session.add(useradd)
                    db.session.commit()
                    return redirect('/user-list')
                except:
                    return "error on add user"
            else:
                return redirect('/user-add')
        else:
            return render_template('user-add.html', user=session['user'])

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('index.html')


@app.before_request
def before_request():
    g.user = None

    if 'user' in session:
        g.user = session['user']


if __name__ == "__main__":
    app.run(debug=True)