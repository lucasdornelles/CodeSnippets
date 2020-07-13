from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import bcrypt

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    about = Column(String)
    password = Column(String)

    user_bookmarks = relationship('Snippet', secondary='bookmarks', lazy='joined')
    snippets = relationship('Snippet')

    def __init__(self, name, password):
        self.name = name
        self.password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        self.about = ""

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf8'), self.password)

    def update_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())


class Tagmap(Base):
    __tablename__ = 'tagmap'
    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'))
    snippet_id = Column(Integer, ForeignKey('snippets.id'))

    tag = relationship('Tag', backref=backref('tagmap', cascade='all, delete-orphan'))
    snippet = relationship('Snippet', backref=backref('tagmap', cascade='all, delete-orphan'))

    def __init__(self, snippet, tag):
        self.snippet = snippet
        self.tag = tag


class Snippet(Base):
    __tablename__ = 'snippets'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    snippet = Column(String)
    description = Column(String)
    public = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    mode = Column(String)
    user = relationship('User')
    tags = relationship('Tag', secondary='tagmap', lazy='joined')
    n_tags = Column(Integer)

    def __init__(self, name, snippet, description, mode, user):
        self.name = name
        self.snippet = snippet
        self.description = description
        self.mode = mode
        self.user = user

    def add_tags(self, items):
        self.n_tags = len(items)
        for tag in items:
            self.tagmap.append(Tagmap(snippet=self, tag=tag))

    def get_tag_string(self):
        tag_string = ""
        for tag in self.tags:
            tag_string = tag_string+tag.name+","
        return tag_string[:-1]

    def get_tag_list(self):
        return [tag.name for tag in self.tags]


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    snippets = relationship('Snippet', secondary='tagmap')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    snippet_id = Column(Integer, ForeignKey('snippets.id'))

    user = relationship('User', backref=backref('bookmarks', cascade='all, delete-orphan'))
    snippet = relationship('Snippet', backref=backref('bookmarks', cascade='all, delete-orphan'))
