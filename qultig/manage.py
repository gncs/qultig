import argparse
import datetime
import json
import logging
import math
import os
import random
from typing import List, Dict

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from qultig.models import Base, Artist, Painting, Stem, Item, Option, StemCategory


def setup(engine, data_dir: str, num_options=4, **kwargs):
    drop_all(engine)
    load_authors(engine, data_dir)
    load_paintings(engine, data_dir)
    create_who_items(engine, num_options)
    create_style_items(engine, num_options)
    create_date_items(engine, num_options)
    create_title_items(engine, num_options)


def drop_all(engine):
    logging.info('Dropping all and create new tables')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def load_authors(engine, data_dir: str):
    logging.info('Loading artists')
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(os.path.join(data_dir, 'authors.json'), 'r') as f:
        authors = json.load(f)

    for i, author in authors.items():
        artist = Artist(**author)
        session.add(artist)

    session.commit()


def load_paintings(engine, data_dir: str):
    logging.info('Loading paintings')
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(os.path.join(data_dir, 'paintings.json'), 'r') as f:
        df = pd.DataFrame.from_dict(json.load(f), orient='index')

    for k, v in df.groupby('author'):
        paintings = v.drop('author', axis=1)
        artist = session.query(Artist).filter(Artist.name == k).first()

        for index, row in paintings.iterrows():
            painting = Painting(artist=artist, **row)
            session.add(painting)

        session.commit()


def create_who_items(engine, num_options: int):
    logging.info("Creating 'who' items")
    Session = sessionmaker(bind=engine)
    session = Session()

    stem = Stem(text='Who made this painting?', category=StemCategory.who)
    artists = list(session.query(Artist).all())

    items = []
    for painting in session.query(Painting).filter(~Painting.is_detail):
        q = Item()

        q.stem = stem
        q.painting = painting

        key_text = painting.artist.name

        other_artist_names = [artist.name for artist in artists if artist != painting.artist]
        option_texts = [key_text] + random.sample(other_artist_names, num_options - 1)

        options = create_options(option_texts)
        q.options = list(options.values())
        q.key = options[key_text]

        items.append(q)

    session.add_all(items)
    session.commit()


def create_style_items(engine, num_options: int):
    logging.info("Creating 'style' items")
    Session = sessionmaker(bind=engine)
    session = Session()

    stem = Stem(text="What is this painting's style of art?", category=StemCategory.style)
    styles = [item[0] for item in session.query(Painting.style).distinct()]

    items = []
    for painting in session.query(Painting).filter(~Painting.is_detail):
        q = Item()

        q.stem = stem
        q.painting = painting

        key_text = painting.style

        other_styles = [style for style in styles if style != painting.style]
        option_texts = [key_text] + random.sample(other_styles, num_options - 1)

        options = create_options(option_texts)
        q.options = list(options.values())
        q.key = options[key_text]

        items.append(q)

    session.add_all(items)
    session.commit()


def create_date_items(engine, num_options: int, date_increment: int = 50):
    logging.info("Creating 'date' items")
    Session = sessionmaker(bind=engine)
    session = Session()

    stem = Stem(text="When was this painting made?", category=StemCategory.date)

    items = []
    for painting in session.query(Painting).filter(Painting.is_int_date).filter(~Painting.is_detail):
        q = Item()

        q.stem = stem
        q.painting = painting

        int_date = int(q.painting.date)

        key_text = str(int_date)
        option_texts = [key_text] + invent_dates(int_date, date_increment, num_options - 1)

        options = create_options(option_texts)
        q.options = list(options.values())
        q.key = options[key_text]

        items.append(q)

    session.add_all(items)
    session.commit()


def create_title_items(engine, num_options: int):
    logging.info("Creating 'title' items")
    Session = sessionmaker(bind=engine)
    session = Session()

    stem = Stem(text="What is this painting's title?", category=StemCategory.title)
    titles = [item[0] for item in
              session.query(Painting.title).filter(~Painting.is_detail).filter(Painting.clean_title)]

    items = []
    for painting in session.query(Painting).filter(Painting.is_detail):
        q = Item()

        q.stem = stem
        q.painting = painting

        key_text = str(painting.original_title)
        other_titles = [title for title in titles if title != key_text]
        option_texts = [key_text] + random.sample(other_titles, num_options - 1)

        options = create_options(option_texts)
        q.options = list(options.values())
        q.key = options[key_text]

        items.append(q)

    session.add_all(items)
    session.commit()


def create_options(options: List[str]) -> Dict[str, Option]:
    copy = options.copy()
    random.shuffle(copy)
    return {o: Option(text=o) for o in copy}


def invent_dates(true_date: int, increment: int, count: int):
    # Assert that invented dates do not lie in the future
    now = datetime.datetime.now()
    delta = now.year - true_date

    if delta < 0:
        raise ValueError('Date lies in the future: ' + str(true_date))

    s = math.floor(delta / increment)
    low = 0
    if s < count:
        low = count - s

    pos = random.randint(low, count)
    start = true_date - pos * increment

    return [start + i * increment for i in range(0, count + 1) if i != pos]


def print_content(engine, *args, **kwargs):
    Session = sessionmaker(bind=engine)
    session = Session()

    print('Number of paintings: ' + str(session.query(Painting).count()))
    print('Number of artists: ' + str(session.query(Artist).count()))
    print('Number of items: ' + str(session.query(Item).count()))


def create_parser():
    parser = argparse.ArgumentParser(description='qultig - database management')

    subparsers = parser.add_subparsers(title='sub-commands', dest='function')
    setup_parser = subparsers.add_parser('setup', help='setup database')
    setup_parser.add_argument('--data-dir', required=True)

    subparsers.add_parser('print', help='print database content')

    return parser


def hook():
    functions = {
        'setup': setup,
        'print': print_content,
    }

    logging.getLogger().setLevel(logging.INFO)
    args = create_parser().parse_args()
    engine = create_engine('sqlite:///' + os.environ['SQLITE_PATH'], echo=False)
    functions[args.function](engine=engine, **vars(args))


if __name__ == '__main__':
    hook()
