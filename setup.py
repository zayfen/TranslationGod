from setuptools import setup, find_packages

setup(
    name="translation_god",
    version="1.0",
    author="zayfen",
    author_email="zhangyunfeng@pudutech.com",
    description="A translation tool based ChatGPT",
    url="https://codeup.aliyun.com/60a7c4c62c5969c370c58471/translation_god",
    packages=find_packages(),
    classifiers=[
        # 3 Alpha; 4 Beta; 5 Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Application :: Translator',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
        'Programming Language :: Python :: 3.11'
        'Programming Language :: Python :: 3.12'
    ],
    python_requires='>=3.5',
    entry_points={
        'console_scriptes': [
            'translation_god = translation_god.main:main'
        ]
    },
    scripts=['bin/translation_god']
)
