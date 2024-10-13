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