---
layout: archive
title: "CV"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---

{% include base_path %}

Education
======
* Ph.D in Health Policy and Management, Harvard University, 2028 (expected)
* B.A. in Mathematics and Economics, Wesleyan University, 2018
  * Phi Beta Kappa
  * Gilbert Clee Scholarship for high standards of leadership and a deep commitment to Wesleyan University
  * Robertson Prize for Excellence in Mathematics
  * Rae Shortt Prize for Excellence in Mathematics
  * White Prize for Excellence in Economics
  * Omicron Delta Epsilon, International Economics Honors Society
  * Plukas Teaching Apprentice Award 

Work experience
======
* Fall 2021 - present: External Advisor
  * McKinsey & Co., remote
    
* Fall 2021 - Summer 2023: Research Assistant
  * Harvard Medical School, Boston

* Fall 2018 - Summer 2021: Senior Business Analyst
  * McKinsey & Co., New York

Publications
======
  <ul>{% for post in site.publications reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
  
Talks
======
  <ul>{% for post in site.talks reversed %}
    {% include archive-single-talk-cv.html  %}
  {% endfor %}</ul>
  
Teaching
======
  <ul>{% for post in site.teaching reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
