from setuptools import find_packages, setup

setup(
    name='flask-sqlx',
    version='0.0.3',
    description='旨在为写sql的程序拆分sql语句出程序中,分类管理。目前支持增删改查、分页、事务,以及flask项目中多数据库连接。',
    long_description=open('README.rst').read(),
    author='miaokela',
    author_email='2972799448@qq.com',
    maintainer='miaokela',
    maintainer_email='2972799448@qq.com',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/miaokela/flask-sqlx',
    license='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)