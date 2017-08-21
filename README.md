# Item catalog app

This app is part of Udacity's Full Stack Web Developer course, and is built using
1. Python and the Flask framework
2. SQLAlchemy with SQLite for development testing
3. Front-end using Bootstrap and jQuery (minimally)

## To install and run the project

1. Install [vagrant] (https://docs.vagrantup.com/v2/installation/).
2. Clone the Udacity github repo `git clone https://github.com/OscarDoc/fullstack-nanodegree-vm.git`.
3. From the command line navigate to /fullstack-nanodegree-vm/vagrant and run `vagrant up` to provision the Vagrant virtual machine.
4. Run `vagrant ssh` to log into the Vagrant virtual machine.
5. Install Python dependencies listed at the beginning of the firstflask.py file including `flask`, `sqlalchemy`, `oauth2client.cient`, `httplib2`, `json`, and `requests`.
6. Edit `Vagrantfile` and forward port 5000 from the Vagrant virtual machine to the same or another port on `localhost` so you can access and test on your computer.
7. Start the app by running `python firstflask.py` from within the Vagrant virtual machine. This app was coded using Python 2.7.6.
8. The app can be accessed from your browser at localhost:5000 or the forwarded port you specified in step 6. 

## The following files/folders are including in this repo

1. /static: JSS and CSS files
2. /templates: HTML templates to perform CRUD operations from flask
3. sqlalchemy_db_setup.py: Python file to set up the restaurantmenuwithuser.db
4. restaurantmenuwithusers.db: database file with read/write protections per user
5. lotsofmenus.py: populate database with dummy data
6. client_secrets.json: JSON formatted file with client id, client secret, and other oAuth 2.0 parameters. The file authorizes a user to obtain a token before the user authenticates for access to app.
