'''
    Shopping Project Database
    -----------------------------------------------------------------
    Database Model For Shopping Site
    author : Nitesh Kumar Niranjan <niteshkumarniranjan@gmail.com>
'''

import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *
from playhouse.migrate import SqliteMigrator
import uuid

# Default database
DATABASE = SqliteDatabase('shop.db')
migrator = SqliteMigrator(DATABASE)


# User Table
class User(UserMixin, Model):
    """App Users Table"""
    full_name = CharField()
    email = CharField(unique=True)
    password = CharField(max_length=100)
    mobile_no = CharField()
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)


    class Meta:
        database = DATABASE
  
    @classmethod
    def create_user(cls, full_name, email, password, mobile_no, admin=False):
        try:
            cls.create(
                full_name = full_name,
                email = email,
                password = generate_password_hash(password),
                mobile_no = mobile_no,
                is_admin = admin
            )
        except IntegrityError:
            raise ValueError("User already exists")


class Product(Model):
    """Products Table"""
    name = CharField()
    title = CharField()
    image_1 = CharField()
    image_2 = CharField()
    image_3 = CharField()
    count = IntegerField()
    actual_price = IntegerField(null=False)
    off_percent = IntegerField(null=False)
    buy_price = IntegerField(null=False)
    style = CharField()
    lenses_color = CharField()
    frame_color = CharField()
    brand_name = CharField()
    lenses_material = CharField()
    frame_material = CharField()
    usage = CharField()
    packaging = CharField()
    uv_protection = CharField()
    model_no = CharField()
    suitable_for = CharField()
    size = CharField()
    ideal_for = CharField()
    typ_e = CharField()
    features = CharField()
    case_type = CharField()
    dimensions_bridgesize = CharField()
    dimensions_hrizontal_width = CharField()
    dimensions_frame_arm_lenght = CharField()
    weight = CharField() 
    other_details = TextField()
    published_at = DateTimeField(default=datetime.datetime.now)


    class Meta:
        database = DATABASE
        order_by = ('-published_at',)

    @classmethod
    def add_product(cls, name, image_1, image_2, image_3, count, actual_price, off_percent, buy_price, 
                            style, lenses_color, frame_color, brand_name, lenses_material, frame_material, usage, packaging,
                            uv_protection, model_no, suitable_for, size, ideal_for, typ_e, features, case_type, dimensions_bridgesize,
                            dimensions_hrizontal_width, dimensions_frame_arm_lenght, weight, other_details):
        try:
            _title = name.replace(" ", "_").lower()
            cls.create(
                name = name, 
                title = _title,
                image_1 = image_1, 
                image_2 = image_2, 
                image_3 = image_3,
                count = count,
                actual_price = actual_price, 
                off_percent = off_percent, 
                buy_price = buy_price, 
                style = style,
                lenses_color = lenses_color, 
                frame_color = frame_color, 
                brand_name = brand_name, 
                lenses_material = lenses_material, 
                frame_material = frame_material, 
                usage = usage, 
                packaging = packaging,
                uv_protection = uv_protection, 
                model_no = model_no, 
                suitable_for = suitable_for, 
                size = size, 
                ideal_for = ideal_for, 
                typ_e = typ_e, 
                features = features, 
                case_type = case_type, 
                dimensions_bridgesize = dimensions_bridgesize,
                dimensions_hrizontal_width = dimensions_hrizontal_width, 
                dimensions_frame_arm_lenght = dimensions_frame_arm_lenght, 
                weight = weight, 
                other_details = other_details,
            )
        except IntegrityError:
            raise ValueError("Some Error Happened")


class Comment(Model):
    user = ForeignKeyField(User, related_name='user_comment')
    product = ForeignKeyField(Product, related_name='products_comment')
    text = TextField()
    rating = IntegerField()
    comment_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE

    @classmethod
    def add_comment(cls, user, product, text, rating):
        try:
            cls.create(
                user = user,
                product = product, 
                text = text,
                rating = rating
            )
        except IntegrityError :
            raise ValueError("Some Error Happened")

class Cart(Model):
    user_email = ForeignKeyField(User, related_name='carts')
    product_id = ForeignKeyField(Product, related_name='products')
    count = IntegerField()
    
    class Meta:
        database = DATABASE

    @classmethod
    def add_product(cls, user_email_id, product_id_id, count=1):
        try:
            cls.create(
                user_email_id=user_email_id,
                product_id_id=product_id_id,
                count=count
            )
        except IntegrityError:
            raise ValueError("Some Error Happened")



class BuyHistory(Model):
    """Item Buying History"""
    order_id = CharField(max_length=50, unique=True)
    product_id = ForeignKeyField(Product, related_name='product')
    buyer = ForeignKeyField(User, related_name='customer')
    product_name = CharField()
    buyer_name = CharField()
    mobile_no = IntegerField()
    payment_option = CharField()
    product_quantity = IntegerField()
    buyer_address = TextField()
    buy_time = DateTimeField(default=datetime.datetime.now)
    status = CharField()
    delivered = BooleanField()
    deliverTime = DateTimeField(null = True, default = datetime.datetime.now)


    class Meta:
        database = DATABASE
        order_by = ('buy_time',)
    
    @classmethod
    def add_history(cls, buyer, product_id, product_name, product_quantity, buyer_name, buyer_address, mobile_no, payment_option, status="Initiated", delivered=False):
        cls.create(
            order_id = str(uuid.uuid4()),
            buyer = buyer,
            product_id = product_id,
            product_name = product_name,
            product_quantity = product_quantity,
            buyer_name = buyer_name,
            buyer_address = buyer_address,
            mobile_no = mobile_no,
            payment_option = payment_option,
            status = status,
            delivered=delivered
        )


class Review(Model):
    user = CharField()
    order_id = CharField()
    text = TextField()
    comment_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE
    
    @classmethod
    def add_review(cls, user, order_id, text):
        try:
            cls.create(
                user = user,
                order_id = order_id, 
                text = text
            )
        except IntegrityError :
            raise ValueError("Some Error Happened")

class Banner(Model):
    link = CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def add_banner(cls, link):
        try:
            cls.create(
                link = link,
            )
        except IntegrityError :
            raise ValueError("Some Error Happened")


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Product, Cart, BuyHistory, Comment, Review, Banner], safe=True)
    DATABASE.close()
