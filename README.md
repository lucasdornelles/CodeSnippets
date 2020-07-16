## CS50x Final Project: CodeSnippets

### Introduction:
CodeSnippets is a SNS like code snippets database implemented using Flask, sqlalchemy, postgresSQL and 
codemirror as a code writing front-end api.
A live version can be found in https://codesnippets0.herokuapp.com/

### Front-end:
Code is writing using the code mirror api, tagsinput and typeahead are used for inserting and editing code snippets tags.
<br>
**codemirror**: CodeMirror is a versatile text editor implemented in JavaScript for the browser. It is specialized for editing code, and comes with a number of language modes and addons that implement more advanced editing functionality. (<a href="codemirror.net">codemirror.net</a>)
<br>
**tagsinput**: Bootstrap Tags Input is a jQuery plugin providing a Twitter Bootstrap user interface for managing tags.(https://bootstrap-tagsinput.github.io/bootstrap-tagsinput/examples/)
<br>
**typeahead**: a flexible JavaScript library that provides a strong foundation for building robust typeaheads. (https://twitter.github.io/typeahead.js/)
<br>
Code snippets are ordered by the number of tags when searching. 
### Back-end:
Database was implemented in postgresSQL using plain sqlalchemy, many to many relationship were implemented using sqlalchemy
secondary relationship (for bookmarks and tags).
<br>
**postgresSQL**: PostgreSQL is a powerful, open source object-relational database system with over 30 years of active development that has earned it a strong reputation for reliability, feature robustness, and performance.(https://www.postgresql.org/)
<br>
**sqlalchemy**: SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.
It provides a full suite of well known enterprise-level persistence patterns, designed for efficient and high-performing database access, adapted into a simple and Pythonic domain language.
(https://www.sqlalchemy.org/)
<br>
<br>
And that is pretty much it. Database models are implemented in database.py, config.py sets the aplication configurations
and app.py implements the routes and database interactions.