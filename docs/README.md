# CLTL/Pepper Documentation

To add documentation:
1. Document code in [NumpyDoc](https://numpydoc.readthedocs.io/en/latest/format.html) format
2. Add additional text in ReStructuredText format
2. Make sure to ```pip install sphinx numpydoc sphinx_rtd_theme```
3. Make sure to ```(source) activate``` the pepper environment
4. Generate API documentation sources: ```make api```
5. Generate HTML pages from API documentation sources: ```make html```