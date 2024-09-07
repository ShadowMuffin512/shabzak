import importlib
import os

import eel

from db import init_db

eel.init("web")
ROUTES_DIR = "routes"


def expose_all_functions(module):
    for func_name in dir(module):
        if not func_name.startswith("__"):
            func = getattr(module, func_name)
            if callable(func):
                eel.expose(func)


init_db.init_db()
for filename in os.listdir(ROUTES_DIR):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]  # Remove '.py' extension
        module_path = f"{ROUTES_DIR}.{module_name}"
        module = importlib.import_module(module_path)
        expose_all_functions(module)

eel.start("index.html", size=(800, 600))
