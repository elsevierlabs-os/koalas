# Koalas

Koalas is a [Pandas](http://pandas.pydata.org/) based package for manipulation, filtering, matching and characterization of term lists.

## Contents

- [Installation](#installation)
    - [Direct installation to simply use Koalas](#direct-installation-to-simply-use-koalas)
    - [Install Koalas for development](#install-koalas-for-development)
- [General use](#general-use)
- [Tutorials](#tutorials)
- [Release notes](#release-notes)
- [module *koalas*](#module-koalas)
    - [class **WordFrame**](#class-wordframe)
    - [class **WordList**](#class-wordlist)
- [module *koalas.scripts*](#module-koalas.scripts)
- [module *koalas.lists*](#module-koalas.lists)
    - [Available Lists](#available-lists)


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
## module *koalas*:

- **read_csv** *(filename, provenance=None, *args, **kwargs)*:

     Read the contents of a CSV file into a WordFrame. Provenance info can be passed as a dictionary or as a list of dictionaries for each column. 

- **read_json** *(filename, provenance=None)*:

     Read the contents of a JSON file into a WordFrame. Recognizes saved metadata and attaches it to the WordFrame. As a fallback provenance info can be passed as a dictionary or as a list of dictionaries for each column. 

- **read_excel** *(filename, *args, provenance=None, **kwargs)*:

     Read the contents of a JSON file into a WordFrame. Provenance info can be passed as a dictionary or as a list of dictionaries for each column. This function requires the package `xlrd` to be installed. 

- **read_graph** *(endpointURL, query, username='', password='')*:

     Queries a SPARQL endpoint at `endpointURL` with `query`. 

- **make_triples** *(sub, pre, obj, filename)*:

     *No description yet*

- **concat** *(wordframes, *args, **kwargs)*:

     *No description yet*

- **match** *(base, query, steps=None, on=None, left_on=None, right_on=None, left_all=False, right_all=False, left_suff=None, right_suff=None, left_drop_matched=True, right_drop_matched=False)*:

     This function takes two wordframes, base and query, adds several derived columns as defined in comparison and tries to match them. 

- **match_labels** *(df1, df2, steps, df1_metadata, df2_metadata, df1_keep_all=True, df2_keep_all=True)*:

      Takes two dataframe as input and matches a label column in one to a label column in the other. Parameters: - df1, df2: two pandas DataFrames - steps: list of strings with names of methods to call for the stepwise matching - df1_metadata, df1_metadata: respective metadata for the two DataFrames as a dictionary with the following entries: - name (optional): string that serves as name - source (optional): string with provenance information - labelColumn (required): name of the column containing the labels that are to be matched - conceptColumn (optional): UID of the concept (not the label) - df1_keep_all, df2_keep_all: if `True` the respective non- matched labels are returned as well Returns: - one dataframe with the matched entries and all of the original columns plus: a column `matched_how` that after which step the strings matched and a column `matched_string` that contains the actually matched string. 

- **match_concepts** *(matched_labels, df1_metadata, df2_metadata, one_to_one=True)*:

     *No description yet*

### class **WordFrame**:

- **rename** *(*args, **kwargs)*:

     Overrides the Pandas DataFrame method to consider metadata. 

- **merge** *(second, *args, **kwargs)*:

     Overrides the Pandas DataFrame method to consider metadata. 

- **concat** *(wordframes, *args, **kwargs)*:

     Overrides the Pandas DataFrame method to consider metadata. 

- **apply_by_row** *(*args, to=None, **kwargs)*:

     *No description yet*

- **agg_by_col** *(func)*:

     *No description yet*

- **apply** *(*args, on=None, to=None, **kwargs)*:

     Overrides the Pandas DataFrame method. In contrast to Pandas the `apply` method is called on a column (wordlist) in line with the behaviour of other methods in Koalas. Accordingly can take an `on` and a `to` argument. 

- **astype** *(*args, on=None, to=None, **kwargs)*:

     Overrides the Pandas DataFrame method. In contrast to Pandas the `astype` method is called on a column (wordlist) in line with the behaviour of other methods in Koalas. Accordingly can take an `on` and a `to` argument. 

- **deduplicate** *(on=None, steps=None)*:

     Groups on (a) specific column(s) and returns the first row of each group. The parameter `on` takes a column name as string or a list of column names. To influence which row is returned, sort the wordframe before. 

- **filter** *(on=None, where='')*:

     Filters the rows of the wordframe on the column specified with `on`, with the condition given to `where`. So `wf.filter(on='x', where='=="y"')` is equivalent to `wf[wf['x'] == 'y']`. The advantage is in method chaining where the syntax `[lambda wf: wf['x'] == 'y']` can be avoided. 

- **match_to** *(query, steps=None, on=None, left_on=None, right_on=None, left_all=True, right_all=False, left_suff=None, right_suff=None, left_drop_matched=True, right_drop_matched=False)*:

     Match to another wordframe `query` on the column given by `on` (defaults to the column last used). As `steps` a list of matching steps can be given, any WordList method is valid. If the columns to be compared differ between the two wordframes use `left_on` and `right_on`. To return all rows, including the ones that did not match, set `left_all` or `right_all` to `True`, respectively. To remove rows that matched so they are not matched in the next matching step set `left_drop_matched` and/or `right_drop_matched` to `True`. 

- **match_to_self** *(steps=None, on=None, all=False, drop_matched=False)*:

     Match a wordframe to itself to identify duplicates or similar terms. Matches of a term to itself are filtered out. By default only matched terms are returned, set `all` to `False` to change this behaviour. 

- **to_json** *(filename, additional=None)*:

     Saves the wordframe to a JSON file including all metadata. 

- **stack_list** *(on=None, to=None)*:

     Works on a column containing a list in each row. Each entry of the list is placed in a new row, with the contents of the other columns repeated. 

### class **WordList**:

- **apply** *(function, convert_dtype=True, args=(), **kwargs)*:

     Overrides original implementation of `apply` to take into account NaNs. For this the callable supplied in `apply` is wrapped in a function testing for NaN and is only called on non-NaN values. This results in a performance penalty but solves the problem that most functions outside of Pandas are not NaN-aware. 

- **filter** *(where='')*:

     Filters the rows of the wordlist with the condition given to `where`. So `wl.filter(where='=="y"')` is equivalent to `wf[wf == 'y']`. The advantage is in method chaining where the syntax `[lambda wf: wf == 'y']` can be avoided. 

- **remove_words** *(wordlist)*:

     Remove any words in the string that matches an exact entry in `wordlist`. 

- **remove_first_word** *()*:

     Removes the first word in the string. If there is only one word NaN is returned. 

- **remove_last_word** *()*:

     Removes the last word in the string. If there is only one word NaN is returned. 

- **replace_substrings** *(stringlist, repl='')*:

     Replaces any substring in the string that matches an exact entry in `stringlist`. By default it is replaced with an empty string (i.e. removed). Passing a dictionary you can give replacements by row. 

- **resolve_medical_terms** *()*:

     *No description yet*

- **remove_punctuation** *(replace_with_whitespace=False)*:

     Removes any punctuation from the string, including some non-ASCII. 

- **remove_whitespace** *()*:

     Replaces any whitespace in the input string with a single space. 

- **remove_qualifiers** *()*:

     Removes 'qualifiers' that are enclosed in parentheses, e.g. (biology), from the string including adjacent extra whitespace. 

- **remove_control_characters** *()*:

     Removes control characters. 

- **replace_non_ascii** *(replacement='')*:

     Replaces non-ASCII characters with the character in `replacement`. 

- **replace_url_encoded_characters** *()*:

     *No description yet*

- **replace_typographic_forms** *()*:

     Replaces curly single and double quotes with straight ones, and different dashes and minus with a simple hyphen. 

- **normalize_unicode** *()*:

     Replace unicode characters by their canonical form. 

- **remove_accents** *()*:

     Remove accents from letters by decomposing their canonical unicode glyph. 

- **replace_accented_characters** *(remove_others=False, replacement='?')*:

     Replaces accented, non-ASCII characters with an ASCII equivalent as defined in the list `accented characters`. 

- **replace_greek_characters** *()*:

     Replaces greek characters with their name in Latin script using the list `greek characters`. 

- **replace_words** *(wordmapping)*:

     Replaces words with another word defined in a dictionary (or a WordList with words to be replaced in the index) passed into `wordmapping`. 

- **word_isin** *(wordlist, agg='any')*:

     Returns `True` if any word or all words in the string match(es) an entry in `wordlist`, depending on the parameter `agg`. 

- **term_isin** *(termlist)*:

     Returns True if the entire string matches an entry in `termlist`. 

- **word_number** *()*:

     Returns the number of words in the string. 

- **pos_tag** *(pos_tag_function=None)*:

     Returns a list of POS tags corresponding to each word in the string. Uses the NLTK pos tagger by default but another one can be passed into the method through the `pos_tag_function` parameter. 

- **tokenize** *(tokenize_function=None)*:

     Returns a list of tokens for the string. Uses by default the NLTK TreebankWordTokenizer but another one can be passed into the method through the `tokenize_function` parameter. 

- **stem** *(stem_function=None)*:

     Returns the stem of each word in the string. Uses by default the NLTK SnowballStemmer but another one can be passed into the method through the `stem_function` parameter. 

- **lemmatize** *(lemmatize_function=None)*:

     Returns the lemma of each word in the string. Uses by default the NLTK WordNetLemmatizer but another one can be passed into the method through the `lemmatize_function` parameter. 

- **melt_list** *(column)*:

     *No description yet*

- **explode** *()*:

     *No description yet*

- **exact** *()*:

     Returns an exact copy of the string. This is the identity method for convenient use as a matching step. 

- **extract_acronym** *()*:

     Returns an acronym if found and otherwise NaN. This method looks for acronyms in parentheses that follow their expanded term, e.g. "United States of America (USA)". 

- **sort_words** *(descending=False)*:

     Returns the string with words arranged alphabetically. 

- **natural_word_order** *()*:

     Returns the string split on commas and reverses the order of tokens. 

- **normalize** *()*:

     Convenience function that calls after another the following methods: `str.lower`, `replace_special_characters`, `remove_punctuation`, `replace_greek_characters`, `replace_words(british_to_american)`, `remove_whitespace`. 

## module *koalas.scripts*:

 This module contains additional scripts that can be used on WordFrames. Scripts can be accesed through the `script` accessor like this: `terms.script.is_binomial_name(on='label')`. To avoid making dependencies of these scripts obligatory to install, they have to be explicitly imported (e.g. `import koalas.scripts.binomial_name`). New scripts can easily be added by providing a function that takes a single value or an entire WordList as input. Just add one of the decorators from the `register` module (`register_script_for_single_value` or `register_script_for_series`) like this: ``` @register_script_for_single_value def my_cool_function(value): do something with value return result ``` 

## module *koalas.lists*:

- **load** *(listname, substitutions=False, full_dataset=False)*:

     Loads a reference wordlist specified by `listname`. To get a wordlist with the terms as index and a substitution term as value set `substitutions` to `True`. This can be used with the `replace_words` method. Setting `full_dataset` to `True` returns a wordframe instead, including additional data columns if present. 

- **save** *(wordframe, listname, provenance, termColumn, substitutionColumn=None)*:

     Add a new reference wordlist to koalas. Given a wordframe, provenance information and name for the list a JSON file is saved in the folder `lists` within the koalas package. 

### Available Lists:

- **British English:**
  - *title*: British English and American English variants
  - *category*: high frequency words
  - *source*: unknown
  - *link*: unknown
  - *description*: A list of words whose spelling differs between British and American English.
  - *licence*: unknown
  - *version*: unknown
- **academic words:**
  - *title*: Academic words
  - *category*: domain specific terms
  - *source*: Dr Averil Coxhead, Victoria University of Wellington
  - *link*: https://www.victoria.ac.nz/lals/resources/academicwordlist
  - *description*: The list contains 570 word families which were selected according to principles. The list does not include words that are in the most frequent 2000 words of English. The AWL was primarily made so that it could be used by teachers as part of a programme preparing learners for tertiary level study or used by students working alone to learn the words most needed to study at tertiary institutions. The word list has been divided into sublists based on the frequency of occurrence of the words in the Academic Corpus. The words in Sublist 1 occur more frequently in the corpus than the other words in the list. Sublist 2 occurs with the next highest frequency.
  - *licence*: unknown
  - *version*: 2000
- **stopwords Humbolt:**
  - *title*: A list of 319 stopwords (Humbolt Stopwords)
  - *category*: stopwords
  - *source*: HumboltStopwords
  - *link*: http://xpo6.com/list-of-english-stop-words/
  - *description*: Stop Words are words which do not contain important significance to be used in Search Queries. Usually these words are filtered out from search queries because they return vast amount of unnecessary information.
  - *licence*: unknown
  - *version*: as of 2006-04-16
- **chemical elements:**
  - *title*: Chemical elements
  - *category*: domain specific terms
  - *source*: unknown
  - *link*: unknown
  - *description*: A list of the first 119 chemical elements.
  - *licence*: unknown
  - *version*: unknown
- **diseases:**
  - *title*: Diseases
  - *category*: domain specific terms
  - *source*: unknown
  - *link*: unknown
  - *description*: A list of 938 diseases including abbreviations and spelling variations.
  - *licence*: unknown
  - *version*: unknown
- **stopwords MySQL:**
  - *title*: 543 Stopwords used in MySQL
  - *category*: stopwords
  - *source*: Ranks.nl
  - *link*: https://www.ranks.nl/stopwords
  - *description*: Single words including contracted words with apostrophe.
  - *licence*: unknown
  - *version*: unknown
- **greek characters:**
  - *title*: Greek characters
  - *category*: characters
  - *source*: Wikipedia
  - *link*: https://en.wikipedia.org/wiki/Greek_alphabet
  - *description*: A list of greek characters and their names in Latin script.
  - *licence*: free
  - *version*: 800 B.C.
- **common words Google:**
  - *title*: 20000 most common words according to Google
  - *category*: high frequency words
  - *source*: Google
  - *link*: https://github.com/first20hours/google-10000-english/blob/master/20k.txt
  - *description*: This repo contains a list of the 10,000 most common English words in order of frequency, as determined by n-gram frequency analysis of the Google's Trillion Word Corpus. This repo is useful as a corpus for typing training programs. According to analysis of the Oxford English Corpus, the 7,000 most common English lemmas account for approximately 90% of usage, so a 10,000 word training corpus is more than sufficient for practical training applications.
  - *licence*: Web 1T 5-gram Version 1 Agreement
  - *version*: 2016/07/18 (commit: cb727a8ef0932d7d9519e8fe3973ad0a9600170d)
- **common words Gutenberg:**
  - *title*: The 36663 most common words in Project Gutenberg
  - *category*: high frequency words
  - *source*: Wiktionary
  - *link*: https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists#Project_Gutenberg
  - *description*: Most common words in Project Gutenberg: These lists are the most frequent words, when performing a simple, straight (obvious) frequency count of all the books found on Project Gutenberg. The list of books was downloaded in July 2005, and "rsynced" monthly thereafter. These are mostly English words, with some other languages finding representation to a lesser extent. Many Project Gutenberg books are scanned once their copyright expires, typically book editions published before 1923, so the language does not necessarily always represent current usage. For example, "thy" is listed as the 280th most common word. Also, with 24,000+ books, the text of the boilerplate warning for Project Gutenberg appears on each of them.
  - *licence*: Creative Commons Attribution-ShareAlike License
  - *version*: as of 2006-04-16
- **accented characters:**
  - *title*: Accented characters
  - *category*: characters
  - *source*: AnAGram
  - *link*: unknown
  - *description*: A list of accented characters and ASCII characters that should be used to replace them.
  - *licence*: unknown
  - *version*: unknown
- **demonyms:**
  - *title*: List of countries and demonyms
  - *category*: geo-political entities
  - *source*: Wikipedia
  - *link*: https://en.wikipedia.org/wiki/List_of_adjectival_and_demonymic_forms_for_countries_and_nations
  - *description*: List of countries and territories with adjectives and names of their inhabitants
  - *licence*: Creative Commons Attribution-ShareAlike License
  - *version*: 06:57, 13 May 2018
- **stopwords Stanford:**
  - *title*: 257 Stopwords used in the Standford Core NLP functionalities
  - *category*: stopwords
  - *source*: Stanford NLP
  - *link*: https://github.com/stanfordnlp/CoreNLP/blob/master/data/edu/stanford/nlp/patterns/surface/stopwords.txt
  - *description*: Single words including punctuation and contracted words with apostrophe.
  - *licence*: GNU GPL v3
  - *version*: 2016/01/23 (commit: ceefe81491183e557cd047755a5a88a90bfeb2af)
- **cities:**
  - *title*: List of the 223 largest cities
  - *category*: geo-political entities
  - *source*: Wikipedia
  - *link*: https://en.wikipedia.org/wiki/List_of_largest_cities
  - *description*: A list of large cities and the countries they lie in.
  - *licence*: Creative Commons Attribution-ShareAlike License
  - *version*: 04:40, 18 April 2018
- **common words BYU:**
  - *title*: 5000 Most Frequent words in a balanced corpus of American English
  - *category*: high frequency words
  - *source*: Brigham Young University
  - *link*: https://www.wordfrequency.info/free.asp
  - *description*: The 5,000-60,000 word lists are based on the only large, genre-balanced, up-to-date corpus of American English -- the 560 million word Corpus of Contemporary American English (COCA).
  - *licence*: free to use
  - *version*: unknown, fetched 2018/04/19

