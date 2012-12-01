from setuptools import setup
from __init__ import VERSION


setup(name='nanote',
      version=VERSION,
      description='nanote terminal note-taking software',
      author='Ben Morris',
      author_email='ben@bendmorris.com',
      url='https://github.com/hourchallenge/nanote',
      packages=['nanote'],
      package_dir={
                'nanote':''
                },
      entry_points={
        'console_scripts': [
            'nanote = nanote.nanote:main',
        ],
      },
      )
