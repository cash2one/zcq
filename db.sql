/* create database */
CREATE DATABASE qqzc;
/* create database users */
GRANT ALL PRIVILEGES ON qqzc.* TO 'qqzc'@'localhost' IDENTIFIED BY '123456';


/* users */
CREATE TABLE users (
    name VARCHAR(20) NOT NULL PRIMARY KEY, 
    password VARCHAR(64), 
    total INT unsigned
);

/* login table */
CREATE TABLE logins (
    id INT unsigned NOT NULL auto_increment, 
    logdate DATETIME NOT NULL, 
    ip VARCHAR(20), 
    uname VARCHAR(20), 
    PRIMARY KEY(id), 
    FOREIGN KEY(uname) REFERENCES users(name)
);

/* users phone */
CREATE TABLE userphones (
    id INT unsigned NOT NULL auto_increment,
    phone VARCHAR(20) NOT NULL,
    adate DATETIME NOT NULL, /* Add date */
    uname VARCHAR(20),
    udate DATETIME,
    total INT,
    status INT,
    PRIMARY KEY(id), /* cannot use id,phone ? */
    FOREIGN KEY(uname) REFERENCES users(name)
);

/* actions */
CREATE TABLE actions (
    id INT unsigned NOT NULL auto_increment,
    ip VARCHAR(20) NOT NULL,
    uname VARCHAR(20),
    uphone VARCHAR(20),
    uin VARCHAR(30),
    adate DATETIME NOT NULL,
    code VARCHAR(10),
    smsvc VARCHAR(10),
    region VARCHAR(20),
    trytimes INT,
    PRIMARY KEY(id),
    FOREIGN KEY(uname) REFERENCES users(name)
    /* FOREIGN KEY(uphone) REFERENCES userphones(phone) */
);

/* devices */
CREATE TABLE devices (
    dname VARCHAR(20) NOT NULL,
    password VARCHAR(64),
    ip VARCHAR(20),
    duuid VARCHAR(128),
    status INT,
    PRIMARY KEY(dname)
);

CREATE TABLE smsvc (
    id INT UNSIGNED NOT NULL auto_increment, 
    phone VARCHAR(20), 
    devip VARCHAR(20), 
    devname VARCHAR(20), 
    devsession VARCHAR(128), 
    request_time DATETIME, 
    clientip VARCHAR(20), 
    response_time DATETIME, 
    status INT, 
    code VARCHAR(20), 
    PRIMARY KEY(id)
);

CREATE TABLE uin(
    uin VARCHAR(100) NOT NULL,
    password VARCHAR(100),
    nick VARCHAR(100),
    country VARCHAR(100),
    province VARCHAR(100),
    city VARCHAR(100),
    birth VARCHAR(20),
    nongli INT,
    gender INT,
    phone VARCHAR(20),
    region VARCHAR(20),
    ip VARCHAR(20),
    dev VARCHAR(20),
    adate DATETIME,
    status INT,
    PRIMARY KEY(uin)
);

CREATE TABLE smstext(
    id INT UNSIGNED NOT NULL auto_increment,
    time DATETIME,
    sfrom VARCHAR(80),
    sto VARCHAR(80),
    text VARCHAR(10240),
    com VARCHAR(10),
    uname VARCHAR(20),
    PRIMARY KEY(id),
    FOREIGN KEY(uname) REFERENCES users(name)
);

