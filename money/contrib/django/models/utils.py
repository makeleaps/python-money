def currency_field_name(name: str) -> str:
    return "%s_currency" % name


def currency_field_db_column(db_column: str) -> str | None:
    return None if db_column is None else "%s_currency" % db_column
