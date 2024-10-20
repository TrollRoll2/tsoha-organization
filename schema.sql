 CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role
 );

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    question TEXT,
    user_id INTEGER REFERENCES accounts,
    approved BOOLEAN DEFAULT FALSE
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    review TEXT,
    rating INTEGER,
    user_id INTEGER REFERENCES accounts,
    approved BOOLEAN DEFAULT FALSE
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    eventname TEXT NOT NULL, 
    event_date DATE NOT NULL, 
    description TEXT, 
    creator_id INTEGER, 
    FOREIGN KEY (creator_id) REFERENCES accounts(id)
); 

CREATE TABLE answers (
    id SERIAL PRIMARY KEY, 
    answer TEXT NOT NULL, 
    question_id INT REFERENCES questions(id), 
    responder INT REFERENCES accounts(id)
);