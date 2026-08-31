# Meta-Repository of Sanskrit eTexts

This repository aggregates Sanskrit etexts and their metadata from major digital libraries, including GRETIL, the Digital Sanskrit Buddhist Canon (DSBC), Wikisource, Muktabodha, and independent contributions from Hamburg University researchers.

### Core Concept

External collections are imported and standardized with TEI XML headers to record their origin, history, and licensing. To ensure data integrity and ease of analysis, metadata is maintained dually:

* **CSV Files:** The repository's ground truth. They allow corpus-level analysis and tracking authors, categories, translations, URLs, and cross-collection duplicates.
* **TEI Headers:** Ensure metadata remains permanently attached to individual files for independent extraction and web rendering.

Utility scripts automate corpus management, including two-way metadata synchronization (CSV to TEI and vice versa), file auditing, and the generation of deduplicated plain-text subsets for targeted NLP research.

*Ongoing Challenges:* Achieving consistent, complete metadata and enforcing uniform formatting standards across highly heterogeneous source texts. It's hoped that granular TEI-tagging can be achieved in due course.

### The Collections

* **GRETIL:** Sourced from the [sanskrit-texts/gretil-corpus](https://github.com/sanskrit-texts/gretil-corpus) fork. File contents currently remain unmodified.
* **GRETIL Extra:** GRETIL texts absent from the main GitHub repository, retrofitted with basic TEI headers.
* **DSBC:** Texts scraped from the [DSBC website](https://www.dsbcproject.org/), combined, stripped of HTML, and outfitted with TEI headers containing source and copyist information.
* **Wikisource & Muktabodha:** Manually catalogued and marked up by student assistants, supplemented by cumulative bulk downloads where available.
* **Hamburg:** Etexts provided by Indologists at the University of Hamburg. (Texts of unknown origin can be removed upon request).

### Repository Structure

* **`corpus/`**: Primary storage for TEI XML source texts, organized into subdirectories by collection.
* **`corpus_txt/`**: Plain-text derivatives generated from the XML corpus for downstream NLP processing and reading.
* **`metadata/`**: CSV catalogs containing bibliographic data and deduplication tracking.
* **`scripts/`**: Python utilities for corpus management. The primary auditing tool, `corpus_validate_filenames.py`, ensures 1:1 parity between CSV records and physical files while validating all duplication pointers.
* **`src/`**: Raw files downloaded, scraped, or otherwise acquired prior to TEI transformation.

---

The structure and scripts of this repository are being developed for the [Intellexus Project](https://intellexus.net/) and are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0).
