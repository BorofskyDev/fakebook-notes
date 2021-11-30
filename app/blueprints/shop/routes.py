from flask.templating import render_template
from stripe.api_resources import line_item
from .import bp as shop
from .models import Product, Cart
from flask import redirect, url_for, flash, session, request, current_app as app
import stripe
from flask_login import current_user
from app import db

@shop.route('/')
def index():
    stripe.api_key = app.config.get('STRIPE_TEST_SK')
    context = {
        'products' : stripe.Product.list()
    }
    return render_template('shop/index.html', **context)

@shop.route('/product/add/<id>')
def add_product(id):
    cart_item = Cart.query.filter_by(product_key=str(id)).filter_by(user_id=current_user.get_id()).first()
    if cart_item:
        cart_item.quantity +=1 
        db.session.commit()
        flash('Product added successfully', 'success')
        return redirect(url_for('shop.index'))
    cart_item = Cart(product_key=str(id), user_id=current_user.get_id(), quantity=1)
    db.session.add(cart_item)
    db.session.commit()

    flash('Product added successfully', 'success')
    return redirect(url_for('shop.index'))

@shop.route('/cart')
def cart():
    stripe.api_key = app.config.get('STRIPE_TEST_SK')
    cart_items = []
    for i in Cart.query.filter_by(user_id=current_user.get_id()).all():
        stripe_product = stripe.Product.retrieve(i.product_key)
        product_dict = {
            'product' : stripe_product,
            'price': float(stripe.Price.retrieve(stripe_product['metadata']['price_id'])['unit_amount']) / 100,
            'quantity' : i.quantity
        }
        cart_items.append(product_dict)
    context = {
        'cart' : cart_items
    }
    return render_template('shop/cart.html', **context)

@shop.route('/cart/delete')
def delete():
    p = Product.query.get(request.args.get('id'))
    cart = Cart.query.get(request.args.get('product_key'))
    try:
        cart_item = Cart.query.filter_by(user_id=current_user.id).first()
        db.session.delete(cart_item)
    except:
        flash(f"There has been an error in deleting the item. Your item has not been deleted.", 'danger')
    db.session.commit()
    flash(f'Your product has been successfully removed from your cart.', 'info')
    return redirect(url_for('shop.cart'))


@shop.route('/cart/subtotal')
def subtotal():
    stripe.api_key = app.config.get('STRIPE_TEST_SK')
    for i in Cart.query.filter_by(user_id=current_user.get_id()).all():
        stripe_product = stripe.Product.retrieve(i.product_key)
        # p = Product("price")
        # p = float(Product.price)
        p = stripe.Price.retrieve(stripe_product['metadata']['price_id'])
        c = float(i.quantity)
        # p = 15.99
        # c = 5
        print(p, c, type(p), type(c))
        pre_tax = p * float(c)
        print(pre_tax)
        return redirect(url_for('shop.cart'))


# @shop.route('/cart/update')
# def update_cart():
#     stripe.api_key = app.config.get('STRIPE_TEST_SK')
#     cart = Cart.query.get(request.args.get('product_key'))
#     for i in enumerate(cart):
#         if i == Cart.product_key:
#             cart["quantity"] = cart["quantity"] 




@shop.route('/checkout', methods=['POST'])
def create_checkout_session():
    stripe.api_key = app.config.get('STRIPE_TEST_SK')
    items = []
    for i in Cart.query.filter_by(user_id=current_user.get_id()).all():
        stripe_product = stripe.Product.retrieve(i.product_key)
        product_dict = {
            
            'price': stripe.Price.retrieve(stripe_product['metadata']['price_id']),
            'quantity': i.quantity
        }
        items.append(product_dict)
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=items,
            mode='payment',
            success_url='http://localhost:5000/success',
            cancel_url= 'http://localhost:5000/cancelled'
        )
    except Exception as error:
        return str(error)
    return redirect(checkout_session.url, code=303)


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/cancelled")
def cancelled():
    return render_template("cancelled.html")

