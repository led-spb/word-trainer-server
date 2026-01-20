from typing import List
import click
from flask import current_app
from flask.cli import AppGroup
from ..models import db
from ..models.word import Word, Accent
from ..services.words import WordService
from ..services.spellings import SpellingService

imports_commands = AppGroup('import', help='Import data')


def split_csv(line: str) -> List[str]:
    line = line.strip()
    for s in [',', '|', '/']:
        line = line.replace(s, ';')
    return line.split(';')


@imports_commands.command('words', help='Import words from csv file')
@click.option('--level', type=int, default=6)
@click.argument('filename', type=str)
def import_word(filename = None, level = 6):
    with open(filename, 'rt', encoding='utf-8') as fp:
        for line in fp:
            d = split_csv(line)

            word = d[0].strip()
            context = next(iter(d[1:2]), None)
            spellings = d[2:]
            if word == '':
                continue

            if context is not None:
                context = context.strip()

            create_word(word, None if context == '' else context, level, spellings)
    return


def is_vowel(chr) -> bool:
    return chr.lower() in ['а','е','ё','и','о','у','ы','э','ю','я']


def create_word(full_word :str, context :str, level :int, spellings :List[str]):
    word = WordService.find_by_name(full_word.lower(), context)

    if word is None:
        current_app.logger.warning(f'{full_word} {context}')
        word = Word(
            fullword = full_word.lower(),
            context = context,
            level = level
        )

    accent_position = next(
        (idx for idx, chr in enumerate(full_word) if chr.isupper() and is_vowel(chr)), None)
    if accent_position is not None:
        acc_positions = [acc.position for acc in word.accents]
        if accent_position not in acc_positions:
            current_app.logger.warning(f'{full_word} accent')
            word.accents.append(
                Accent(word_id=word.id, position=accent_position)
            )
            db.session.add(word)

    for sp in spellings:
        SpellingService.import_spelling(word, sp.strip())

    db.session.add(word)
    db.session.commit()
    return word
