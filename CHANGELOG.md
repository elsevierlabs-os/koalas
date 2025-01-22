# Release notes

## Version 0.3.0

 - new normalisation function: `url_normalise`.
 - new flagging functions: `has_lowercase_acronym` and `is_lowercase_acronym`.
 - fix the nan-aware apply function to deal with all versions of NaN.
 - allow any accessor method in matching steps
 - add unit tests

## Version 0.2.1

- new word lists:
  - greek characters and their names
  - words with difference in British English - American English
  - medical affixes and their meanings
  - academic words (thanks, Janneke!)
- allow to pass credentials in a query to a SPARQL endpoint
- deduplication of rows can now work with the same step-wise approach as matching
- new example on matching labels
- new method: replace typographic quotes and dashes by ASCII variants
- new method: extract acronyms from terms of pattern "expansion (acronym)"

## Version 0.2.0

- new mechanism to load reference lists (`kl.lists.load('name of list')`)
- thanks to Vero, many more word lists are included (e.g. geonames, diseases, common words, ...)
- new mechanism to include scripts for extending Koalas
- first extension script: recognize binomial species names by Anke
- improved matching machine: now additional arguments can be passed in for each step,
repeated application of step is possible, application of step to only one list of terms
- matching to self now possible
- and some more new methods on WordFrame/WordList

## Version 0.1.0

- original release
