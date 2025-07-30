---
layout: page
title: Denials Analysis
permalink: /denials_analysis/
---

<div class="container">
  <p>This page hosts an interactive analysis of Medicare Advantage denial rates. The dashboard is hosted on a separate service and embedded here.</p>
  
  <div class="iframe-container">
    <iframe
      src="YOUR_DASH_APP_URL_HERE"
      frameborder="0"
      allowfullscreen
      style="width: 100%; height: 800px; border: 1px solid #ccc;">
    </iframe>
  </div>

  <p class="mt-3">
    <a href="https://github.com/ggweinreb/website/blob/master/apps/code/denials_line_graph.py" target="_blank">
      Click here to view the source code for this analysis on GitHub.
    </a>
  </p>
</div>

<style>
  .iframe-container {
    position: relative;
    overflow: hidden;
    width: 100%;
    padding-top: 60%; /* Aspect ratio */
  }
  .iframe-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
</style>
