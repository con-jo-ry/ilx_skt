# gretil-corpus

## Workflow taken so far

* Get the tags inventory, in order to replace the HTML tags.

* Check the validity of files as XMl files.

* Check the validity of files as TEI files.

* Get the inventory of all the characters in ```body``` elements.

* Split the words.

* Generate the index (fill text, titles, ??) (maybe ask https://michaelmeyer.fr/ for a lexicon?).

## Changes

### For the validation according to XML specification

* Fixed some duplicated ```@xml:id``` within the same document.

* For the ```@xml:id``` attributes that were invalid NCNames, I did the following replacements:

    * ```,``` with ```_comma_```;
    * ```*``` with ```_asterisk_```;
    * ```@``` with ```_at-sign_```;
    * ```:``` with ```_colon_```;
    * ```[``` with ```_left-square-bracket_```;
    * ```]``` with ```_right-square-bracket_```;
    * ```|``` with ```_pipeline_```;
    * ```/``` with ```_forward-slash_```;
    * ```(``` with ```_left-parenthesis_```;
    * ```)``` with ```_right-parenthesis_```;
    * space with nothing.

### For the validation according to TEI specification

* Replaced ```{http://www.tei-c.org/ns/1.0}NOTE``` tag with ```{http://www.tei-c.org/ns/1.0}note```.

* Replaced ```{http://www.tei-c.org/ns/1.0}p``` tag with ```{http://www.tei-c.org/ns/1.0}lg```.

* Added correct markers for divisions in file ```sa_viSNupurANa-crit.xml```.

## Work to do, on the semantic level of texts

* Further segmentation for the contents of ```lg``` elements that contain the delimiter ```|``` (see file ```sa_viSNupurANa-crit.xml```).

* There are ```lg``` elements without ```@xml:id```.

* Check ```@corresp```, to point to existing ID-s.

* For some files, the word separator is the full stop, see ```mahān.mahī.astabhayad.```.

* For some files, should the ```p``` element be kept?

* For the file ```sa_bhartRhari-vAkyapadIya.xml```, some ```note``` elements are, in fact, ```head``` elements, but no division of text is set, and I think there have to be divisions.

* The file ```sa_kiraNatantra1-6.xml``` is very poorly segmented.


## Work to do, generally speaking

* The XML files have to be valid.

* The TEI files have to valid according to TEI schema.

## Resources

[SwiftLaTeX, a WYSIWYG Browser-based LaTeX Editor](https://swiftlatex.com/) - maybe this can help with generation in the browser of a LaTeX file from a TEI file.

[MuPDF WASM](https://mupdf.readthedocs.io/en/latest/mupdf-wasm.html) - maybe this can help with generation in the browser of a PDF file from a TEI file.

[xml_schema_generator](https://docs.rs/xml_schema_generator/latest/xml_schema_generator/) - for generation of XML schema from XML files.

[Convert HTML to PDF using JavaScript](https://www.codexworld.com/convert-html-to-pdf-using-javascript-jspdf/)

[How To Convert HTML to PDF using JavaScript](https://stackoverflow.com/questions/74638117/how-to-convert-html-to-pdf-using-javascript)

[Sebastian Nehrdich via INDOLOGY, 2024.11.03]()
For those of you who want to use the dharmamitra Sanskrit grammatical capabilities that Oliver Hellwig and I published recently there is now a simple python package that calls our API: https://pypi.org/project/dharmamitra-sanskrit-grammar/

Please be aware that we might need to rate-limit the API so in case you have trouble to access or need more volume, feel free to reach out to me.

Also, for those of you who use emacs there is now a simple dharmamitra emacs extension that integrates translation and grammatical analysis capabilities into emacs: https://github.com/dharmamitra/dharmamitra-emacs

If you want to learn more about how the grammar model works, our preprint (which is more or less identical with the submitted version of the paper) is available here: https://arxiv.org/abs/2409.13920



