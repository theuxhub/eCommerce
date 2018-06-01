'''
Routes for the website
'''

from flask import Flask, make_response, jsonify, g, render_template, flash, redirect, url_for, request, send_from_directory, session, abort

from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_uploads import configure_uploads
from flask_mail import Mail, Message
from flask_sslify import SSLify
from flask_compress import Compress

from itsdangerous import URLSafeTimedSerializer

from threading import Thread

from werkzeug.datastructures import CombinedMultiDict, FileStorage
from werkzeug.utils import secure_filename
import os
import datetime

import forms
import models

from peewee import SelectQuery

app = Flask(__name__)

app.secret_key = 'secret-key' # Your sceret key

# app.config['UPLOADED_<Name of Upload Set In Uppercase>_DEST']
app.config['UPLOADED_IMAGES_DEST'] = 'images/uploads/products'

configure_uploads(app, (forms.images,))

login_manager = LoginManager() # create a login manager
login_manager.init_app(app) # initialize login manager with flask app
login_manager.login_view = 'login' # view used for login


app.config['MAIL_SERVER']='' # Your mail server
app.config['MAIL_PORT'] = 587 # Your mail server port
app.config['MAIL_USERNAME'] = '' # your mail server username
app.config['MAIL_PASSWORD'] = '' # your mail server password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
sslify = SSLify(app)
Compress(app)

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if (endpoint == 'static' or endpoint == 'product_images'):
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connet to the database before each request."""
    try:
        g.db = models.DATABASE
        g.db.connect()
    except models.OperationalError:
        pass


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

#
# Routes For Authentication
#

@app.route('/register/', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Awesome! You have registerd to Our Site", category='Success')
        try:
            models.User.create_user(
                full_name = form.full_name.data,
                email = form.email.data,
                password = form.password.data,
                mobile_no = form.mobile_no.data
            )
            user = models.User.get(models.User.email == form.email.data)
            login_user(user)
        except ValueError:
            pass
        # Send Email
        send_email("Account Registered", 'support@redgingger.com', [form.email.data], '', render_template('email/register.html', user=form.full_name.data))
        next = request.args.get('next')
        return redirect(next or url_for('index'))
    return render_template('register.html', form=form, user=current_user)


@app.route('/login/', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    next = request.args.get('next')
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match", "Error")
        else:
            if check_password_hash(user.password.encode('utf-8'), form.password.data):
                login_user(user)
                if current_user.is_admin:
                    return redirect(next or url_for('dashboard'))
                else:
                    flash("Successfully logged in!", "Success")
                    return redirect(next or url_for('index'))
            else:
                flash("Your email or password doesn't match", "Error")
    return render_template('login.html', form=form, user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Successfully logged out. Come back again!!", "Success")
    return redirect(url_for('index'))


@app.route('/profile/')
@login_required
def user_profile():
    products = models.Product.select(models.BuyHistory, models.Product).join(models.BuyHistory).annotate(models.BuyHistory, models.BuyHistory.product_quantity).where(models.BuyHistory.buyer == current_user.id)
    return render_template('user-profile.html', user=current_user, products=products)


# cancel order
@app.route('/order/cancel/<id>')
@login_required
def cancel_order(id):
    q = models.BuyHistory.update(status="Canceled").where(models.BuyHistory.order_id == id)
    q.execute()
    flash('Order Canceled!')
    return redirect(url_for('user_profile'))

@app.route('/new_password/', methods=('GET', 'POST'))
@login_required
def change_password():
    form = forms.new_password()
    if form.validate_on_submit():
        user = models.User.get(models.User.email == current_user.email)
        if check_password_hash(user.password, form.old_password.data):
            q = models.User.update(password=generate_password_hash(form.password.data)).where(models.User.email == current_user.email)
            q.execute()
            # Send Email
            msg = Message('Hello', sender = 'support@redgingger.com', recipients = [current_user.email])
            msg.body = "Your password of RedGingger has been succesfully changed!"
            mail.send(msg)
            return redirect(url_for('index'))
        else:
            flash("Wrong Password!")
    return render_template('change-password.html', user=current_user, form=form)

#
# Routes for front pages
#

@app.route('/')
def index():
    return render_template("index.html", user=current_user, products=models.Product, links=models.Banner)


@app.route('/about')
def t_about():
    return render_template("about.html", user=current_user)

@app.route('/return')
def t_return():
    return render_template("return.html", user=current_user)

@app.route('/contact-us', methods=('GET', 'POST'))
def contact_us():
    form = forms.ContactForm()
    if form.validate_on_submit():
        # Send Email
        message = "Hello Navneet,\nA new contact mail from {0}\n{1}\n{2}\n{3}".format(form.name.data, form.email.data, form.mobile_no.data, form.message.data)
        send_email("Contact Form Message", 'support@redgingger.com', ['nkaushik1998@gmail.com'], message, '')
        send_email("Contact Form Message", 'support@redgingger.com', ['niteshkumarniranjan@gmail.com'], message, '')
        return redirect(url_for('thanks_contact'))
    return render_template("contact.html", user=current_user, form=form)

@app.route('/thanks')
def thanks_contact():
    return render_template("thanks.html", user=current_user)

@app.route('/products/ideal_for/boys')
def boys_products():
    products = models.Product.select().where(models.Product.ideal_for.contains('Boys'))
    return render_template("index_boys.html", user=current_user, products=products, links=models.Banner)

@app.route('/products/ideal_for/girls')
def girls_products():
    products = models.Product.select().where(models.Product.ideal_for.contains('Girls'))
    return render_template("index_girls.html", user=current_user, products=products, links=models.Banner)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', user=current_user), 404

#
# Dashboard Routes
#

@app.route('/dashboard/')
@login_required
def dashboard():
    if current_user.is_admin:
        return render_template("dashboard/html/dashboard.html", user=current_user)
    else:
        return redirect(url_for('index'))


@app.route('/dashboard/users/')
@login_required
def dashboard_users():
    if current_user.is_admin:
        return render_template("dashboard/html/user.html", user=current_user, data=models.User)
    else:
        return redirect(url_for('index'))


@app.route('/dashboard/products/')
@login_required
def dashboard_products():
    if current_user.is_admin:
        return render_template("dashboard/html/product.html", user=current_user, products=models.Product, app=app)
    else:
        return redirect(url_for('index'))


@app.route('/dashboard/products/new/', methods=('GET', 'POST'))
@login_required
def dashboard_products_new():
    if current_user.is_admin:
        form = forms.new_product_form(CombinedMultiDict((request.files, request.form)))
        filename1 = ''
        filename2 = ''
        filename3 = ''
        if form.validate_on_submit():
            if form.image_1.data:
                f = form.image_1.data
                filename1 = secure_filename(f.filename)
                f.save(os.path.join(
                    app.instance_path, app.config['UPLOADED_IMAGES_DEST'], filename1
                ))
            if form.image_2.data:
                f = form.image_2.data
                filename2 = secure_filename(f.filename)
                f.save(os.path.join(
                    app.instance_path, app.config['UPLOADED_IMAGES_DEST'], filename2
                ))
            if form.image_3.data:
                f = form.image_3.data
                filename3 = secure_filename(f.filename)
                f.save(os.path.join(
                    app.instance_path, app.config['UPLOADED_IMAGES_DEST'], filename3
                ))
            models.Product.add_product(
                name=form.name.data,
                image_1=filename1,
                image_2=filename2,
                image_3=filename3,
                count=form.count.data,
                actual_price=form.actual_price.data,
                off_percent=form.off_percent.data,
                buy_price=form.buy_price.data,
                style= form.style.data,
                lenses_color = form.lenses_color.data,
                frame_color = form.frame_color.data,
                brand_name = form.brand_name.data,
                lenses_material = form.lenses_material.data,
                frame_material = form.frame_material.data,
                usage = form.usage.data,
                packaging = form.packaging.data,
                uv_protection = form.uv_protection.data,
                model_no = form.model_no.data,
                suitable_for = form.suitable_for.data,
                size = form.size.data,
                ideal_for = form.ideal_for.data,
                typ_e = form.typ_e.data,
                features = form.features.data,
                case_type = form.case_type.data,
                dimensions_bridgesize = form.dimensions_bridgesize.data,
                dimensions_hrizontal_width = form.dimensions_hrizontal_width.data,
                dimensions_frame_arm_lenght = form.dimensions_frame_arm_lenght.data,
                weight = form.weight.data,
                other_details = form.other_details.data
            )
            return redirect(url_for('dashboard_products'))
        return render_template("dashboard/html/product/new.html", user=current_user, form=form)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard/products/edit/<id>', methods=('GET', 'POST'))
@login_required
def dashboard_products_edit(id):
    if current_user.is_admin:
        product = models.Product.get(models.Product.id == id)
        form = forms.edit_product_form(CombinedMultiDict((request.files, request.form)), obj=product)
        # q = models.User.update(password=form.password.data).where(models.User.email == current_user.email)
        filename1 = ''
        filename2 = ''
        filename3 = ''

        if form.validate_on_submit():
            if form.image_1.data:
                f = form.image_1.data
                if type(f) == FileStorage:
                    filename1 = secure_filename(f.filename)
                    f.save(os.path.join(
                        app.instance_path, app.config['UPLOADED_IMAGES_DEST'], filename1
                    ))
                else:
                    filename1 = f
            if form.image_2.data:
                f = form.image_2.data
                if type(f) == FileStorage:
                    filename2 = secure_filename(f.filename)
                    f.save(os.path.join(
                        app.instance_path, app.config['UPLOADED_IMAGES_DEST'], filename2
                    ))
                else:
                    filename2 = f
            if form.image_3.data:
                f = form.image_3.data
                if type(f) == FileStorage:
                    filename3 = secure_filename(f.filename)
                    f.save(os.path.join(
                        app.instance_path, app.config['UPLOADED_IMAGES_DEST'], filename3
                    ))
                else:
                    filename3 = f
            q = models.Product.update(
                name=form.name.data,
                count=form.count.data,
                image_1 = filename1,
                image_2 = filename2,
                image_3 = filename3,
                actual_price=form.actual_price.data,
                off_percent=form.off_percent.data,
                buy_price=form.buy_price.data,
                style= form.style.data,
                lenses_color = form.lenses_color.data,
                frame_color = form.frame_color.data,
                brand_name = form.brand_name.data,
                lenses_material = form.lenses_material.data,
                frame_material = form.frame_material.data,
                usage = form.usage.data,
                packaging = form.packaging.data,
                uv_protection = form.uv_protection.data,
                model_no = form.model_no.data,
                suitable_for = form.suitable_for.data,
                size = form.size.data,
                ideal_for = form.ideal_for.data,
                typ_e = form.typ_e.data,
                features = form.features.data,
                case_type = form.case_type.data,
                dimensions_bridgesize = form.dimensions_bridgesize.data,
                dimensions_hrizontal_width = form.dimensions_hrizontal_width.data,
                dimensions_frame_arm_lenght = form.dimensions_frame_arm_lenght.data,
                weight = form.weight.data,
                other_details = form.other_details.data
            ).where(models.Product.id == id)
            q.execute()
        return render_template('dashboard/html/product/edit.html', user=current_user, form=form, item=product)
    else:
        return redirect(url_for('index'))


@app.route('/dashboard/products/delete/<id>', methods=('GET', 'POST'))
@login_required
def dashboard_products_delete(id):
    if current_user.is_admin:
        product_ins = models.Product.get(models.Product.id == id)
        product_ins.delete_instance()
        return redirect(url_for('dashboard_products'))
    else:
        return redirect(url_for('index'))


@app.route('/dashboard/orders/')
@login_required
def dashboard_orders():
    if current_user.is_admin:
        return render_template("dashboard/html/orders.html", user=current_user, products=models.BuyHistory, app=app)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard/orders/edit/<int:order_id>')
@login_required
def dashboard_orders_edit(order_id):
    if current_user.is_admin:
        product = models.BuyHistory.get(models.BuyHistory.id == order_id)
        return render_template("dashboard/html/edit-order.html", user=current_user, product=product, app=app)
    else:
        return redirect(url_for('index'))


@app.route('/dahboard/delivered/<int:order_id>/<int:deliv>')
@login_required
def dashboard_delivered(order_id, deliv):
    if current_user.is_admin:
        if deliv == 1:
            q = models.BuyHistory.update(delivered = True, status="Delivered", deliverTime=datetime.datetime.now()).where(models.BuyHistory.id == order_id)
            q.execute()
        else:
            q = models.BuyHistory.update(delivered = False, status="Initiated").where(models.BuyHistory.id == order_id)
            q.execute()
        return redirect(url_for('dashboard_orders'))
    else:
        return redirect(url_for('index'))

@app.route('/dashboard/banner/', methods=['GET', 'POST'])
@login_required
def dashboard_banner():
    if current_user.is_admin:
        if request.method == 'POST':
            url = request.form['text']
            models.Banner.add_banner(link = url)
        return render_template('dashboard/html/banner.html', user=current_user, app=app, links=models.Banner)
    return redirect(url_for('index'))

@app.route('/dashboard/banner/del/<id>')
@login_required
def del_dashboard_banner(id):
    if current_user.is_admin:
        q = models.Banner.get(models.Banner.id == id)
        q.delete_instance()
        return redirect(url_for('dashboard_banner'))
    return redirect(url_for('index'))

#
# Product Route
#
@app.route('/product/<path:name>/', methods=('GET', 'POST'))
def product_index(name):
    try:
        product_ins = models.Product.get(models.Product.title == name)
    except models.Product.DoesNotExist:
        return abort(404)
    # comments = models.User.select(models.Product, models.User, models.Comment).join(models.Comment).annotate(models.Comment, models.Comment.text).where(models.Product.title == name)
    comments = models.Comment.select().where(models.Comment.product == product_ins)
    return render_template("product/index.html", user=current_user, product=product_ins, comments=comments)


@app.route('/add_comment/<int:product_id>', methods=('GET', 'POST'))
def add_comment(product_id):
    if request.method == 'POST':
        if current_user.is_authenticated:
            models.Comment.add_comment(
                user = current_user.id,
                product = product_id,
                text = request.form['review-text'],
                rating= request.form['rating']
            )
        else:
            return redirect(url_for('login'))
    product_ins = models.Product.get(models.Product.id == product_id)
    return redirect(url_for('product_index', name=product_ins.title))

#
# Cart and checkout route
#

@app.route('/buy_now/<int:product_id>')
@login_required
def buy_now(product_id):
    try:
        if models.Cart.get((models.Cart.user_email == current_user.id) & (models.Cart.product_id == product_id)):
            print('1')
            prod = models.Cart.get((models.Cart.user_email == current_user.id) & (models.Cart.product_id == product_id))
            q = models.Cart.update(count = prod.count + 1).where((models.Cart.user_email == current_user.id) & (models.Cart.product_id == product_id))
            q.execute()
    except models.Cart.DoesNotExist:
        print('2')
        models.Cart.add_product(
            user_email_id= current_user.id,
            product_id_id= product_id,
            count = 1
        )
    return redirect(url_for('checkout'))

@app.route("/delete_to_cart/<int:product_id>/", methods=('GET', 'POST'))
@login_required
def delete_to_cart(product_id):
    try:
        prod = models.Cart.get((models.Cart.user_email == current_user.id) & (models.Cart.product_id == product_id))
        prod.delete_instance()
    except models.Cart.DoesNotExist:
        pass
    return redirect(url_for('cart_index'))


@app.route("/add_to_cart/<int:product_id>/", methods=('GET', 'POST'))
@login_required
def add_to_cart(product_id):
    try:
        if models.Cart.get((models.Cart.user_email == current_user.id) & (models.Cart.product_id == product_id)):
            print('1')
            prod = models.Cart.get((models.Cart.user_email == current_user.id) & (models.Cart.product_id == product_id))
            q = models.Cart.update(count = prod.count + 1).where((models.Cart.user_email == current_user.id) & (models.Cart.product_id == product_id))
            q.execute()
    except models.Cart.DoesNotExist:
        print('2')
        models.Cart.add_product(
            user_email_id= current_user.id,
            product_id_id= product_id,
            count = 1
        )

    flash("Successfully added to cart!")
    return redirect(url_for('cart_index'))


@app.route("/cart/", methods=('GET', 'POST'))
@login_required
def cart_index():
    products = models.Product.select(models.Cart, models.Product).join(models.Cart).annotate(models.Cart, models.Cart.count).where(models.Cart.user_email == current_user.id)
    return render_template('cart.html', user=current_user, products=products)

@app.route("/checkout/", methods=('GET', 'POST'))
@login_required
def checkout():
    products = {}
    totalprice = 0
    try:
        products = models.Product.select(models.Cart, models.Product).join(models.Cart).annotate(models.Cart, models.Cart.count).where(models.Cart.user_email == current_user.id)
        for prod in products:
            totalprice += prod.buy_price * prod.cart.count
    except models.Cart.DoesNotExist:
        pass

    if request.method == 'POST':
        fullname = request.form['fullname']
        hostelname = request.form['hostelname']
        mobile_no = request.form['mobileno']
        payment_options = request.form['pay']

        for product in products:
            models.BuyHistory.add_history(
                buyer = current_user.id,
                product_id = product.id,
                product_name = product.name,
                product_quantity = product.cart.count,
                buyer_name = fullname,
                buyer_address = 'Hostel Name: ' + hostelname,
                mobile_no = mobile_no,
                payment_option=payment_options,
            )

        try:
            ins = models.Cart.delete().where(models.Cart.user_email_id == current_user.id)
            ins.execute()
        except models.Cart.DoesNotExist:
            pass

        flash("You Order has been placed Successfully!", "Success")
        return redirect(url_for('index'))

    return render_template("checkout.html", user=current_user, products=products, totalprice=totalprice)


@app.route("/search", methods=('POST', 'GET'))
def search():
    query = request.args.get('keyword')
    print(query)
    products = models.Product.select().where(models.Product.title.regexp(query.replace(' ', '|')))
    return render_template('search.html', user=current_user, products=products , query=query)

@app.route('/product_images')
def uploaded_file():
    filename = request.args.get('image')
    return send_from_directory(os.path.join(app.instance_path, app.config['UPLOADED_IMAGES_DEST']), filename)

@app.route('/banner/<filename>')
def banner(filename):
    return send_from_directory(os.path.join(app.instance_path, app.config['banner_url']), filename)

def upload_file(file):
    try:
        file.save(file.filename)
    except:
        flash("Error Occured!!!!")

@app.route('/sitemap.xml')
def sitemap_file():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/db.db')
@login_required
def get_db():
    if current_user.is_admin:
        return send_from_directory(app.root_path, 'shop.db')
    else:
        return redirect(url_for('index'))


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = forms.EmailForm()
    if form.validate_on_submit():
        user = models.User.get(models.User.email == form.email.data)
        token = ts.dumps(user.email, salt='recover-key')
        recover_url = url_for(
            'reset_with_token',
            token=token,
            _external=True)

        msg = Message('Password reset requested', sender = 'support@redgingger.com', recipients = [form.email.data])
        msg.html = """
        Hello {0},
        Password reset request has been initiated for you account to reset the password please click the link below
        <a href='{1}'>{2}</a>
        """.format(user.full_name, recover_url, recover_url)
        mail.send(msg)
        return redirect(url_for('index'))
    return render_template('reset.html', form=form, user=current_user)


@app.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        abort(404)

    form = forms.PasswordForm()

    if form.validate_on_submit():
        user = models.User.get(models.User.email == email)

        q = models.User.update(password=generate_password_hash(form.password.data)).where(models.User.email == email)
        q.execute()

        return redirect(url_for('login'))

    return render_template('reset_with_token.html', form=form, token=token, user=current_user)


@app.route('/dashboard/reviews')
def add_review_dashboard():
        return render_template("dashboard/html/reviews.html", user=current_user, app=app, reviews=models.Review)

@app.route('/dashboard/reviews/edit/<id>', methods=['GET', 'POST'])
def edit_review_dashboard(id):
    if current_user.is_admin:
        review = models.Review.get(models.Review.id == id)
        form = forms.new_review(obj=review)
        if form.validate_on_submit():
            q = models.Review.update(
                user = form.user.data,
                order_id = form.order_id.data,
                text = form.text.data
            ).where(models.Review.id == id)
            q.execute()
        return render_template("dashboard/html/review/edit.html", user=current_user, form=form)
    else:
        return redirect(url_for('index'))

@app.route('/dashboard/reviews/delete/<id>', methods=['GET'])
def delete_review_dashboard(id):
    if current_user.is_admin:
        product_ins = models.Review.get(models.Review.id == id)
        product_ins.delete_instance()
        return redirect(url_for('add_review_dashboard'))
    else:
        return redirect(url_for('index'))

@app.route('/dashboard/reviews/new/', methods=('GET', 'POST'))
@login_required
def dashboard_review_new():
    if current_user.is_admin:
        form = forms.new_review()
        if form.validate_on_submit():
            models.Review.add_review(
                user = form.user.data,
                order_id = form.order_id.data,
                text = form.text.data
            )
            return redirect(url_for('add_review_dashboard'))
        return render_template("dashboard/html/product/new.html", user=current_user, form=form)
    else:
        return redirect(url_for('index'))


@app.route('/reviews/')
def all_reviews():
    return render_template('reviews.html', user=current_user, rev=models.Review)
