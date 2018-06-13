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

* Pre-computed 30s preview segments [can be downloaded here](https://github.com/sigsep/sigsep-mus-cutlist-generator/releases/download/v0.3/30s_previews.csv). These previews were generated using the original MUSDB18 data set as input.

* Pre-computed 7s preview segments [can be downloaded here](https://github.com/sigsep/sigsep-mus-cutlist-generator/releases/download/v0.3/7s_previews.csv). These previews were generated using the 30s previews as input, meaning that 
a sample index of 0 (or timestamp of 0s) denotes the beginning of the
corresponding 30s preview and **not** the start of the original track.

See the [latest release notes](https://github.com/sigsep/sigsep-mus-cutlist-generator/releases).

### References

[1] R. Bittner, J. Salamon, M. Tierney, M. Mauch, C. Cannam and J. P. Bello, "MedleyDB: A Multitrack Dataset for Annotation-Intensive MIR Research", in 15th International Society for Music Information Retrieval Conference, Taipei, Taiwan, Oct. 2014.
