from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

app = Flask(__name__)

engine = create_engine("sqlite:///flask_db.sqlite", echo=False)

Base = declarative_base()

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    call = Column(Integer)
    injured = Column(Boolean, default=False)
    injury_description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    reservations = relationship("Reservation", back_populates="member")

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True)
    sport = Column(String(50), nullable=False)
    day = Column(String(10), nullable=False)
    time = Column(String(10), nullable=False)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False) 
    member = relationship("Member", back_populates="reservations")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def index():
    return render_template('index.html')
    

@app.route('/members', methods=['GET', 'POST'])
def members():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        call = request.form.get('call')
        injured = 'yes' if request.form.get('injured') == 'on' else 'no'
        injury_description = request.form.get('injury_description')

        member = Member(
            first_name=first_name,
            last_name=last_name,
            call=call,
            injured=(injured == 'yes'),
            injury_description=injury_description
        )

        session.add(member)
        session.commit()

        return redirect(url_for('reservation', member_id=member.id))

    return render_template('members.html')

@app.route('/reservation', methods=['GET', 'POST'])
def reservation():
    if request.method == 'POST':
        sport = request.form.get('sport')
        day = request.form.get('day')
        time = request.form.get('time')
        member_id = request.form.get('member_id')

        reservation = Reservation(sport=sport, day=day, time=time, member_id=member_id)
        session.add(reservation)
        session.commit()

        return redirect(url_for('pay'))

    members = session.query(Member).all()
    member_id = request.args.get('member_id')

    return render_template('reservation.html', member_id=member_id, members=members)

@app.route('/pay', methods=['GET', 'POST'])
def pay():
    if request.method == "POST":

        return redirect(url_for('thank_you'))
    return render_template('pay.html')

@app.route('/list')
def list():
    members = session.query(Member).all()
    return render_template('list.html', members=members)

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

    
@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
