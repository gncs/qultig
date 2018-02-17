from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='qultig',
      version='0.1.8',
      description='A tiny Flask app for awesome quizzes',
      long_description=readme(),
      classifiers=['Programming Language :: Python :: 3.5'],
      author='Gregor Simm',
      python_requires='>=3.5',
      packages=find_packages(),
      entry_points={
          'console_scripts': ['qultig-setup = qultig.manage:hook'],
      },
      include_package_data=True,
      install_requires=[
          'flask',
          'sqlalchemy',
          'pandas',
          'hashids',
      ],
      zip_safe=False,
      )
