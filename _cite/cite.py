"""
cite process to convert sources and metasources into full citations
"""

import re
import traceback
from importlib import import_module
from pathlib import Path
from dotenv import load_dotenv
from util import *


def is_arxiv_paper(citation):
    """
    Check if a citation is an arXiv/preprint paper.
    Based on bibtex-to-manubot deduplication logic.
    """
    _id = get_safe(citation, "id", "").lower()
    publisher = get_safe(citation, "publisher", "").lower()
    link = get_safe(citation, "link", "").lower()

    # Check various indicators of arXiv papers
    if "arxiv" in _id:
        return True
    if publisher in ["arxiv", "corr"]:
        return True
    if "arxiv.org" in link:
        return True
    return False


def normalize_title(title):
    """Normalize title for comparison by lowercasing and extracting words."""
    if not title:
        return []
    title = title.lower()
    # Extract words using regex
    words = re.findall(r'\b\w+\b', title)
    return words


def find_title_overlap(title1, title2, min_words=6):
    """
    Find the longest consecutive word overlap between two titles.
    Returns the count of consecutive matching words.
    """
    words1 = normalize_title(title1)
    words2 = normalize_title(title2)

    if not words1 or not words2:
        return 0

    max_overlap = 0

    # Check all possible starting positions
    for i in range(len(words1)):
        for j in range(len(words2)):
            # Count consecutive matches starting from these positions
            overlap = 0
            while (i + overlap < len(words1) and
                   j + overlap < len(words2) and
                   words1[i + overlap] == words2[j + overlap]):
                overlap += 1
            max_overlap = max(max_overlap, overlap)

    return max_overlap


def remove_arxiv_duplicates(citations, min_overlap=6):
    """
    Remove arXiv papers that have published versions.
    Based on bibtex-to-manubot Smart Deduplication logic.
    """
    # Separate arXiv and non-arXiv papers
    arxiv_papers = [c for c in citations if is_arxiv_paper(c)]
    non_arxiv_papers = [c for c in citations if not is_arxiv_paper(c)]

    log(f"Found {len(arxiv_papers)} arXiv paper(s) and {len(non_arxiv_papers)} published paper(s)")

    # Track which arXiv papers to remove
    arxiv_ids_to_remove = set()

    # Compare each arXiv paper with non-arXiv papers
    for arxiv_paper in arxiv_papers:
        arxiv_title = get_safe(arxiv_paper, "title", "")
        arxiv_id = get_safe(arxiv_paper, "id", "")

        for published_paper in non_arxiv_papers:
            published_title = get_safe(published_paper, "title", "")

            overlap = find_title_overlap(arxiv_title, published_title, min_overlap)

            if overlap >= min_overlap:
                arxiv_ids_to_remove.add(arxiv_id)
                log(f"Removing arXiv duplicate: '{arxiv_title[:50]}...'", indent=1)
                log(f"  Published version: '{published_title[:50]}...' (overlap: {overlap} words)", indent=1)
                break  # No need to check other published papers

    # Filter out duplicates
    filtered_citations = [
        c for c in citations
        if get_safe(c, "id", "") not in arxiv_ids_to_remove
    ]

    removed_count = len(citations) - len(filtered_citations)
    if removed_count > 0:
        log(f"Removed {removed_count} arXiv duplicate(s)", level="INFO")

    return filtered_citations


# load environment variables
load_dotenv()


# save errors/warnings for reporting at end
errors = []
warnings = []

# output citations file
output_file = "_data/citations.yaml"


log()

log("Compiling sources")

# compiled list of sources
sources = []

# in-order list of plugins to run
plugins = ["google-scholar", "pubmed", "orcid", "dblp", "sources"]

# loop through plugins
for plugin in plugins:
    # convert into path object
    plugin = Path(f"plugins/{plugin}.py")

    log(f"Running {plugin.stem} plugin")

    # get all data files to process with current plugin
    files = Path.cwd().glob(f"_data/{plugin.stem}*.*")
    files = list(filter(lambda p: p.suffix in [".yaml", ".yml", ".json"], files))

    log(f"Found {len(files)} {plugin.stem}* data file(s)", indent=1)

    # loop through data files
    for file in files:
        log(f"Processing data file {file.name}", indent=1)

        # load data from file
        try:
            data = load_data(file)
            # check if file in correct format
            if not list_of_dicts(data):
                raise Exception(f"{file.name} data file not a list of dicts")
        except Exception as e:
            log(e, indent=2, level="ERROR")
            errors.append(e)
            continue

        # loop through data entries
        for index, entry in enumerate(data):
            log(f"Processing entry {index + 1} of {len(data)}, {label(entry)}", level=2)

            # run plugin on data entry to expand into multiple sources
            try:
                expanded = import_module(f"plugins.{plugin.stem}").main(entry)
                # check that plugin returned correct format
                if not list_of_dicts(expanded):
                    raise Exception(f"{plugin.stem} plugin didn't return list of dicts")
            # catch any plugin error
            except Exception as e:
                # log detailed pre-formatted/colored trace
                print(traceback.format_exc())
                # log high-level error
                log(e, indent=3, level="ERROR")
                errors.append(e)
                continue

            # loop through sources
            for source in expanded:
                if plugin.stem != "sources":
                    log(label(source), level=3)

                # include meta info about source
                source["plugin"] = plugin.name
                source["file"] = file.name

                # add source to compiled list
                sources.append(source)

            if plugin.stem != "sources":
                log(f"{len(expanded)} source(s)", indent=3)


log("Merging sources by id")

# merge sources with matching (non-blank) ids
for a in range(0, len(sources)):
    a_id = get_safe(sources, f"{a}.id", "")
    if not a_id:
        continue
    for b in range(a + 1, len(sources)):
        b_id = get_safe(sources, f"{b}.id", "")
        if b_id == a_id:
            log(f"Found duplicate {b_id}", indent=2)
            sources[a].update(sources[b])
            sources[b] = {}
sources = [entry for entry in sources if entry]


log(f"{len(sources)} total source(s) to cite")


log()

log("Generating citations")

# list of new citations
citations = []


# loop through compiled sources
for index, source in enumerate(sources):
    log(f"Processing source {index + 1} of {len(sources)}, {label(source)}")

    # if explicitly flagged, remove/ignore entry
    if get_safe(source, "remove", False) == True:
        continue

    # new citation data for source
    citation = {}

    # source id
    _id = get_safe(source, "id", "").strip()

    # manubot doesn't work without an id
    if _id:
        log("Using Manubot to generate citation", indent=1)

        try:
            # run manubot and set citation
            citation = cite_with_manubot(_id)

        # if manubot cannot cite source
        except Exception as e:
            plugin = get_safe(source, "plugin", "")
            file = get_safe(source, "file", "")
            # if regular source (id entered by user), throw error
            if plugin == "sources.py":
                log(e, indent=3, level="ERROR")
                errors.append(f"Manubot could not generate citation for source {_id}")
            # otherwise, if from metasource (id retrieved from some third-party api), just warn
            else:
                log(e, indent=3, level="WARNING")
                warnings.append(
                    f"Manubot could not generate citation for source {_id} (from {file} with {plugin})"
                )
                # discard source from citations
                continue

    # preserve fields from input source, overriding existing fields
    citation.update(source)

    # ensure date in proper format for correct date sorting
    if get_safe(citation, "date", ""):
        citation["date"] = format_date(get_safe(citation, "date", ""))

    # add new citation to list
    citations.append(citation)


log()

log("Removing arXiv duplicates")

# Remove arXiv papers that have published versions (Smart Deduplication)
citations = remove_arxiv_duplicates(citations, min_overlap=6)

log(f"{len(citations)} citation(s) after deduplication")


log()

log("Saving updated citations")


# save new citations
try:
    save_data(output_file, citations)
except Exception as e:
    log(e, level="ERROR")
    errors.append(e)


log()


# exit at end, so user can see all errors/warnings in one run
if len(warnings):
    log(f"{len(warnings)} warning(s) occurred above", level="WARNING")
    for warning in warnings:
        log(warning, indent=1, level="WARNING")

if len(errors):
    log(f"{len(errors)} error(s) occurred above", level="ERROR")
    for error in errors:
        log(error, indent=1, level="ERROR")
    log()
    exit(1)

else:
    log("All done!", level="SUCCESS")

log()
