<div align="center" id="madewithlua">
  <img
    src="https://github.com/LegendBug/COMP3030J-Hudson/blob/main/hudson-logo.png"
    width="125"
    height="125"
  />
</div>
<h1 align="center">Mrs. Hudson</h1>

**H.U.D.S.O.N.** stands for **Holistic Utility Deployment & Sustainability Overseeing Network**.

It is an internal resource management system aimed to boost sustainability of exhibition centers developed for COMP3030J Software Engineering Project 2.

## Project Background

Holmes Exhibition Company is a company specializes in conference, exhibition, and event planning and organization. It provides comprehensive conference planning and organization services, including determining conference themes, designing agendas, inviting guests, booking venues, rent- ing equipment, and managing conference affairs. It tailor customized solutions according to clients’ needs and budgets, coordinating all details to ensure smooth conference proceedings.

Its primary service is exhibition design and construction: the company is responsible for the overall planning and design of exhibition events, including booth layout, exhibition content planning, exhibit design, and exhibition construction. It offers the creative designs based on client requirements and exhibition themes, utilizing various professional equipment and materials for booth construction to create attractive and impactful exhibition spaces.

## Project Solution

To address the outlined issues, we’re developing a resource management system called **Mrs. Hudson**, serving as a comprehensive manager for the exhibition center to minimize waste and optimize asset and energy usage. The system will feature an online repository where exhibitors can find and select needed items like sound systems and lighting, boosting item reusability and the company’s sustainability. The Holmes Exhibition Company will supply these items based on repository stock levels, ensuring efficient use. Additionally, energy management will adapt to the exhibition center’s fluctuating foot traffic, increasing air conditioning during busy times and reducing energy use during quieter periods, thus conserving resources.

## Functionalities

+ Graphical Venue Layout Management
+ Venue, Exhibition & Booth Management
+ Venue Statistics Analysis
+ Venue Inventory Management
+ AI Copilot for User Accessibility
+ Internal Communication System
+ User Management

## Project Details

### Tech Stack

+ Django
+ JQuery
+ Bootstrap 5
+ Konva.js *(for the Layout module)*
+ Vue *(for the Layout module)*
+ PyTorch *(for the Statistics/Watson Overseer module)*

### Entity-relationship Model for the Database Schema

<img src="https://github.com/LegendBug/COMP3030J-Hudson/blob/main/er-diagram.png" alt="Entity-Relationship Diagram" style="zoom:100%;" />

## Deployment

### Recommended Environment

+ **Python 3.11**
+ **MySQL 8.x**

### Project Setup

1. Install all required Python packages by run this command in your terminal:

    ```shell
    pip install -r requirements.txt
    ```

2. Create a database schema called `hudson` in your RDBMS and run the following commands:

    ``` shell
    # Generate migration files:
    python manage.py makemigrations
    # Execute migration:
    python manage.py migrate
    # Run the server:
    python manage.py runserver
    ```

Note that before running the project for the first time, you need to create a `.env` file in the root directory of your project. Format the file as shown below, replacing `your_username` and `your_password` with your actual RDBMS settings and `your_openai_api_key` with your own OpenAI API Key:

```text
DB_HOST='localhost'
DB_PORT='3306'
DB_USERNAME='your_username'
MYSQL_ROOT_PASSWORD='your_password'
MYSQL_DATABASE='hudson'
OPENAI_API_KEY='your_openai_api_key'
```
