from sqlalchemy.inspection import inspect


def model_to_dict(model):
    if model is None:
        return None

    def process_field(field):
        if isinstance(field, list):
            return [process_field(item) for item in field]
        elif hasattr(field, "__table__"):
            return model_to_dict(field)
        return field

    data = {
        column.name: process_field(getattr(model, column.name))
        for column in inspect(model).mapper.column_attrs
    }
    return data
