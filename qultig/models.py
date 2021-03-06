import enum

from sqlalchemy import Column, Table, Integer, Sequence, Boolean, String, Enum, UnicodeText
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class StemCategory(enum.Enum):
    who = 0
    style = 1
    date = 2
    title = 3


class Artist(Base):
    __tablename__ = 'artists'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)

    name = Column(String(50))
    wiki_search_url = Column(String(50), nullable=True)

    paintings = relationship('Painting', uselist=True)

    def __repr__(self):
        return "<Artist(id='%s', name='%s')>" % (self.id, self.name)


class Painting(Base):
    __tablename__ = 'paintings'

    id = Column(Integer, Sequence('painting_id_seq'), primary_key=True)

    artist_id = Column(Integer, ForeignKey('artists.id'))
    artist = relationship('Artist', uselist=False, back_populates='paintings', foreign_keys=[artist_id])

    img_url = Column(String(50), nullable=False)

    title = Column(String(50), nullable=True)
    original_title = Column(String(50), nullable=True)
    is_detail = Column(Boolean, nullable=False, default=False)
    clean_title = Column(Boolean, nullable=False, default=False)

    date = Column(String(50), nullable=True)
    is_int_date = Column(Boolean, nullable=False, default=False)

    location = Column(String(50), nullable=True)
    style = Column(String(50), nullable=True)

    comment = Column(UnicodeText, nullable=True)

    source_name = Column(String(50), nullable=True)
    source_url = Column(String(50), nullable=True)

    wiki_search_style_url = Column(String(50), nullable=True)

    def __repr__(self):
        return "<Painting(id='%s', artist='%s', url_img='%s', title='%s')>" % (
            self.id, self.artist, self.img_url, self.title)


class Stem(Base):
    __tablename__ = 'stems'

    id = Column(Integer, Sequence('stem_id_seq'), primary_key=True)
    category = Column(Enum(StemCategory), nullable=False)
    text = Column(String(50), nullable=False)


item_option_association = Table('item_option_association', Base.metadata,
                                Column('item_id', Integer, ForeignKey('items.id')),
                                Column('option_id', Integer, ForeignKey('options.id')),
                                )


class Option(Base):
    __tablename__ = 'options'

    id = Column(Integer, Sequence('option_id_seq'), primary_key=True)
    text = Column(String(50), nullable=False)

    items = relationship('Item', secondary=item_option_association, uselist=True, back_populates='options')


quiz_item_association = Table('quiz_item_association', Base.metadata,
                              Column('quiz_id', Integer, ForeignKey('quizzes.id')),
                              Column('item_id', Integer, ForeignKey('items.id')),
                              )


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, Sequence('item_id_seq'), primary_key=True)

    stem_id = Column(Integer, ForeignKey('stems.id'), nullable=False)
    stem = relationship('Stem', uselist=False, foreign_keys=[stem_id])

    painting_id = Column(Integer, ForeignKey('paintings.id'), nullable=False)
    painting = relationship('Painting', uselist=False, foreign_keys=[painting_id])

    options = relationship('Option', secondary=item_option_association, uselist=True, back_populates='items')

    key_id = Column(Integer, ForeignKey(Option.id), nullable=False)
    key = relationship(Option, uselist=False, foreign_keys=[key_id])

    quizzes = relationship('Quiz', secondary=quiz_item_association, uselist=True, back_populates='items')

    def __repr__(self):
        return "<Item(id='{}', painting_id='{}', options='{}', key='{}')>".format(self.id, self.painting_id,
                                                                                  self.options, self.key)


class Quiz(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, Sequence('quiz_id_seq'), primary_key=True)
    items = relationship('Item', secondary=quiz_item_association, uselist=True, back_populates='quizzes')

    def __repr__(self):
        return "<Quiz(id='{}')>".format(self.id)
