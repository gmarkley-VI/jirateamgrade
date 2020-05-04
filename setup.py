from setuptools import setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()



setup(
    name='jirateamgrade',
    version='0.0.1',
    packages=['jirateamgrade'],
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/gmarkley-VI/jirateamgrade",
    license='License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    author='Gabriel Markley',
    author_email='gabriel.markley@gmail.com',
    description='A tool to grade your teams usage of JIRA',
)
