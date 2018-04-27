# SIGSEP MUS 30s Cut-List Generator

This repository aims to generate a cut-list for generating excerpts from the
[MUSDB18](https://sigsep.github.io/musdb.html) music data set.

Note that this project does not generate audio. Please see
[sigsep-mus-2018-trim](https://github.com/deeuu/sigsep-mus-2018-trim) which will
generate audio previews from a cut-list created using this software.

### Method

The idea is to generate excerpts of 30s [1]

### Usage

* Install python3.6 requirements using `pip install -r requirements.txt`
* Run `python generate_cutlist.py --musdb /path/to/musdb --duration 30`
* For the [decoded wav dataset](https://github.com/sigsep/sigsep-mus-io), run `python generate_cutlist.py --musdb /path/to/musdb --iswav --duration 30`
* For further applications, you can use the [previews trim generator](https://github.com/deeuu/sigsep-mus-2018-trim)

### Download Previews

* Pre-computed preview segments [can be downloaded here](https://github.com/sigsep/sigsep-mus-previews/releases/download/v0.2/30s_previews.csv)

### References

[1] R. Bittner, J. Salamon, M. Tierney, M. Mauch, C. Cannam and J. P. Bello, "MedleyDB: A Multitrack Dataset for Annotation-Intensive MIR Research", in 15th International Society for Music Information Retrieval Conference, Taipei, Taiwan, Oct. 2014.
