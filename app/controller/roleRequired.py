from functools import wraps
from flask_login import  current_user
from flask import render_template, session

def roles_required(roles):
    roles = [roles]
    new_roles = [s.strip() for s in roles[0].split(',')]

    def decorator_function(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            #print('roles', roles)
            #print('new_roles', new_roles)
            #print('session',  session["roles"])
            #print(any(role in new_roles for role in session["roles"]))
            if not any(role in new_roles for role in session["roles"]):
                return render_template('erro.html', e='Usuário sem permissão de acesso.')
            return f(*args, **kwargs)

        return wrapper

    return decorator_function