import sqlite3 # sqlite3느ㄴ with 키워드를 사용하여 컨텍스트 매니저를 통해 트랜잭션을 관리한다.

# 데이터베이스와의 연결과 구문을 실행하는 관심사를 추상화 시킨다.
# 영속 계층
class DatabaseManager:
    def __init__(self, database_filename):
        self.connection = sqlite3.connect(database_filename)

    def __del__(self):
        self.connection.close()

    def _execute(self, statement, values=None):
        with self.connection: # 데이터 트랜잭션 컨텍스트를 생성한다.
            cursor = self.connection.cursor()
            cursor.execute(statement, values or [])
            return cursor
    
    def create_table(self, table_name, columns):
        columns_with_types = [
            f'{column_name} {data_type}' for column_name, data_type in columns.items()
        ]
        self._execute(f'''
                        CREATE TABLE IF NOT EXISTS {table_name}
                        ({', '.join(columns_with_types)});
                      ''')
    
    def add(self, table_name, data):
        placeholders = ', '.join('?' * len(data))
        column_names = ', '.join(data.keys())
        column_values = tuple(data.values())

        self._execute(f'''
                        INSERT INTO {table_name}
                        ({column_names})
                        VALUES ({placeholders})
                      ''',
                      column_values)
    
    def delete(self, table_name, criteria):
        placeholders = [f'{column} = ?' for column in criteria.keys()]
        delete_criteria =' AND '.join(placeholders)

        self._execute(f'''
                        DELETE FROM {table_name}
                        WHERE {delete_criteria}
                      ''',
                      tuple(criteria.values()),
                    )
    
    def select(self, table_name, criteria=None, order_by=None):
        criteria = criteria or {}

        query = f'SELECT * FROM {table_name}'

        # 쿼리에서 리터럴 값이 있는 곳에는 플레이스홀더를 사용해야 한다.
        if criteria:
            placeholders = [f'{column} = ?' for column in criteria.keys()]
            select_criteria = ' AND '.join(placeholders)
            query += f' WHERE {select_criteria}'

        if order_by:
            query += f' ORDER BY {order_by}'

        return self._execute(
            query,
            tuple(criteria.values()),
        )