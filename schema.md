CREATE TABLE sqlite_sequence(name,seq);
CREATE UNIQUE INDEX username ON users (username);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL
);

CREATE TABLE bolsas (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER,
    origin TEXT,
    price INTEGER,
    grams INTEGER,
    toaster TEXT NOT NULL,
    date DATE,
    active TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);


CREATE TABLE rondas (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    prensa_id INTEGER,
    bolsa_id INTEGER,
    cost INTEGER,
    date DATETIME,
    FOREIGN KEY(bolsa_id) REFERENCES bolsas(id),
    FOREIGN KEY(prensa_id) REFERENCES prensas(id)
);

CREATE TABLE prensas (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    owner_id INTEGER,
    capacity INTEGER,
    FOREIGN KEY(owner_id) REFERENCES users(id)
);

CREATE TABLE incidencias (
    ronda_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(ronda_id) REFERENCES rondas(id)
);

