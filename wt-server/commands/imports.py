import click
from flask import current_app
from flask.cli import AppGroup
from ..models import db
from ..models.word import Word, Accent
from ..services.words import WordService

imports_commands = AppGroup('import', help='Import data')


@imports_commands.command('words', help='Import words from plain file')
@click.option('--level', type=int, default=6)
@click.argument('filename', type=str)
def import_word(filename = None, level = 6):
    with open(filename, 'rt', encoding='utf-8') as fp:
        for line in fp:
            d = line.split('/', 2)
            word = d[0].strip()
            context = None if len(d) < 2 else d[1].strip()

            create_word(word, context, level)
    return


def create_word(full_word, context, level):
    word = WordService.find_by_name(full_word, context)

    if word is None:
        current_app.logger.warning(f'{full_word} {context}')
        word = Word(
            fullword = full_word,
            context = context,
            level = level
        )

    accent_position = next((idx for idx, chr in enumerate(full_word) if chr.isupper()), None)
    if accent_position is not None:
        acc_positions = [acc.position for acc in word.accents]
        if accent_position not in acc_positions:
            word.accents.append(
                Accent(word_id=word.id, position=accent_position)
            )
            db.session.add(word)


    db.session.add(word)
    db.session.commit()
    return word
