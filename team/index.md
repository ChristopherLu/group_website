---
title: Team
nav:
  order: 3
  tooltip: About our team
---

# {% include icon.html icon="fa-solid fa-users" %}Meet Our Team

__Rome wasn’t built in a day — RoMA builds the future of robotics step by step.__

At RoMA, we are a dedicated team of passionate researchers to advance the frontier of foundation models for next-gen robotics. 

{% include section.html %}

{% include list.html data="members" component="portrait" filter="role == 'principal-investigator'" %}

{% include list.html data="members" component="portrait" filter="role != 'principal-investigator' and alumni != true" sort="order" %}

{% include section.html background="images/ucl_robotics.jpg" dark=true %}

Do you want to hear more?

{% include section.html %}

Please [reach out]({{ site.baseurl }}/recruitment) if you are interested in joining. We are happy to support Early Career/postdoc fellowships. 

{% capture content %}

{% endcapture %}

{% include grid.html style="square" content=content %}