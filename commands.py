import sys
from database import DatabaseManager
from datetime import datetime

db = DatabaseManager('bookmarks.db')


# 각 작업에 대한 로직을 명령 객체로 캡슐화하고 execute 메서드로 실행하는 일관된 방법을 제공함으로써,
# 각 작업을 표현 계층에서 분리할 수 있다. 표현 계층은 그런 명령을 어떻게 동작하는지를 신경 쓰지 않고 메뉴 옵션과 명령을 연결할 수 있다. -> 커맨드 패턴
class CreateBookmarksTableCommand:
    def execute(self):
        db.create_table('bookmarks', {
            'id': 'integer primary key autoincrement',
            'title': 'text not null',
            'url': 'text not null',
            'notes': 'text',
            'date_added': 'text not null',
        })

class AddBookmarkCommand:
    def execute(self, data):
        data['data_added'] = datetime.utcnow().isoformat()
        db.add('bookmarks', data)
        return 'Bookmark added!'

class ListBookmarksCommand:
    def __init__(self, order_by='date_added'):
        self.order_by = order_by
    
    def execute(self):
        return db.select('bookmarks', order_by=self.order_by).fetchall()
    
class DeleteBookmarksCommand:
    def execute(self, data):
        db._execute('bookmarks', {'id': data})
        return 'Bookmark deleted!'

class QuitCommand:
    def execute(self):
        sys.exit()