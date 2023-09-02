from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()

setup(
    name='clumpi',
    version="0.0.1",
    description="Calculate Clumpiness index by Zhang, Bradlow and Small (2015)",
    long_description=readme,
    long_description_content_type='text/markdown',
    author='jniimi',
    author_email='jniimi@meijo-u.ac.jp',
    url='https://github.com/jniimi/clumpi',
    download_url='https://github.com/jniimi/clumpi',
    packages=find_packages(),
    keywords='RFMC Clumpiness marketing CRM',
    license='MIT'
)
