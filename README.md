
# Pepper Ecommerce Website

Pepper is an end-to-end ecommerce website that specializes in selling women's vintage model dresses. The website has a user-facing side and a custom-made admin side, both of which are fully responsive and have a range of functionalities.


## Acknowledgements

 - [AWS EC2 instance setup](https://youtu.be/cc0Hf_I3ykY)
 - [Set Up Django with Postgres, Nginx, and Gunicorn on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-20-04)
 - [AWS RDS PostgreSQL Instance for Django](https://django.how/resources/aws-rds-postgresql-instance-for-django-project/#:~:text=AWS%20RDS%20PostgreSQL%20Instance%20for%20Django%20Project%20Django.How,...%206%20Failed%20building%20wheel%20for%20psycopg2%20)
 - [Storing Django Static and Media Files on Amazon S3](https://testdriven.io/blog/storing-django-static-and-media-files-on-amazon-s3/#:~:text=Storing%20Django%20Static%20and%20Media%20Files%20on%20Amazon,6%20Private%20Media%20Files%20...%207%20Conclusion%20)
 - [Secure Nginx with Lets Encrypt on Ubuntu 20.04 with Certbot](https://youtu.be/R5d-hN9UtpU)

## User Side Functionalities
* User login and registration.
* Login with OTP and phone number verification for registration
* Search functionality
* Dress variations by size and color
* Category and subcategory browsing
* Brand-wise category browsing
* Payment options including PayPal and Razorpay
* Cart management
* Order management
* Coupon management
* Address management
* Profile management for users, including the ability to change address and password
* Cancel orders
* Invoice download
* Return option

## Admin Side Functionalities
* Admin login and registration
* Order management
* Sales overview using charting tools such as Chart.js
* Sales report management
* Banner management
* Offer management
* Coupon management
* Category and subcategory management
* Product management
* User management

## Technologies and Tools Used
* Django
* PostgreSQL
* HTML, CSS, and JavaScript
* Bootstrap
* Ajax and XHTTP
* NGINX
* Charts
* GitHub
* AWS (EC2, RDS, and S3 bucket)
* Twilio
* PayPal and Razorpay
* Custom decorators and slugs

## Hosting and Deployment
The website is hosted on AWS EC2 and the database is hosted on AWS RDS (PostgreSQL). The code for the project is available on GitHub.


## Run Locally
Clone the project
```bash 
https://github.com/AswanthAnu/django_project.git
```
Go to the project directory
```bash 
    cd ecom
```
Install dependencies
```bash
    pip install -r requirements.txt
```
Start the server
```bash 
    cd ecom
    python manage.py runserver - Windows OS
    python3 manage.py runserver - MAC OS, Linux OS
```
## Appendix

Before Running the project make sure that you are in virtual env


## Environment Variables

To run this project, you will need to add the following enivronment variables to your .env file
`SECRET KEY` - Django Secret Key
## PayPal
`ACCOUNT_SID` `AUTH_TOKEN` `SERVICE`
## Razorpay
`RAZOR_KEY_ID` `RAZOR_KEY_SECRET` `OPENEXCHANGEKEY`
## AWS S3 Static Files Configuration
`AWS_ACCESS_KEY_ID` `AWS_SECRET_ACCESS_KEY` `AWS_STORAGE_BUCKET_NAME` 


### Walk through the site

**Landing Page**
![pepper1](https://user-images.githubusercontent.com/101197982/210614795-17a597bf-af3a-4104-b0b9-6aca68b82dac.png)

**Store and individual product details**
![Peppercol1](https://user-images.githubusercontent.com/101197982/210614966-528a64f5-b001-4a3e-b54c-63961f2dbf89.jpg)

**Cart and checkout**
![peppercol2](https://user-images.githubusercontent.com/101197982/210615033-68ae34c1-558c-425a-9afe-a780b5948643.jpg)

**Coupon, Order, Order details**
![peppercol3](https://user-images.githubusercontent.com/101197982/210615168-d0d2a547-3569-4004-9c5b-95631006e514.jpg)

**Admin Side**
![peppercol4](https://user-images.githubusercontent.com/101197982/210615209-f9ccad1c-68be-4385-937e-b5a99dc0818b.jpg)
