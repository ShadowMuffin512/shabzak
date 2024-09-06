# utils.py
from sqlalchemy.inspection import inspect

def model_to_dict(model):
    if model is None:
        return None
    return {column.name: getattr(model, column.name) for column in inspect(model).mapper.column_attrs}