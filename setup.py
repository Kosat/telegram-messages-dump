from setuptools import setup
from telegram_messages_dump import __version__

setup(
    name='telegram-messages-dump',
    version=__version__,
    description='Telegram Messages Dump console util.',
    author='Kostya K',
    author_email='kostikkv@gmail.com',
    url='https://github.com/Kosat/telegram-messages-dump',
    download_url='https://github.com/Kosat/telegram-messages-dump/releases',
    install_requires=['telethon==0.18.3'],
    packages=['telegram_messages_dump', "telegram_messages_dump.exporters"],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: MIT',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Windows',
        'Programming Language :: Python :: 3'
    ],
    entry_points={
        'console_scripts':
            ['telegram-messages-dump = telegram_messages_dump.run:main']
    }
)
