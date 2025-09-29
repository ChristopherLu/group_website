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

{% include list.html data="highlights" component="citation" style="rich" %}

{% include section.html %}

## All

{% include search-box.html %}

{% include search-info.html %}

{% comment %}
Display all publications except those already highlighted to avoid duplicates
{% endcomment %}
{% assign highlight_ids = site.data.highlights | map: "id" %}
{% for citation in site.data.citations %}
  {% unless highlight_ids contains citation.id %}
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
  {% endunless %}
{% endfor %}
