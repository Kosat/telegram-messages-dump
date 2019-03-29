
"""Setup script for telegram-messages-dump"""

import os.path
from setuptools import setup
from telegram_messages_dump import __version__

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

setup(
    name='telegram-messages-dump',
    version=__version__,
    description='Telegram Messages Dump console utility.',
    long_description_content_type="text/markdown",
    long_description=README,
    author='Kostya Kravets',
    author_email='kostikkv@gmail.com',
    url='https://github.com/Kosat/telegram-messages-dump',
    download_url='https://github.com/Kosat/telegram-messages-dump/releases',
    install_requires=['telethon==1.6.2'],
    license="MIT",
    packages=['telegram_messages_dump', "telegram_messages_dump.exporters"],
    include_package_data=True,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        'Programming Language :: Python :: 3'
    ],
    entry_points={
        'console_scripts':
            ['telegram-messages-dump = telegram_messages_dump.run:main']
    }
)
