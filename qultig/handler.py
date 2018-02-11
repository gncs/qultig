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


def get_art_quizzes(session: Session, category_distr: CategoryDistribution) -> List[models.Quiz]:
    selected_ids = []

    for category, count in category_distr.items():
        stem = session.query(models.Stem).filter(models.Stem.category == category).first()
        quiz_ids = [item[0] for item in session.query(models.Quiz.id).filter(models.Quiz.stem == stem)]
        selected_ids += random.sample(quiz_ids, count)

    quizzes = list(session.query(models.Quiz).filter(models.Quiz.id.in_(selected_ids)))
    random.shuffle(quizzes)
    return quizzes


Response = namedtuple('Response', ['item_id', 'option_id'])
Feedback = namedtuple('Feedback', ['correct', 'labels'])


def get_art_feedback(session: Session, response: Response) -> Feedback:
    quiz = session.query(models.Quiz).filter(models.Quiz.id == response.item_id).first()

    correct = response.option_id == quiz.key.id
    labels = {quiz.key.id: True}

    if not correct:
        labels.update({response.option_id: False})

    return Feedback(correct=correct, labels=labels)
