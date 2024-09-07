import importlib
import os

import eel

from db import init_db

eel.init("web")
ROUTES_DIR = "routes"


init_db.init_db()
for filename in os.listdir(ROUTES_DIR):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]  # Remove '.py' extension
        module_path = f"{ROUTES_DIR}.{module_name}"
        module = importlib.import_module(module_path)

eel.start("index.html", size=(800, 600))
