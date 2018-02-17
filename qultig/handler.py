import random
from collections import namedtuple
from typing import List

from sqlalchemy.orm import Session

from qultig import models


class CategoryDistribution(dict):
    def __init__(self, who=2, style=2, date=1, title=2):
        super().__init__()
        self[models.StemCategory.who] = who
        self[models.StemCategory.style] = style
        self[models.StemCategory.date] = date
        self[models.StemCategory.title] = title


def build_art_item(session: Session, category_distr: CategoryDistribution) -> List[models.Item]:
    selected_ids = []

    for category, count in category_distr.items():
        stem = session.query(models.Stem).filter(models.Stem.category == category).first()
        item_ids = [item[0] for item in session.query(models.Item.id).filter(models.Item.stem == stem)]
        selected_ids += random.sample(item_ids, count)

    items = list(session.query(models.Item).filter(models.Item.id.in_(selected_ids)))
    random.shuffle(items)
    return items


Response = namedtuple('Response', ['item_id', 'option_id'])
Feedback = namedtuple('Feedback', ['correct', 'labels'])


def get_art_feedback(session: Session, response: Response) -> Feedback:
    item = session.query(models.Item).filter(models.Item.id == response.item_id).first()

    correct = response.option_id == item.key.id
    labels = {item.key.id: True}

    if not correct:
        labels.update({response.option_id: False})

    return Feedback(correct=correct, labels=labels)
