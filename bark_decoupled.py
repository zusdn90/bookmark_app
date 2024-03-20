#!/usr/bin/env python
# 비즈니스 로직과 표현 계층 분리하기
# 기존 하드코딩된 특정 메시지 대신에 상태와 결과의 개념을 이용하여 상호작용한다.

import os
from collections import OrderedDict

import commands


def format_bookmark(bookmark):
    return '\t'.join(
        str(field) if field else ''
        for field in bookmark
    )


class Option:
    def __init__(self, name, command, prep_call=None, success_message='{result}'):  # <1> 결과를 반환하는 명령에 대한 디폴트 메세지는 결과 그 자체다.
        self.name = name
        self.command = command
        self.prep_call = prep_call
        self.success_message = success_message  # <2> 나중에 사용하기 위해 이 옵션에 대해 구성된 성공 메세지를 저장한다.

    def choose(self):
        data = self.prep_call() if self.prep_call else None
        success, result = self.command.execute(data)  # <3> 실행 결과와 상태를 받는다.

        formatted_result = ''

        if isinstance(result, list):  # <4> 필요한 경우, 표시할 결과의 형태를 만든다.
            for bookmark in result:
                formatted_result += '\n' + format_bookmark(bookmark)
        else:
            formatted_result = result

        if success:
            print(self.success_message.format(result=formatted_result))  # <5> 필요한 경우, 형식화된 결과를 삽입하여 성공 메세지를 출력한다.

    def __str__(self):
        return self.name


def clear_screen():
    clear = 'cls' if os.name == 'nt' else 'clear'
    os.system(clear)


def print_options(options):
    for shortcut, option in options.items():
        print(f'({shortcut}) {option}')
    print()


def option_choice_is_valid(choice, options):
    return choice in options or choice.upper() in options


def get_option_choice(options):
    choice = input('Choose an option: ')
    while not option_choice_is_valid(choice, options):
        print('Invalid choice')
        choice = input('Choose an option: ')
    return options[choice.upper()]


def get_user_input(label, required=True):
    value = input(f'{label}: ') or None
    while required and not value:
        value = input(f'{label}: ') or None
    return value


def get_new_bookmark_data():
    return {
        'title': get_user_input('Title'),
        'url': get_user_input('URL'),
        'notes': get_user_input('Notes', required=False),
    }


def get_bookmark_id_for_deletion():
    return get_user_input('Enter a bookmark ID to delete')


def get_github_import_options():
    return {
        'github_username': get_user_input('GitHub username'),
        'preserve_timestamps':
            get_user_input(
                'Preserve timestamps [Y/n]',
                required=False
            ) in {'Y', 'y', None},
    }


def get_new_bookmark_info():
    bookmark_id = get_user_input('Enter a bookmark ID to edit')
    field = get_user_input('Choose a value to edit (title, URL, notes)')
    new_value = get_user_input(f'Enter the new value for {field}')
    return {
        'id': bookmark_id,
        'update': {field: new_value},
    }


def loop():
    clear_screen()

    options = OrderedDict({
        'A': Option(
            'Add a bookmark',
            commands.AddBookmarkCommand(),
            prep_call=get_new_bookmark_data,
            success_message='Bookmark added!',  # <6> 결과가 없는 옵션은 정적 성공 메시지를 지정할 수 있다.
        ),
        'B': Option(
            'List bookmarks by date',
            commands.ListBookmarksCommand(),  # <7> 결과만 출력해야 하는 옵션은 메시지를 지정할 필요가 없다.
        ),
        'T': Option(
            'List bookmarks by title',
            commands.ListBookmarksCommand(order_by='title'),
        ),
        'E': Option(
            'Edit a bookmark',
            commands.EditBookmarkCommand(),
            prep_call=get_new_bookmark_info,
            success_message='Bookmark updated!'
        ),
        'D': Option(
            'Delete a bookmark',
            commands.DeleteBookmarkCommand(),
            prep_call=get_bookmark_id_for_deletion,
            success_message='Bookmark deleted!',
        ),
        'G': Option(
            'Import GitHub stars',
            commands.ImportGitHubStarsCommand(),
            prep_call=get_github_import_options,
            success_message='Imported {result} bookmarks from starred repos!',  # <8> 결과와 사용자 정의 메시지를 갖는 옵션은 두 가지 모두를 합칠 수 있다.
        ),
        'Q': Option(
            'Quit',
            commands.QuitCommand()
        ),
    })
    print_options(options)

    chosen_option = get_option_choice(options)
    clear_screen()
    chosen_option.choose()

    _ = input('Press ENTER to return to menu')


if __name__ == '__main__':
    while True:
        loop()