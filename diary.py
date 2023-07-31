"""Diary Application

Records date and description. Entries are displayed as a card.
It uses bootstrap 5.2.3 to style the elements.

pip install reactpy
pip install pandas
pip install reactpy-flake8
"""


from typing import Union
from datetime import datetime
from reactpy import component, html, event, hooks
from reactpy.backend.fastapi import configure
from fastapi import FastAPI
import pandas as pd


BOOTSTRAP_CSS = html.link(
    {
        'href': 'https://cdn.jsdelivr.net/npm/'
                'bootstrap@5.2.3/dist/css/bootstrap.min.css',
        'integrity': 'sha384-rbsA2VBKQhggwzxH7pPCaAq'
                     'O46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65',
        'rel': 'stylesheet',
        'crossorigin': 'anonymous'
    }
)


CSV_FILENAME = 'diary.csv'
COLUMN_HEADER = ['Date', 'Description']


def get_df(fn: str) -> tuple[bool, Union[pd.DataFrame, str]]:
    """Converts csv file to dataframe."""
    try:
        df = pd.read_csv(fn)
    except FileNotFoundError:
        df = pd.DataFrame(columns=COLUMN_HEADER)
        df.to_csv(fn, index=False)
    except Exception as err:
        return False, repr(err)
    return True, df


def get_date() -> str:
    """Gets date and time."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


@component
def Card(text: list):
    return html.div(
        html.div(
            {'class': 'card text-dark bg-light border-secondary mb-2'},
            html.div(
                {'class': 'card-body text-secondary'},
                html.div(
                    {'class': 'card-title text-secondary'},
                    html.h6(text[0])
                ),
                html.div(
                    {'class': 'card-text text-secondary'},
                    html.span(f'{text[1]}'),
                ),
            ),
        ),
    )


@component
def BuildCards(fn: str, records: list):
    """Save record to csv and build a list of cards."""
    dfr = pd.DataFrame(records, columns=COLUMN_HEADER)
    dfr.to_csv(fn, index=False)

    return html.div(
        {
            'style': {
                'height': '600px',
                'overflow-y': 'auto',
                'white-space': 'pre-wrap'
            }
        },
        [Card(rec) for rec in records[::-1]]
    )


@component
def Diary():
    csvfn = CSV_FILENAME
    description, set_description = hooks.use_state('')

    # Open the existing csv file. It will be created if it does not exist.
    # If there is error, we will send the error message and exit.
    okdf, df = get_df(csvfn)
    if not okdf:
        return html.h4(
            {'style': {'color': 'red'}},
            f'There is error {df} in opening the {csvfn} file.'
        )

    # Initialize our records from existing csv file.
    records, set_records = hooks.use_state(df.values.tolist())

    def update_textvalue(event):
        set_description(event['target']['value'])

    @event(prevent_default=True)
    def submit(event):
        """Updates records."""
        set_records(records + [[get_date(), description]])

    return html.div(
        BOOTSTRAP_CSS,
        html.div(
            {'class': 'container'},
            html.div(
                html.h2('My Diary'),
                html.form(
                    {'on_submit': submit},

                    html.div(
                        {'class': 'form-group'},
                        html.label(
                            {
                                'html_for': 'description',
                                'class': 'text-primary fs-5'
                            },
                            'Description'
                        ),
                        html.textarea(
                            {
                                'class': 'form-control border-primary',
                                'id': 'description',
                                'type': 'textarea',
                                'rows': '4',
                                'on_change': update_textvalue,
                            }
                        ),
                    ),

                    html.p(),
                    html.input(
                        {'class': 'btn btn-success',
                         'type': 'submit', 'value': 'Save'}
                    ),
                    html.input(
                        {'class': 'btn btn-danger mx-1',
                         'type': 'reset', 'value': 'Clear'}
                    ),
                ),
                html.p(),
                BuildCards(csvfn, records),
            ),
        ),
    )


app = FastAPI()
configure(app, Diary)
