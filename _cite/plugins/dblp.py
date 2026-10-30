"""
DBLP plugin for fetching publications from DBLP XML API
Processes entries from _data/dblp*.yaml files
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import Request, urlopen
from util import *


def main(entry):
    """
    receives single list entry from dblp data file
    returns list of sources to cite
    """

    # get author id from entry (DBLP PID like "154/4313")
    author_id = get_safe(entry, "author_id", "")

    if not author_id:
        raise Exception('No "author_id" key in entry. Use your DBLP PID (e.g., "154/4313" from https://dblp.org/pid/154/4313.html)')

    # query DBLP XML API
    @log_cache
    @cache.memoize(name=__file__, expire=1 * (60 * 60 * 24))
    def query_by_pid(pid):
        """Query DBLP by author PID using XML API"""
        url = f"https://dblp.org/pid/{pid}.xml"
        request = Request(url=url)
        response = urlopen(request).read()
        # DBLP may return an HTML bot-check page instead of XML; don't cache it
        if not response.lstrip().startswith(b"<?xml"):
            raise Exception(
                "DBLP did not return XML (likely blocked by its anti-bot check). "
                "Try again later, download the XML manually and set xml_file, "
                "or add publications manually in _data/sources.yaml."
            )
        return response

    # use a manually downloaded DBLP XML file if given, otherwise fetch from DBLP
    xml_file = get_safe(entry, "xml_file", "")
    if xml_file:
        xml_data = (Path("_data") / xml_file).read_bytes()
    else:
        xml_data = query_by_pid(author_id)

    # parse XML
    root = ET.fromstring(xml_data)

    # list of sources to return
    sources = []

    # find all publication elements (inside <r> elements)
    # publication types: article, inproceedings, proceedings, book, incollection, phdthesis, mastersthesis, www
    for r_elem in root.findall('.//r'):
        for pub in r_elem:
            # create source
            source = {}

            # get title
            title_elem = pub.find('title')
            title = title_elem.text if title_elem is not None else ""
            # Clean up title (remove trailing period if present)
            if title:
                title = title.strip()
                if title.endswith('.'):
                    title = title[:-1]

            # get year
            year_elem = pub.find('year')
            year = year_elem.text if year_elem is not None else ""

            # get DOI from ee (electronic edition) URLs
            doi = None
            for ee in pub.findall('ee'):
                if ee.text and 'doi.org' in ee.text:
                    # extract DOI from URL
                    match = re.search(r'doi\.org/(.+)$', ee.text)
                    if match:
                        doi = match.group(1)
                        break

            # get venue/publisher
            venue = ""
            venue_elem = pub.find('journal') or pub.find('booktitle')
            if venue_elem is not None:
                venue = venue_elem.text or ""

            # get authors
            authors = []
            for author in pub.findall('author'):
                if author.text:
                    authors.append(author.text)

            # get URL (first ee element)
            url = ""
            ee_elem = pub.find('ee')
            if ee_elem is not None and ee_elem.text:
                url = ee_elem.text

            # build source
            if doi:
                # prefer DOI for manubot citation
                source["id"] = f"doi:{doi}"
            else:
                # manual entry if no DOI
                if title:
                    source["title"] = title
                if authors:
                    source["authors"] = authors
                if venue:
                    source["publisher"] = venue
                if year:
                    source["date"] = f"{year}-01-01"
                if url:
                    source["link"] = url

            # copy fields from entry to source (allows overrides)
            source.update(entry)

            # remove the query fields from the source
            source.pop("author_id", None)
            source.pop("xml_file", None)

            # add source to list if it has content
            if source.get("id") or source.get("title"):
                sources.append(source)

    return sources
