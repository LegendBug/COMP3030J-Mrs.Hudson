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

The company is facing several challenges regrading sustainability, which are
+ **Inefficiency of inventory management**
  + Holmes Company's inventory management is still at the stage of manual recording, leading to chaotic material circulation, inability to timely recover leased materials, and difficulties in duplicate procurement and equipment damage statistics.
+ **Serious waste of energy resources**
  + The company lacks dynamic monitoring means for the use of water and electricity resources, unable to adjust consumption according to the flow of people and the number of displays, resulting in unnecessary waste of energy and environmental burden.
+ **Low utilization of venue space**
  + To simplify management processes, companies often allocate venue space that exceeds customer needs, leading to low utilization rates and indirectly causing a waste of resources.
+ **Inefficient reservation system**
  + Currently, event organizers need to make reservations for exhibitions with Holmes Company via telephone. This reservation mechanism significantly increases the management costs of Holmes and reduces the operational efficiency of the company's business.

## Project Solution

According to the challenges stated, the system should satisfy the following basic requirements:

+ Efficient venue reservation
+ Flexible layout design
+ Convenient material management
+ Transmission of various types of messages

To address the outlined issues, we developed a resource management system called **Mrs. Hudson**, serving as a comprehensive manager for the exhibition center to minimize waste and optimize asset and energy usage. The system features an online repository where exhibitors can find and select needed items like sound systems and lighting, boosting item reusability and the company’s sustainability. The Holmes Exhibition Company can supply these items based on repository stock levels, ensuring efficient use. The system also enables its user to manage or apply various venues, exhibitions and booths as well as editing their layouts, during which they can communicate efficiently with a built-in user-friendly messaging system. Additionally, energy management of the system can adapt to the exhibition center’s fluctuating foot traffic, increasing air conditioning during busy times and reducing energy use during quieter periods, thus conserving resources.

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
+ Konva.js
+ Vue
+ PyTorch

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
    ```

3. Run the project using the following command:

    ```shell
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
