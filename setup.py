from setuptools import setup, find_packages

with open('requirements.txt', 'r') as reqs:
    requirements = reqs.read().split('\n')
    
with open('README.md', 'r') as readme:
    description = readme.read()
    
packs = list(find_packages())

setup(
    name='BackGym-Trade',
    url='https://github.com/willarliss/BackGym-Trade',
    author='Will Arliss',
    author_email='warliss98@gmail.com',
    packages=packs,
    install_requires=requirements,
    version='0.0.1',
    license='MIT',
    python_requires='>=3.7',
    description='A stock trading environment for backtesting and reinforcement learning',
    long_description=description,
    long_description_content_type='text/markdown',
    classifiers=['Programming Language :: Python :: 3']
)
   