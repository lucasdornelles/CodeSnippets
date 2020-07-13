import sys
import time

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Snippet(Base):
    __tablename__ = 'snippets'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    snippet = Column(String)
    tags = relationship('Tag', secondary='tagmap')

    def __init__(self, name, snippet):
        self.name = name
        self.snippet = snippet

    def add_tags(self, items):
        for tag in items:
            self.tagmap.append(Tagmap(snippet=self, tag=tag))


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


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    snippets = relationship('Snippet', secondary='tagmap')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


engine = create_engine('sqlite:///resources/dummy_database.db', echo=True)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

tag1 = Tag('tag1')
tag2 = Tag('tag2')
tag3 = Tag('tag3')
tag4 = Tag('tag4')
tag5 = Tag('tag5')
tag6 = Tag('tag6')

session.add_all([tag1, tag2, tag3, tag4, tag5, tag6])
session.commit()

snippet1 = Snippet('snippet1', 'test1')
snippet2 = Snippet('snippet2', 'test2')

snippet1.add_tags([tag1, tag2, tag3, tag4])
snippet2.add_tags([tag4, tag5, tag6])

session.commit()
print(snippet1.id)
snippet1.tags.remove(tag1)
session.commit()
print(snippet1.tags)
snippet1.add_tags([tag6])
session.commit()
print(snippet1.tags)
print(snippet2.tags)
print()
print('start query')
start_time = time.time()
print(sys.getsizeof(session))
print()
print('first query')
print(time.time() - start_time)
snippet = session.query(Snippet).filter(Snippet.tags.any(name='tag6'))
print(time.time() - start_time)
print('second query')
print(time.time() - start_time)
snippet = snippet.filter(Snippet.tags.any(name='tag5'))
print(time.time() - start_time)
print('count')
print(time.time() - start_time)
snippet = snippet.first()
print(sys.getsizeof(snippet))
print(time.time() - start_time)
print('answer')
print(snippet.tags)
print(time.time() - start_time)
snippet = session.query(Snippet).filter(Snippet.tags.any(name='tag6')).filter(Snippet.tags.any(name='tag5')).first().tags
print(time.time() - start_time)
new_sni=Snippet.query.filtery(Snippet.tags.any(name='tag5')).first()
print(new_sni.tags)

# working for now...
# session querys seems to only execute a select after a selec function has bem called(first() all() etc)
# so it seem fine to nest querys on a for tag in tags loop before calling a select
# size seems consistent the same before queryng but couldn't evaluate if it has any performance loss
# due to it being to fast already

# another test seems like it takes about 2 milliseconds to prepare the query object(56 byts)
# it's decent fast, but not terrible fast
# on another test it looks like my computer cant actually precisely measure the time
# also a inline nested query seems to take about the same time....
# guess its fine for now, will utilize the nested loop query
