# Mrs. Hudson

**H.U.D.S.O.N.** stands for **Holistic Utility Deployment & Sustainability Overseeing Network**.

An internal resource management system developed for COMP3030J Software Engineering Project 2.

## Project Background

Holmes Exhibition Company is a company specializes in conference, exhibition, and event planning and organization. It provides comprehensive conference planning and organization services, including determining conference themes, designing agendas, inviting guests, booking venues, rent- ing equipment, and managing conference affairs. It tailor customized solutions according to clients’ needs and budgets, coordinating all details to ensure smooth conference proceedings.

Its primary service is exhibition design and construction: the company is responsible for the overall planning and design of exhibition events, including booth layout, exhibition content planning, exhibit design, and exhibition construction. It offers the creative designs based on client requirements and exhibition themes, utilizing various professional equipment and materials for booth construction to create attractive and impactful exhibition spaces.

## Project Solution

To address the outlined issues, we’re developing a resource management system called **Mrs. Hudson**, serving as a comprehensive manager for the exhibition center to minimize waste and optimize asset and energy usage. The system will feature an online repository where exhibitors can find and select needed items like sound systems and lighting, boosting item reusability and the company’s sustainability. The Holmes Exhibition Company will supply these items based on repository stock levels, ensuring efficient use. Additionally, energy management will adapt to the exhibition center’s fluctuating foot traffic, increasing air conditioning during busy times and reducing energy use during quieter periods, thus conserving resources.

## Deployment

### Recommended Environment

+ **Python 3.11**
+ **Django 5.x**
+ **MySQL 8.x**

### Project Setup

First, install all required Python packages by run this command in your terminal:

```shell
pip install -r requirements.txt
```

Then create a database schema called `hudson` in your RDBMS and run the following commands:

``` shell
# Generate migration files:
python manage.py makemigrations
# Execute migration:
python manage.py migrate
# Run the server:
python manage.py runserver
```

Note that before running the project for the first time, you need to create a `.env` file in the root directory of your project. Format the file as shown below, replacing `your_username` and `your_password` with your actual RDBMS settings:

```text
DB_HOST='localhost'
DB_PORT='3306'
DB_USERNAME='your_username'
MYSQL_ROOT_PASSWORD='your_password'
MYSQL_DATABASE='hudson'
```

### Additional Commands
Using these commands to create superusers and new Django apps:
``` shell
# Create a superuser:
python manage.py createsuperuser
# Create a new app:
python manage.py startapp <app_name>
```
