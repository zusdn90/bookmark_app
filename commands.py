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
    def execute(self, data, timestamp=None):
        data['data_added'] = timestamp or datetime.utcnow().isoformat()
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


class ImportGitHubStarsCommand:
    def _extract_bookmark_info(self, repo):  # <1>
        return {
            'title': repo['name'],
            'url': repo['html_url'],
            'notes': repo['description'],
        }

    def execute(self, data):
        bookmarks_imported = 0

        github_username = data['github_username']
        next_page_of_results = f'https://api.github.com/users/{github_username}/starred'  # <2>

        while next_page_of_results:  # <3>
            stars_response = requests.get(  # <4>
                next_page_of_results,
                headers={'Accept': 'application/vnd.github.v3.star+json'},
            )
            next_page_of_results = stars_response.links.get('next', {}).get('url')  # <5>

            for repo_info in stars_response.json():
                repo = repo_info['repo']  # <6>

                if data['preserve_timestamps']:
                    timestamp = datetime.strptime(
                        repo_info['starred_at'],  # <7>
                        '%Y-%m-%dT%H:%M:%SZ'  # <8>
                    )
                else:
                    timestamp = None

                bookmarks_imported += 1
                AddBookmarkCommand().execute(  # <9>
                    self._extract_bookmark_info(repo),
                    timestamp=timestamp,
                )

        return f'Imported {bookmarks_imported} bookmarks from starred repos!'  # <10>


class EditBookmarkCommand:
    def execute(self, data):
        db.update(
            'bookmarks',
            {'id': data['id']},
            data['update'],
        )
        return 'Bookmark updated!'

class QuitCommand:
    def execute(self):
        sys.exit()