from flask import Flask, render_template, url_for, request, redirect, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_db_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession() 

'''Show restaurants'''

@app.route('/')
@app.route('/restaurants/')
def printRestaurants():
	restaurant = session.query(Restaurant)
	return render_template('restaurants.html', restaurant=restaurant)

'''Create new restaurants'''

@app.route('/restaurants/new/', methods=['GET','POST'])
def newRestaurantItem():
	if request.method == 'POST':
	  newItem = Restaurant(name = request.form['name'])
	  session.add(newItem)
	  session.commit()
	  return redirect(url_for('printRestaurants'))
	else:
	  return render_template('newrestaurant.html')

'''Edit restaurants'''

@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurantItem(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

	if request.method == 'POST':
	  restaurant.name = request.form['name']
	  session.add(restaurant)
	  session.commit()
	  return redirect(url_for('printRestaurants'))
	else:
	  return render_template('editrestaurant.html', restaurant=restaurant)

'''Delete restaurants'''

@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurantItem(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

	if request.method == 'POST':
	  session.delete(restaurant)
	  session.commit()
	  return redirect(url_for('printRestaurants'))
	else:
	  return render_template('deleterestaurant.html', restaurant=restaurant)

'''Show the menu for a restaurant'''

@app.route('/restaurants/<int:restaurant_id>/')
def printMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	return render_template('menu.html', restaurant=restaurant, items=items)

#	output = ''
#	for i in items:
#		output += i.name + '<br>'
#		output += i.price + '<br>'
#		output += i.description + '<br>'
#		output += '<br>'
#	return output

'''Create new menu'''

@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	if request.method == 'POST':
	  newItem = MenuItem(name = request.form['name'], price = request.form['price'], description = request.form['description'], restaurant_id = restaurant_id)
	  session.add(newItem)
	  session.commit()
	  return redirect(url_for('printMenu', restaurant_id=restaurant_id))
	else:
	  return render_template('newmenuitem.html', restaurant_id=restaurant_id)


'''Edit the menu'''

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
#	return "page for edit menu item"

	item = session.query(MenuItem).filter_by(id=menu_id).one()

	if request.method == 'POST':
	  item.name = request.form['name']
	  item.description = request.form['description']
	  item.price = request.form['price']
	  item.course = request.form['course']
	  session.add(item)
	  session.commit()
	  return redirect(url_for('printMenu', restaurant_id = restaurant_id))
	else:
	  return render_template('editmenuitem.html', id=menu_id, item=item, restaurant_id=restaurant_id)


'''Delete the menu'''

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
#	return "page to delete menu item"

	item = session.query(MenuItem).filter_by(id=menu_id).one()

	if request.method == 'POST':
	  session.delete(item)
	  session.commit()
	  return redirect(url_for('printMenu', restaurant_id = restaurant_id))
	else:
	  return render_template('deletemenuitem.html', id=menu_id, item=item, restaurant_id=restaurant_id)



if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
