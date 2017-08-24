from flask import (Flask, render_template, url_for,
                   request, redirect, jsonify, flash, Markup)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy_db_setup import Base, Restaurant, MenuItem, User

# imports for oAuth 2.0
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('/var/www/catalog/flaskapp_menu/client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Restaurant menu app"

# engine = create_engine('sqlite:///restaurantmenuwithusers.db')
engine = create_engine('postgresql://menu:menu@localhost/menu')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


'''Login'''


@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32)
    )
    login_session['state'] = state
    return render_template('login.html', STATE=state)

'''Login Google connect route'''


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 527)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # if user doesn't exist add to db

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = "<h1>Welcome, " + login_session['username'] + "!</h1>" \
             "<img src='" + login_session['picture'] + "'" \
             "style='" \
             "width: 300px;" \
             "height: 300px;" \
             "border-radius: 150px;" \
             "-webkit-border-radius: 150px;" \
             "-moz-border-radius: 150px;'>"
    flash("Logged in as %s" % login_session['username'])
    print "done!"
    return output

'''User helper functions'''


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

'''Logout google connect route'''


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('User not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400)
        )
        response.headers['Content-Type'] = 'application/json'
        return response

'''Show restaurants'''


@app.route('/')
@app.route('/restaurants/')
def printRestaurants():
        restaurant = session.query(Restaurant).order_by(asc(Restaurant.name))

        if 'username' not in login_session:
            return render_template(
                                  'publicrestaurants.html',
                                  restaurant=restaurant)
        else:
            return render_template('restaurants.html', restaurant=restaurant)

'''Show restaurants in JSON'''


@app.route('/restaurants/JSON/')
def printRestaurantsJSON():
        restaurant = session.query(Restaurant)
        return jsonify(Restos=[i.serialize for i in restaurant])

'''Create new restaurants'''


@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurantItem():
        if 'username' not in login_session:
            return redirect('/login')
        if request.method == 'POST':
            newItem = Restaurant(
                      name=request.form['name'],
                      user_id=login_session['user_id']
                      )
            session.add(newItem)
            session.commit()
            return redirect(url_for('printRestaurants'))
        else:
            return render_template('newrestaurant.html')

'''Edit restaurants'''


@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurantItem(restaurant_id):
        if 'username' not in login_session:
            return redirect('/login')

        restaurant = session.query(Restaurant).filter_by(id=restaurant_id) \
                            .one()

        if restaurant.user_id != login_session['user_id']:
            value = Markup(
                    "<script>function checkFunction() {"
                    "alert('You do not have permission to edit this"
                    "restaurant.');} </script>"
                    "<body onload='checkFunction()'>")
            return value

        if request.method == 'POST':
            restaurant.name = request.form['name']
            session.add(restaurant)
            session.commit()
            return redirect(url_for('printRestaurants'))
        else:
            return render_template(
                'editrestaurant.html',
                restaurant=restaurant)

'''Delete restaurants'''


@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurantItem(restaurant_id):
        if 'username' not in login_session:
            return redirect('/login')

        restaurant = session.query(Restaurant).filter_by(id=restaurant_id) \
                            .one()

        if restaurant.user_id != login_session['user_id']:
            value = Markup(
              "<script>function checkFunction() {"
              "alert('You do not have permission to delete this"
              "restaurant.');} </script>"
              "<body onload='checkFunction()'>")
            return value

        if request.method == 'POST':
            session.delete(restaurant)
            session.commit()
            return redirect(url_for('printRestaurants'))
        else:
            return render_template(
                'deleterestaurant.html', restaurant=restaurant)

'''Show the menu for a restaurant'''


@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu')
def printMenu(restaurant_id):
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id) \
                            .one()

        creator = getUserInfo(restaurant.user_id)
        loginuser = login_session['user_id']

        items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)

        if 'username' not in login_session or creator.id != loginuser:
            return render_template(
                    'publicmenu.html', items=items, restaurant=restaurant,
                    creator=creator, loginuser=loginuser)
        else:
            return render_template(
              'menu.html', restaurant=restaurant,
              items=items, creator=creator
            )

'''Show the menu for a restaurant in JSON'''


@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def printMenuJSON(restaurant_id):
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id) \
                            .one()
        items = session.query(MenuItem) \
                       .filter_by(restaurant_id=restaurant_id).all()
        return jsonify(MenuItems=[i.serialize for i in items])

'''Create new menu'''


@app.route('/restaurants/<int:restaurant_id>/menu/new/',
           methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
        if 'username' not in login_session:
            return redirect('/login')

        loginuser = login_session['user_id']

        if request.method == 'POST':
            newItem = MenuItem(
                name=request.form['name'], price=request.form['price'],
                description=request.form['description'],
                course=request.form['course'],
                restaurant_id=restaurant_id, user_id=loginuser
            )
            session.add(newItem)
            session.commit()
            return redirect(url_for('printMenu', restaurant_id=restaurant_id))
        else:
            return render_template(
                'newmenuitem.html', restaurant_id=restaurant_id
            )


'''Edit the menu'''


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
        if 'username' not in login_session:
            return redirect('/login')

        item = session.query(MenuItem).filter_by(id=menu_id).one()

        if item.user_id != login_session['user_id']:
            value = Markup(
              "<script>function checkFunction() {"
              "alert('You do not have permission to edit this"
              " menu item.');} </script>"
              "<body onload='checkFunction()'>")
            return value

        if request.method == 'POST':
            item.name = request.form['name']
            item.description = request.form['description']
            item.price = request.form['price']
            item.course = request.form['course']
            session.add(item)
            session.commit()
            return redirect(url_for('printMenu', restaurant_id=restaurant_id))
        else:
            return render_template(
                'editmenuitem.html', id=menu_id, item=item,
                restaurant_id=restaurant_id)

'''Return menu item in JSON'''


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def showMenuItemJSON(restaurant_id, menu_id):
        item = session.query(MenuItem).filter_by(id=menu_id).one()
        return jsonify(menuitemjson=item.serialize)


'''Delete the menu'''


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
        if 'username' not in login_session:
            return redirect('/login')

        item = session.query(MenuItem).filter_by(id=menu_id).one()

        if item.user_id != login_session['user_id']:
            value = Markup(
              "<script>function checkFunction() {"
              "alert('You do not have permission to delete this"
              " menu item.');} </script>"
              "<body onload='checkFunction()'>")
            return value

        if request.method == 'POST':
            session.delete(item)
            session.commit()
            return redirect(url_for('printMenu', restaurant_id=restaurant_id))
        else:
            return render_template(
                'deletemenuitem.html', id=menu_id,
                item=item, restaurant_id=restaurant_id)


if __name__ == '__main__':
        app.secret_key = 'aidencrestridge11545%&^'
        app.debug = True
        app.run(host='0.0.0.0', port=5000)
