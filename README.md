# Authorisation_Code_Generator

This Merchandise Management Webapp enables branch stores to perform inter-branch stock transfers in a self-service format by generating trackable authorisation codes for each transaction in a fast, reliable, and efficient manner.

The backend follows modern Object-Oriented Programming principles, with Flask integrated to provide a neat & user-friendly frontend.


The Administrator can: 

1. Generate new Authorisation codes  🗂️
2. Search & Filter for any past Authorisation codes and their associated branch transfers 🔍
3. Upload CSV files containing new merchandise product metadata 📤
4. Manage Users/branch stores from a dedicated Admin Portal (includes User Authentication) 👥🛠️
5. Visualize inter-branch merchandise transfer analytics 📈

Branch Stores can: 

1. Request and Retrieve Authorization Codes in a Self-Service manner 🔑
2. Access and review historical records of authorization codes retrieved 📜

## Table of Contents
1. [Database Schema](#database-schema)
2. [Installation](#installation)
3. [Usage](#usage)


## Database Schema

Below is the **Project's Database Schema**:

![Database Schema](/dbschema.png)

## Installation

Follow these steps to install the Webapp:

1. Clone the repository (Set up your own virtual environment if necessary):

   ```bash
   git clone https://github.com/emaseruka1/Authorisation_Code_Generator.git

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt

## Usage

1.  Start the app by running:

    ```bash

    python app/main.py

2. Go to your localhost with the following url. (I advise that you use Google Chrome):

    http://localhost:5555

3. Login as Admin with these details:

    🆔 Store Code: 0
   
    🔑 Password: warehouse1
