---
title: Research
nav:
  order: 1
  tooltip: Published works
---

# {% include icon.html icon="fa-solid fa-microscope" %}Research

At RoMA, our research focuses on developing foundation models for next-generation robotics. Our work spans multiple domains including computer vision, SLAM, sensor fusion, and deep learning.

{% include section.html %}

## Highlighted

{% comment %}
Display highlighted publications without year grouping
{% endcomment %}
{% for highlight in site.data.highlights %}
  {% include citation.html 
     id=highlight.id
     type=highlight.type
     title=highlight.title
     authors=highlight.authors
     publisher=highlight.publisher
     date=highlight.date
     link=highlight.link
     image=highlight.image
     description=highlight.description
     style="rich"
  %}
{% endfor %}

{% include section.html %}

## All

{% include search-box.html %}

{% include search-info.html %}

{% comment %}
Display all publications grouped by year, excluding highlighted ones to avoid duplicates
{% endcomment %}
{% assign highlight_ids = site.data.highlights | map: "id" %}
{% assign filtered_citations = "" | split: "," %}
{% for citation in site.data.citations %}
  {% unless highlight_ids contains citation.id %}
    {% assign filtered_citations = filtered_citations | push: citation %}
  {% endunless %}
{% endfor %}
{% assign years = filtered_citations | group_by_exp: "d", "d.date | date: '%Y'" | sort: "name" | reverse %}

{% for year in years %}
  {% assign data = year.items | sort: "date" | reverse %}
  
  <h3 id="{{ year.name }}">{{ year.name }}</h3>
  
  {% for citation in data %}
    {% include citation.html 
       id=citation.id
       type=citation.type
       title=citation.title
       authors=citation.authors
       publisher=citation.publisher
       date=citation.date
       link=citation.link
       style="rich"
    %}
  {% endfor %}
{% endfor %}
