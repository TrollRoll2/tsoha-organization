There is still a lot left to do on the app, but as of now there are a few different base functionalities that can be tested. Creating accounts, asking questions and leaving reviews is possible for users. Admins have special priviligies and can approve questions and remove questions and reviews, as well as view all users. 

In order to test the app the repository has to be cloned. A .env file will also have to be created with a custom SECRET_KEY and a DATABASE_URL. The database so far will have to include 3 different databases:
1. accounts (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, role UNIQUE)
2. questions (id SERIAL PRIMARY KEY, question TEXT, user_id INTEGER REFERENCES accounts, approved BOOLEAN DEFAULT FALSE)
3. reviews (id SERIAL PRIMARY KEY, review TEXT, rating INTEGER, user_id INTEGER REFERENCES accounts, approved BOOLEAN DEFAULT FALSE)