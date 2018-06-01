'''
All forms for the website
'''

from flask_uploads import IMAGES, UploadSet
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, PasswordField, StringField, TextAreaField
from wtforms.validators import (DataRequired, Email, Length, ValidationError,
                                equal_to, regexp)

import models

images = UploadSet('images', IMAGES)


def email_exists(form, field):
    if models.User.select().where(models.User.email == field.data).exists():
        raise ValidationError('User with email already exists')

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(),Email(),email_exists])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=6), equal_to('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    mobile_no = IntegerField('Mobile No', validators=[DataRequired()])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(),Email()])
    mobile_no = IntegerField("Mobile No", validators=[DataRequired()])
    message = TextAreaField('Your Message', validators=[DataRequired()])

class new_product_form(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    image_1 = FileField('Smallest Image', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    image_2 = FileField('Medium Image', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    image_3 = FileField('Large Image', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    count = IntegerField('Product Count', validators=[DataRequired()])
    actual_price = IntegerField('Product Price')
    off_percent = IntegerField('Off Percent %')
    buy_price = IntegerField('Buy Price')
    style = StringField('Style')
    lenses_color = StringField('Lenses Color')
    frame_color = StringField('Frame Color')
    brand_name = StringField('Brand Name')
    lenses_material = StringField('Lenses Material')
    frame_material = StringField('Frame Material')
    usage = StringField('Usage')
    packaging = StringField('Packaging')
    uv_protection = StringField('UV Protection')
    model_no = StringField('Model No.')
    suitable_for = StringField('Suitable For')
    size = StringField('Size')
    ideal_for = StringField('Ideal For')
    typ_e = StringField('Type')
    features = StringField('Features')
    case_type = StringField('Case Type')
    dimensions_bridgesize = StringField('Bridge Size (dimensions)')
    dimensions_hrizontal_width = StringField('Horizontal Width (dimensions)')
    dimensions_frame_arm_lenght = StringField('Frame Arm Lenghth (dimensions)')
    weight = StringField('Weight')
    other_details = TextAreaField('Other Details')

class edit_product_form(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    image_1 = FileField('Smallest Image', validators=[ FileAllowed(images, 'Images only!')])
    image_2 = FileField('Medium Image', validators=[FileAllowed(images, 'Images only!')])
    image_3 = FileField('Large Image', validators=[FileAllowed(images, 'Images only!')])
    count = IntegerField('Product Count', validators=[DataRequired()])
    actual_price = IntegerField('Product Price')
    off_percent = IntegerField('Off Percent %')
    buy_price = IntegerField('Buy Price')
    style = StringField('Style')
    lenses_color = StringField('Lenses Color')
    frame_color = StringField('Frame Color')
    brand_name = StringField('Brand Name')
    lenses_material = StringField('Lenses Material')
    frame_material = StringField('Frame Material')
    usage = StringField('Usage')
    packaging = StringField('Packaging')
    uv_protection = StringField('UV Protection')
    model_no = StringField('Model No.')
    suitable_for = StringField('Suitable For')
    size = StringField('Size')
    ideal_for = StringField('Ideal For')
    typ_e = StringField('Type')
    features = StringField('Features')
    case_type = StringField('Case Type')
    dimensions_bridgesize = StringField('Bridge Size (dimensions)')
    dimensions_hrizontal_width = StringField('Horizontal Width (dimensions)')
    dimensions_frame_arm_lenght = StringField('Frame Arm Lenghth (dimensions)')
    weight = StringField('Weight')
    other_details = TextAreaField('Other Details')


class Checkout_form(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    room_no = StringField('Room no', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    mobile = IntegerField("Mobile No", validators=[DataRequired()])

class new_password(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=6), equal_to('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])

class new_review(FlaskForm):
    user = StringField('User')
    order_id = StringField('Order-ID')
    text = TextAreaField('Review')
