---
layout: archive
title: "Medicare Advantage Claim Denials"
permalink: /claim-denials/
author_profile: true
---

## Interactive Analysis Dashboard

This dashboard provides an interactive analysis of Medicare Advantage claim denial rates, appeal rates, and healthcare spending patterns across different BETOS (Berenson-Eggers Type of Service) categories.

<div class="iframe-container">
  <iframe
    src="https://denials-line-graph-da765f909e9d.herokuapp.com/"
    frameborder="0"
    allowfullscreen
    allow="fullscreen"
    style="width: 100%; height: 800px; border: 1px solid #ccc;"
    title="Medicare Advantage Denial Rates Dashboard">
  </iframe>
</div>

<style>
  .iframe-container {
    position: relative;
    overflow: hidden;
    width: 100%;
    margin: 20px 0;
  }
  .iframe-container iframe {
    width: 100%;
    height: 800px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  @media (max-width: 768px) {
    .iframe-container iframe {
      height: 600px;
    }
  }
  
  /* Ensure fullscreen works properly */
  .iframe-container:fullscreen iframe {
    width: 100vw;
    height: 100vh;
    border: none;
    border-radius: 0;
  }
</style>

### About the Data

The dashboard analyzes Medicare Advantage claim denial patterns using aggregated claims data. You can explore:

- **Final Denial Rates**: Claims that were denied and not eventually paid
- **Initial Denial Rates**: All initially denied claims (including those later paid on appeal)
- **Appeal Rates**: Proportion of claims that were appealed
- **Appeal Approval Rates**: Success rate of appeals
- **Healthcare Spending**: Total and per-member spending patterns

Use the dropdown menus to filter by BETOS categories and subcategories to explore denial patterns across different types of healthcare services.
