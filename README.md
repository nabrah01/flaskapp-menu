# Item catalog app

This app is part of Udacity's Full Stack Web Developer course, and is built using
1. Python and the Flask framework
2. SQLAlchemy with SQLite for development testing and PostgreSQL for production
3. Front-end using Bootstrap and jQuery (minimally)

## To install and run the project for staging

1. Install [vagrant] (https://docs.vagrantup.com/v2/installation/).
2. Clone the Udacity github repo `git clone https://github.com/OscarDoc/fullstack-nanodegree-vm.git`.
3. From the command line navigate to /fullstack-nanodegree-vm/vagrant and run `vagrant up` to provision the Vagrant virtual machine.
4. Run `vagrant ssh` to log into the Vagrant virtual machine.
5. Install Python dependencies listed at the beginning of the firstflask.py file including `flask`, `sqlalchemy`, `oauth2client.cient`, `httplib2`, `json`, and `requests`.
6. Edit `Vagrantfile` and forward port 5000 from the Vagrant virtual machine to the same or another port on `localhost` so you can access and test on your computer.
7. Start the app by running `python firstflask.py` from within the Vagrant virtual machine. This app was coded using Python 2.7.6.
8. The app can be accessed from your browser at localhost:5000 or the forwarded port you specified in step 6. 

## To set up the server and host this project on a public web address

1. Create an Amazon LightSail account, download the private key to your account, and change the permissions to 600

2. Login into the LightSail server using the private key or the web console

3. Update the package list and upgrade installed packages

4. Create a new user called "grader"
`$ sudo adduser grader`

5. Elevate "grader" to super user
`$ sudo nano /etc/sudoers.d/grader` and add this line to the file `$ grader ALL=(ALL:ALL) ALL`

6. On your local machine and not on the LightSail server create a new SSH keypair
`$ ssh-keygen`

7. Copy the contents of the public key by selecting text on-screen and right clicking copy

8. SSH into server as root and add public key to user `grader`
`$ sudo mkdir /home/grader/.ssh`
`$ sudo nano /home/grader/.ssh/authorized_keys` and paste publickey.pub contents here

9. Restart sshd service

10. Verify you can use the `grader` account and logout and login as `grader` using a key
`$ su grader` and then log out
`$ ssh grader@x.x.x.x -i aws.pem

11. Disable remote login of `root` user by deleting everything in the authorized keys file for root

12. Only allow connections on a non-default `SSH` port 2200, `HTTP`port 80, and `NTP` port 123

13. Require key-based `SSH` authentication and don't allow password text login

14. Install apache to run on port 80, and install PostgreSQL

15. Configure your WSGI app to display a simple text message, and then configure it to serve the Menu app


## The following files/folders are including in this repo

1. /static: JSS and CSS files
2. /templates: HTML templates to perform CRUD operations from flask
3. sqlalchemy_db_setup.py: Python file to set up the restaurantmenuwithuser.db
4. restaurantmenuwithusers.db: database file with read/write protections per user
5. lotsofmenus.py: populate database with dummy data
6. client_secrets.json: JSON formatted file with client id, client secret, and other oAuth 2.0 parameters. The file authorizes a user to obtain a token before the user authenticates for access to app. Not included here, you'll need to download your own from Google oAuth
