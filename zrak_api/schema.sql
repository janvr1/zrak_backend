DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS measurements;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_type INTEGER NOT NULL DEFAULT 0,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) DEFAULT NULL UNIQUE,
    time_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    password TEXT NOT NULL
);

CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    time_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) DEFAULT NULL,
    var0 VARCHAR(255) DEFAULT NULL,
    var1 VARCHAR(255) DEFAULT NULL,
    var2 VARCHAR(255) DEFAULT NULL,
    var3 VARCHAR(255) DEFAULT NULL,
    var4 VARCHAR(255) DEFAULT NULL,
    var5 VARCHAR(255) DEFAULT NULL,
    var6 VARCHAR(255) DEFAULT NULL,
    var7 VARCHAR(255) DEFAULT NULL,
    var8 VARCHAR(255) DEFAULT NULL,
    var9 VARCHAR(255) DEFAULT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, name)
);

CREATE TABLE measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dev_id INTEGER,
    time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    var0 REAL DEFAULT NULL,
    var1 REAL DEFAULT NULL,
    var2 REAL DEFAULT NULL,
    var3 REAL DEFAULT NULL,
    var4 REAL DEFAULT NULL,
    var5 REAL DEFAULT NULL,
    var6 REAL DEFAULT NULL,
    var7 REAL DEFAULT NULL,
    var8 REAL DEFAULT NULL,
    var9 REAL DEFAULT NULL,
    FOREIGN KEY(dev_id) REFERENCES devices(id) ON DELETE CASCADE
);