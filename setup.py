from setuptools import setup, find_packages

setup(
    name="translation_god",
    version="1.0.2",
    author="zayfen",
    author_email="zhangyunfeng0101@gmail.com",
    description="A translation tool based ChatGPT",
    url="https://github.com/zayfen/TranslationGod",
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'translation_god=translation_god.main:main',
            'tg=translation_god.main:main'
        ]
    }
)
