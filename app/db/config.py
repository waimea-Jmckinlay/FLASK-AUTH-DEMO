#============================================================================
# Database schema and seed data configuration
#============================================================================


#----------------------------------------------------------------------------
# Table definitions
#----------------------------------------------------------------------------
# Define your tables with a name, a schema and optional seed/sample data,
# using this format, and then add the tables to the Table Registry below:
#
# class TableName:
#     NAME      = "name"
#     SCHEMA    = "CREATE TABLE name (...)"
#     SEED_DATA = "INSERT INTO name (...)" or None
#----------------------------------------------------------------------------

class UserTable:

    NAME = "users"

    SCHEMA = """
        CREATE TABLE users (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            forename TEXT NOT NULL,
            surname    TEXT NOT NULL,
            username   Text NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """

    SEED_DATA = """
INSERT INTO user(forname, surname, username, password_hash)
VALUES ("Test", "User", "test",
"scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252" )
    """


class messageTable:

    NAME = "message"

    SCHEMA = """
        CREATE TABLE message (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title    TEXT NOT NULL,
            body   Text NOT NULL,


             FOREIGN KEY(user_id) REFERENCES user(id)
        )
    """

    SEED_DATA = """
INSERT INTO note(title, body, pinned, user_id)
VALUES ("Welcome!",        "This is a demo application", 1, 1),
       ("Getting Started", "Use this template to start", 1, 1),
       ("Pinned Note",     "Pinned notes appear at top", 1, 1),
       ("Sample Note",     "This is just a sample note", 0, 1),
       ("Sample Note",     "This is just a sample note", 0, 1),
       ("Sample Note",     "This is just a sample note", 0, 1) 
    """


# Add more table classes here...



#----------------------------------------------------------------------------
# Table registry
#----------------------------------------------------------------------------
# Register all of your tables by adding them to the TABLES list here:
#
# TABLES = [
#     Table1,
#     Table2,
#     etc.
# ]
#
# Note: The table order is important - Create the tables that have
#       foreign keys AFTER the tables they link to have been created
#----------------------------------------------------------------------------

TABLES = [
    UserTable,
    # Add more tables here...
]

