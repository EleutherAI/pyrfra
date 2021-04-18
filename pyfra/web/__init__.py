from .server import *
from functools import wraps, partial
import inspect
import string
import random
from html import escape
try:
    from typing_extensions import Literal
except ModuleNotFoundError:
    from typing import Literal

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from ansi2html import Ansi2HTMLConverter


__all__ = ['page', 'webserver']


def page(pretty_name=None, display: Literal["raw", "text", "monospace"]="monospace", field_names={}, dropdowns={}, roles=['everyone']):
    def _fn(callback, pretty_name, field_names, roles, display):

        sig = inspect.signature(callback)

        class CustomForm(FlaskForm):
            pass

        for name in sig.parameters:
            type = sig.parameters[name].annotation
            is_required = (sig.parameters[name].default == inspect._empty)

            if type == int:
                field = IntegerField
            elif type == bool:
                field = BooleanField
            else:
                if name in dropdowns:
                    field = partial(SelectField, choices=dropdowns[name])
                else:
                    field = StringField

            setattr(CustomForm, name, field(
                field_names.get(name, name), 
                validators=[DataRequired()] if is_required else [],
                default = sig.parameters[name].default if not is_required else None
                ))

        if len(sig.parameters) > 0:
            CustomForm.submit = SubmitField('Submit')
            form = True
        else:
            form = False

        def _callback_wrapper(k):
            html = callback(**k)
            if display == "raw":
                pass
            elif display == "text":
                html = escape(html)
            elif display == "monospace":
                converter = Ansi2HTMLConverter()
                html = converter.convert(html, full=False)
                html = f"<span class=\"monospace\">{html}</span>"
                html += converter.produce_headers()
            else:
                raise NotImplementedError
            
            return html

        register_page(callback.__name__, pretty_name, CustomForm, _callback_wrapper, roles, redirect_index=False, has_form=form)
    
    # used @form and not @form()
    if callable(pretty_name):
        return _fn(pretty_name, pretty_name=None, field_names=field_names, roles=roles, display=display)

    return partial(_fn, pretty_name=pretty_name, field_names=field_names, roles=roles, display=display)


def gen_pass(stringLength=16):
    """Generate a random string of letters, digits """
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength))   


@page("Add User", roles=["admin"])
def adduser(username: str, email: str="example@example.com", roles: str=""):
    password = gen_pass()

    add_user(username, email, password, roles)

    return f"Added user {username} with randomly generated password {password}."


def webserver(debug=False):
    if User.query.count() == 0:
        # Add temporary admin user
        password = gen_pass()
        add_user("root", "example@example.com", password, "admin")
        print("=================================================")
        print("ADMIN LOGIN CREDENTIALS (WILL ONLY BE SHOWN ONCE)")
        print("Username: root")
        print("Password:", password)
        print("=================================================")
    app.run(host='0.0.0.0', debug=debug)