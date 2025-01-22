# Koalas

Koalas is a [Pandas](http://pandas.pydata.org/) based package for manipulation, filtering, matching and characterization of term lists.

{TOC}

## Installation

Koalas is a ready to install Python package. You need to have Python 3 installed (not tested with Python 2) and the packages in the requirements file.

```sh
pip install -r requirements.txt
```

### Direct installation to simply use Koalas

You can install Koalas directly from this GitLab repository. On the command line type

```sh
pip install git+https://gitlab.et-scm.com/candi-coca/koalas.git
```

To upgrade Koalas to a new version run:

```sh
pip install --upgrade koalas
```

### Install Koalas for development

Clone the repository to a convenient location for you.

```sh
git clone https://github.com/elsevierlabs-os/koalas.git
```

Then install Koalas without transferring it to the Python site-packages directory. This way any change to the source files is immediately reflected when you use the package.

```sh
cd koalas
pip install -e .
```

## General use

The central unit in Koalas is the WordFrame, an extended version oof the Pandas DataFrame. Any operation that can be used on a DataFrame also works on a WordFrame. Each column of a WordFrame is a WordList which builds on Pandas' Series.

Additionally to the basic Pandas operations Koalas implements a number of functions to specifically work with terms and words.

## Tutorials

These tutorials are in the form of Jupyter Notebooks. They can be used interactively after downloading.

- [Get started](examples/car-tutorial.ipynb)
- [Metadata and provenance information](examples/metadata-and-provenance.ipynb)
- [Matching to another list of terms](examples/match-labels.ipynb)

## Release notes

Please check the [release notes](CHANGELOG.md) for detailed changes by version.
