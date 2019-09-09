#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-04 17:25
# Author: turpure

# config information
info = {
    'redis': {
        'broker': 'redis://''@192.168.0.172:6379/6',
        'backend': 'redis://''@192.168.0.172:6379/7',
        'task': {
            'host': '192.168.0.172',
            'port': '6379',
            'db': 10
        },
        'result': {
            'host': '192.168.0.172',
            'port': '6379',
            'db': 12
        },
        'cache': {
            'host': '192.168.0.172',
            'port': '6379',
            'db': 11
        }
    },
    'database': {
        'mysql': {
            'host': '192.168.0.150',
            'user': 'root',
            'password': 'ur@2016!',
            'db': 'proCenter',
            'charset': 'utf8'
        },

    },
    'headers': {
        'Authorization': 'Bearer SEV0001MTU0NjY1Mzc2M3xTSU9XdUJFbFU4NDJ5VHVndk8tV3ROem8yYVFCV0QtYjE2aTBDM3FNLWZkbVFyX01aTFJUek05REJZUVZnWVNmOE5TanlCWXhYRk84MWFINHZDTE5UVUJGb0ZSTmFWLXlkZlRCem9YRVg4R21GSEEwVHNQeHJIUWZKMmJ5dWd2VmpKNkZ4Q0V6VS1JdF9EZzF1UGtyb1NzcVQ5VDlQLTRwNnJ4Nl9yaHZTUkEzUmRfZUI0ZFB1TGxXejFFTkNzNm1PUzZoY1BScXI1YVhEWGlWdmVwODJIOVhxTnlZcGYxSVdDQzJXY1RTQjMyUjRWc09FVVU9fJgmguEcQE9NGiD_vYv4ymZpnsmOBH4btJX1l56WY4V7',
        'X-API-Token': 'ZxujHfoifnqH7zZKvZNciyjEP9RvaXHv',
        'X-Version': '3.1.0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        }
}


