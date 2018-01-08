# Adversarial Referential Game

## Links

Some useful links.

- Flickr API - https://www.flickr.com/services/api/
- Flickr API (flickr.phors.search) - https://www.flickr.com/services/api/flickr.photos.search.html
- Flickr API (python client) - https://stuvel.eu/flickrapi-doc/

## Features

Most of these are "Work in Progress", but hopefully should be available in the GUI in addition to being a script.

1. Search: Give "label" and "query". Scrape results from flickr as a child process. Option to skip database.
2. View: Look at all labels and urls that have been scraped.
3. Download: Trigger a download for urls that have been scraped.
4. Export-Crowdflower: Create a crowdflower csv file.
5. Preprocess-Heuristic-Imagenet: Run an imagenet classifier on the data.
6. Preprocess-Heuristic-MultimodalGame: Run a pretrained classifer from the MMGame project.
7. Preprocess-Duplicates: Detect duplicates. Optionally label a file as a duplicate, pointing to the source. Otherwise update "isduplicate-last-checked" and set "duplicate=False".
8. Manual Annotation.
9. Export-Dataset-Splits: Given some parameters, create a dataset.

# License

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
