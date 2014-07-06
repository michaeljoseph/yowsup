from setuptools import setup

setup(
    name='yowsup',
    version='0.0.1',
    description='Yowsup',
    author='Michael Joseph',
    author_email='michaeljoseph@gmail.com',
    packages=['yowsup'],
    entry_points={
        'console_scripts': [
            'yowsup = yowsup.cli:main',
        ],
    },
)
