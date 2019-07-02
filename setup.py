from setuptools import setup, find_packages

short_description = "Fortran Laboratory"

with open("README.rst") as f:
    long_description = f.read()

setup(
    name='fortlab',
    version='0.0.1',
    description=short_description,
    long_description=long_description,
    author='Youngsung Kim',
    author_email='youngsun@ucar.edu',
    license='MIT',
    packages=find_packages(),
    test_suite="tests.fortlab_unittest_suite",
    url='https://github.com/NCAR/fortlab',
    entry_points={
        'console_scripts': [
            'fortlab = fortlab.__main__:main'
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Code Generators']
    )
