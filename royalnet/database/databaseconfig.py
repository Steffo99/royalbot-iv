import typing


class DatabaseConfig:
    def __init__(self,
                 database_uri: str,
                 master_table: typing.Type,
                 identity_table: typing.Type,
                 identity_column_name: str):
        self.database_uri: str = database_uri
        self.master_table: typing.Type = master_table
        self.identity_table: typing.Type = identity_table
        self.identity_column_name: str = identity_column_name
