from distutils.core import setup
from setuptools.command.install import install
from setuptools.command.develop import develop

def download_nltk_data():
    import nltk
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

class PostInstall(install):
    def run(self):
        super().run()
        download_nltk_data()

class PostDevelop(develop):
    def run(self):
        super().run()
        download_nltk_data()

setup(name='Koalas',
      version='0.3.0',
      description='Koalas - Pandas extension for words',
      url='https://gitlab.et-scm.com/candi-coca/koalas',
      author='Till Bey',
      author_email='t.bey@elsevier.com',
      packages=['koalas', 'koalas.lists', 'koalas.scripts'],
      license='copyrighted',
      install_requires=['pandas>=0.23.0', 'numpy', 'nltk', 'openpyxl', 'xlrd'],
      include_package_data=True,
      cmdclass={'install': PostInstall, 'develop': PostDevelop}
     )
