---
title: Contact
nav:
  order: 5
  tooltip: Email, address, and location
---

# {% include icon.html icon="fa-regular fa-envelope" %}Contact

You can find us at the [Robotics with Multimodal Autonomy (RoMA) Lab](https://christopherlu.github.io/group_website/) at [University College London](https://www.ucl.ac.uk/)

{%
  include button.html
  type="email"
  text="xiaoxuan.lu@ucl.ac.uk"
  <!-- link="xiaoxuan.lu@ucl.ac.uk" -->
%}
{%
  include button.html
  type="address"
  tooltip="Our location on Google Maps for easy navigation"
  link="https://www.google.com/maps/dir//1+Pool+St,+London+E20+2AF/@51.5382365,-0.0921534,12z/data=!4m8!4m7!1m0!1m5!1m1!1s0x48761d66f90b73d1:0xcc0139dfc8c5e7c7!2m2!1d-0.0097532!2d51.5382654?entry=ttu&g_ep=EgoyMDI1MDkyMi4wIKXMDSoASAFQAw%3D%3D"
%}

{% include section.html %}

{% capture col1 %}

{%
  include figure.html
  image="images/ucl_east.jpg"
  caption="One Pool Street"
%}

{% endcapture %}

{% capture col2 %}

{%
  include figure.html
  image="images/ucl_robotics.jpg"
  caption="Robotics & AI Lab"
%}

{% endcapture %}

{% include cols.html col1=col1 col2=col2 %}

{% include section.html dark=true %}

<!-- {% capture col1 %}
Lorem ipsum dolor sit amet  
consectetur adipiscing elit  
sed do eiusmod tempor
{% endcapture %}

{% capture col2 %}
Lorem ipsum dolor sit amet  
consectetur adipiscing elit  
sed do eiusmod tempor
{% endcapture %}

{% capture col3 %}
Lorem ipsum dolor sit amet  
consectetur adipiscing elit  
sed do eiusmod tempor
{% endcapture %}

{% include cols.html col1=col1 col2=col2 col3=col3 %}
 -->

