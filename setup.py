from distutils.core import setup


def readme():
    """Import the README.md Markdown file and try to convert it to RST format."""
    try:
        import pypandoc
        return pypandoc.convert('README.md', 'rst')
    except(IOError, ImportError):
        with open('README.md') as readme_file:
            return readme_file.read()


setup(
    name='NYC',
    version='0.1',
    description='Predicting NYC taxi trip duration from one location to the other',
    long_description=readme(),
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    # Substitute <github_account> with the name of your GitHub account
    url='https://github.com/pratha19/NYC_taxi_trip_duration',
    author='Prathamesh Pawar',  # Substitute your name
    author_email='pawar.pratha@gmail.com',  # Substitute your email
    license='MIT',
    packages=['NYC'],
)