# SIGSEP MUS 30s Preview Generator

This repository aims to generate 30s excerpts from the [MUSDB18](https://sigsep.github.io/musdb.html) music data set.

### Method

The idea is to generate excerpts of 30s [1]

### Usage

* Install python3.6 requirements using `pip install -r requirements.txt`
* Run `python generate_previews.py --musb /path/to/musdb`
* For the [decoded wav dataset](https://github.com/sigsep/sigsep-mus-io), run `python generate_previews.py --musb /path/to/musdb --iswav`
* For further applications, you can use the [previews trim generator](https://github.com/faroit/sisec-mus-trim)

### Download Previews

* Pre-computed preview segmentes [can be downloaded here](https://github.com/sigsep/sigsep-mus-previews/releases/download/v0.2/30s_previews.csv)

### References

[1] R. Bittner, J. Salamon, M. Tierney, M. Mauch, C. Cannam and J. P. Bello, "MedleyDB: A Multitrack Dataset for Annotation-Intensive MIR Research", in 15th International Society for Music Information Retrieval Conference, Taipei, Taiwan, Oct. 2014.
