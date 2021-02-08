# CLTL/Pepper Documentation

To add documentation:
1. Document code in [NumpyDoc](https://numpydoc.readthedocs.io/en/latest/format.html) format
2. Add additional text in ReStructuredText format
3. Make sure to ```(source) activate``` the pepper environment
2. Make sure to ```pip install sphinx numpydoc sphinx_rtd_theme```
4. Generate API documentation sources: ```make api```
5. Generate HTML pages from API documentation sources: ```make html```


Some Friendly Sphinx/ReStructuredText Reminders:

- Cross-Reference all the things: 
    - Classes: ``` :class:`~pepper.framework.abstract.camera.AbstractCamera` ```
    - Packages & Modules: ``` :mod:`~pepper.framework.component` ```
    - Functions ``` :func:`~pepper.config.get_backend` ```
    - Methods ``` :meth:`~pepper.brain.basic_brain.BasicBrain.get_classes` ```
    
- Add Links to External Resources: ``` `Text to Show <https://www.verynice.url.com>`_ ```
