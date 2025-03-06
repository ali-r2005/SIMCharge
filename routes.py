from flask import render_template, redirect, url_for, flash, request , session,jsonify
from flask_login import current_user, login_user, logout_user, login_required
import subprocess
import urllib.parse
from app import app, db
from forms import ClientNumberForm, LoginForm, RegistrationForm, AddOfferForm,ClientNumberForm0,selectMoney,Calling
from models import User, ClientNumber, Offer, MobileCarrier

def make_call(phone_number):
    # URL encode the phone number to handle special characters like #
    encoded_number = urllib.parse.quote(phone_number)
    adb_command = f"adb shell am start -a android.intent.action.CALL -d tel:{encoded_number}"
    
    try:
        # Run the adb command to initiate the call
        subprocess.run(adb_command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Congratulations, you have registered successfully! You can now log in.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while registering. Please try again.')
            app.logger.error(f"Registration error: {str(e)}")
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = url_for('dashboard')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    history = ClientNumber.query.all()
    return render_template('dashboard.html', title='Dashboard',history=history)

@app.route('/number0', methods=['GET', 'POST'])
def number0():
    form = ClientNumberForm0()
    if form.validate_on_submit():
        session['mobile_carrier'] = form.mobile_carrier.data
        return redirect(url_for('number'))
    return render_template('number0.html',form=form)

@app.route('/number', methods=['GET', 'POST'])
def number():
    numbers = session.get('numbers', [])
    if len(numbers) >= 20:
        numbers.clear()
        session['numbers'] = numbers
        flash('Number list has been cleared.', 'info')
    form = ClientNumberForm()
    if form.validate_on_submit():
            number = form.number.data
            mobile_carrier = session.get("mobile_carrier")
            
            existing_number = ClientNumber.query.filter_by(number=number).first()
            if existing_number:
                number_data = {
                'number': existing_number.number,
                'mobile_carrier': existing_number.mobile_carrier,
            }
                numbers.append(number_data)
                session["numbers"] = numbers
                flash('Existing number added to session.', 'info')
                return redirect(url_for('number0'))
            
            client_number = ClientNumber(
                number=number,
                mobile_carrier=mobile_carrier,
            )
            db.session.add(client_number)
            db.session.commit()

            number_data = {
            'number': client_number.number,
            'mobile_carrier': client_number.mobile_carrier,
        }
            numbers.append(number_data)
            session['numbers'] = numbers
            flash('New number added successfully.', 'success')
            return redirect(url_for('number0'))
    return render_template('number.html', title='Add Number', form=form)
@app.route('/confirm')
@login_required
def confirm():
    numbers = session.get('numbers', [])
    reversed_numbers = list(reversed(numbers))
    return render_template('confirm.html',title='Confirm Numbers',history=reversed_numbers)

@app.route('/calling/<money>/<code>', methods=['GET','POST'])
@login_required
def calling(money,code):
    form = Calling()
    last_number = session.get('last_number', '')
    money=money
    code = code
    full = last_number+code
    mobile_carrier = session.get('last_mobile_carrier', '')
    if form.validate_on_submit():
        success = make_call(full)
        if success:
            flash('Call initiated successfully!', 'success')
        else:
            flash('Failed to initiate the call. Please try again.', 'error')
        return redirect(url_for('confirm'))
    return render_template('call.html', full=full ,carrier=mobile_carrier,form=form)

@app.route('/add_client_number', methods=['GET', 'POST'])
@login_required
def add_client_number():
    form = ClientNumberForm()
    if form.validate_on_submit():
        client_number = ClientNumber(
            number=form.number.data,
            mobile_carrier=form.mobile_carrier.data
        )
        db.session.add(client_number)
        db.session.commit()
        flash('Client number added successfully.')
        return redirect(url_for('dashboard'))
    return render_template('add_client_number.html', title='Add Client Number', form=form)

@app.route('/add_offer', methods=['GET', 'POST'])
@login_required
def add_offer():
    form = AddOfferForm()
    if form.validate_on_submit():
        offer = Offer(
            title=form.title.data,
            description=form.description.data,
            code=form.code.data,
            mobile_carrier=form.mobile_carrier.data
        )
        db.session.add(offer)
        db.session.commit()
        flash('Offer added successfully.')
        return redirect(url_for('dashboard'))
    return render_template('addOffer.html', title='Add Offer', form=form)

@app.route('/all_offers/<num>/<mc>', methods=['GET', 'POST'])
@login_required
def all_offers(num,mc):
    offers = Offer.query.filter_by(mobile_carrier=mc).all()
    form = selectMoney()
    session['last_number'] = num
    session['last_mobile_carrier'] = mc
    return render_template('allOffers.html', form=form,offers=offers)

@app.route('/delete_offer/<pid>', methods=['DELETE'])
@login_required
def delete_offer(pid):
    offer = Offer.query.filter_by(code=pid).first()
    if offer:
        db.session.delete(offer)
        db.session.commit()
        return jsonify({"message": "Offer deleted successfully."}), 200
    return jsonify({"message": "Offer not found."}), 404



@app.route('/detailOffer/<pid>',methods=['GET',"PUT"])
@login_required
def detailOffer(pid):
    offer = Offer.query.filter_by(code=pid).first()
    if offer:
        return render_template('detail.html', offer=offer)

