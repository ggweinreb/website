# Website Repository Cleanup - Technical Instructions

## Overview
This Jekyll-based academic website (Academic Pages theme) contains significant boilerplate that needs to be removed. This document provides exact file paths and modifications required.

**Repository root:** `C:\Users\gabew\OneDrive - Harvard University\website`

---

## Phase 1: Delete Unused Files

### 1.1 Delete Sample/Demo Images
Delete the following files from `images/`:
```
images/500x300.png
images/3953273590_704e3899d5_m.jpg
images/foo-bar-identity.jpg
images/foo-bar-identity-th.jpg
images/editing-talk.png
images/image-alignment-1200x4002.jpg
images/image-alignment-150x150.jpg
images/image-alignment-300x200.jpg
images/image-alignment-580x300.jpg
images/paragraph-indent.png
images/paragraph-no-indent.png
images/site-logo.png
```

**Command:**
```bash
cd "C:\Users\gabew\OneDrive - Harvard University\website"
rm images/500x300.png images/3953273590_704e3899d5_m.jpg images/foo-bar-identity.jpg images/foo-bar-identity-th.jpg images/editing-talk.png images/image-alignment-*.jpg images/paragraph-indent.png images/paragraph-no-indent.png images/site-logo.png
```

### 1.2 Delete Demo Pages
Delete the following from `_pages/`:
```
_pages/archive-layout-with-content.md
_pages/markdown.md
_pages/non-menu-page.md
```

**Command:**
```bash
rm _pages/archive-layout-with-content.md _pages/markdown.md _pages/non-menu-page.md
```

### 1.3 Delete Sample Content Files
```
_portfolio/portfolio-2.html
_drafts/post-draft.md
_data/authors.yml
files/bibtex1.bib
```

**Command:**
```bash
rm _portfolio/portfolio-2.html _drafts/post-draft.md _data/authors.yml files/bibtex1.bib
```

### 1.4 Delete markdown_generator Directory
Delete entire directory:
```
markdown_generator/
```

**Contents being deleted:**
- `publications.ipynb`
- `publications.py`
- `publications.tsv`
- `talks.ipynb`
- `talks.py`
- `talks.tsv`
- `PubsFromBib.ipynb`
- `pubsFromBib.py`
- `OrcidToBib.ipynb`
- `readme.md`

**Command:**
```bash
rm -rf markdown_generator/
```

### 1.5 Delete Talkmap Files
Delete from repository root:
```
talkmap.ipynb
talkmap.py
talkmap_out.ipynb
```

Delete entire directory:
```
talkmap/
```

Delete GitHub workflow:
```
.github/workflows/scrape_talks.yml
```

**Command:**
```bash
rm talkmap.ipynb talkmap.py talkmap_out.ipynb
rm -rf talkmap/
rm .github/workflows/scrape_talks.yml
```

### 1.6 Delete scripts Directory
Delete entire directory:
```
scripts/
```

**Contents:**
- `cv_markdown_to_json.py`
- `update_cv_json.sh`

**Command:**
```bash
rm -rf scripts/
```

### 1.7 Delete CONTRIBUTING.md
```bash
rm CONTRIBUTING.md
```

### 1.8 Delete CV Page and Supporting Files
Delete the following files:
```
_pages/cv.md
CV.pdf
_data/cv.json
_layouts/cv-layout.html
_includes/cv_template.html
assets/css/cv-styles.css
```

**Command:**
```bash
rm _pages/cv.md CV.pdf _data/cv.json _layouts/cv-layout.html _includes/cv_template.html assets/css/cv-styles.css
```

---

## Phase 2: Update Configuration Files

### 2.1 Remove CV from Navigation
**File:** `_data/navigation.yml`

Remove the CV navigation entry. The file should have entries for Research, Publications, Talks, and Teaching only.

Look for and remove any entry like:
```yaml
  - title: "CV"
    url: /cv/
```

### 2.2 Clean Up _config.yml
**File:** `_config.yml`

Remove or comment out the following unused sections:

#### Comments Section (approx lines 90-150)
Remove the entire comments configuration block including:
- `comments:` section with `provider`, `disqus`, `discourse`, `facebook`, `staticman`, `utterances`, `giscus` subsections

#### Analytics Section
Remove:
- `analytics:` section with `provider` and `google` subsections

#### Unused Author Social Profiles
In the `author:` section, remove empty/unused fields. Keep only:
- `name`
- `avatar`
- `bio`
- `location`
- `employer`
- `googlescholar`
- `linkedin`
- `orcid`

Remove all empty fields like:
- `uri`, `email`, `bitbucket`, `codepen`, `dribbble`, `flickr`, `facebook`, `foursquare`, `github`, `gitlab`, `google_plus`, `keybase`, `instagram`, `impactstory`, `lastfm`, `pinterest`, `soundcloud`, `stackoverflow`, `steam`, `telegram`, `tumblr`, `twitter`, `vine`, `weibo`, `xing`, `youtube`, `wikipedia`, `mastodon`

#### Unused Features
Remove if present:
- `teaser:` configuration
- `breadcrumbs:` if set to false
- Any blog/posts pagination settings

---

## Phase 3: Verify Changes

### 3.1 Test Local Build
Run Jekyll locally to verify the site still builds:
```bash
bundle exec jekyll serve
```
or
```bash
docker-compose up
```

### 3.2 Verify No Broken Links
Check that:
1. Navigation menu no longer shows CV
2. All remaining pages load correctly
3. No 404 errors on existing content

### 3.3 Check Images
Verify that the remaining images in `images/` are still used:
- Profile photo (referenced in `_config.yml`)
- Favicons
- Any images referenced in publications/talks

---

## Files to Preserve
Do NOT delete:
- `Gemfile` and `Gemfile.lock` (needed for Jekyll)
- `Dockerfile` and `docker-compose.yaml` (for local development)
- `package.json` (for JS bundling)
- `_layouts/`, `_includes/`, `_sass/` (core Jekyll templates)
- `assets/` (CSS, JS, fonts - except cv-styles.css noted above)
- `_pages/` (remaining pages: about.md, publications.md, research.md, talks.md, teaching.md, sitemap.md, 404.md, terms.md)
- `_publications/`, `_talks/`, `_teaching/` (content)
- `files/` (PDFs except bibtex1.bib)
- `images/` (remaining profile photos and favicons)

---

## Summary
**Total files to delete:** ~51 files
**Directories to delete:** 3 (markdown_generator/, talkmap/, scripts/)
**Config files to modify:** 2 (_config.yml, _data/navigation.yml)
