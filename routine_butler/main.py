import uuid
from typing import Optional

from nicegui import ui, app
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from loguru import logger
from sqlmodel import Session


from .elements.header import Header
from routine_butler.elements.routines_sidebar import RoutinesSidebar
# from routine_butler.elements.programs_sidebar import ProgramsSidebar
from .database.models import User
from .utils.constants import clrs


# session info keeps track of logged-in user
session_info: dict[str, dict] = {}

def is_authenticated(request: Request) -> bool:
    return session_info.get(request.session.get('id'), {}).get('authenticated', False)


def set_colors():
    ui.colors(
        primary=clrs.primary,
        secondary=clrs.secondary,
        accent=clrs.accent,
        positive=clrs.positive,
        negative=clrs.negative,
        info=clrs.info,
        warning=clrs.warning,
    )



class DBMiddleware:
    def __init__(self, app, engine):
        self.app = app
        self.engine = engine

    async def __call__(self, scope, receive, send):
        scope['db_engine'] = self.engine
        await self.app(scope, receive, send)

def db_session(request: Request) -> Session:
    """helper to get DB session from request"""
    return Session(request.scope['db_engine'])


@ui.page('/')
def main_gui(request: Request) -> None:
    set_colors()

    if not is_authenticated(request):
        return RedirectResponse('/login')

    with db_session(request) as session:
        username = session_info[request.session['id']]['username']
        user = User.eagerly_get_user(session, username)

        if user is None:  # invalid session-id
            del request.session['id']
            ui.open('/login')

        header = Header()
        routines_sidebar = RoutinesSidebar(session, user=user)
        header.routines_button.on("click", routines_sidebar.toggle)

        # programs_sidebar = ProgramsSidebar(
        #     user=self.user, repository=self.repository
        # )

        # header.programs_button.on("click", programs_sidebar.toggle)


@ui.page('/login')
def login(request: Request) -> None:
    set_colors()
    def on_login_attempt():
        with db_session(request) as session:
            user = User.eagerly_get_user(session, username_input.value)

        if user is None:
            ui.notify("Invalid username")
        else:
            session_info[request.session['id']] = {'username': user.username, 'authenticated': True}
            ui.notify("Welcome, " + user.username + "!")
            ui.open('/')

    # used with --testing for automatically login users
    if request.app.auto_login is not None:
        session_info[request.session['id']] = {'username': request.app.auto_login, 'authenticated': True}

    if is_authenticated(request):
        return RedirectResponse('/')
    request.session['id'] = str(uuid.uuid4())
    with ui.card():
        ui.label("Login")
        ui.separator()
        username_input = ui.input("Username")
        ui.button("Login", on_click=on_login_attempt)


def main(db_engine, auto_login=None):
    app.add_middleware(DBMiddleware, engine=db_engine)
    app.add_middleware(SessionMiddleware, secret_key='Ax5#%$3dgsfd.345dg^$fgd')
    app.auto_login = auto_login
    ui.run()
