I have been a little sidetracked so the app is still in a rather primitive state. There are a couple of base functionalities that can be tested, such as creating an account, asking questions on a question board and leaving reviews for the website. More functionality will be added until the next review as well as improved quality and security for the code. 

In order to test the app the repository has to be cloned. A .env file will also have to be created with a custom SECRET_KEY and a DATABASE_URL. The database so far will have to include 3 different databases:
1. accounts (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, role UNIQUE)
2. questions (id SERIAL PRIMARY KEY, question TEXT, user_id INTEGER REFERENCES accounts)
3. reviews (id SERIAL PRIMARY KEY, review TEXT, rating INTEGER, user_id INTEGER REFERENCES accounts)
