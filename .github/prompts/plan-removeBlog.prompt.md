## Plan: Remove Blog From Site

Remove all blog content and any UI/routes that expose posts (archives, categories/tags, RSS). Delete the sample posts and remove/archive pages that list posts. Also disable post processing and feeds in configuration so future “posts” can’t accidentally reappear. This keeps your non-blog sections (research, publications, talks, teaching, pages) intact.

### Steps 4
1. Remove all Markdown files under `_posts/` and delete the folder entirely so no posts can be built.
2. Remove/disable post archive pages under `_pages/` that exist only to list blog posts (typically year/category/tag/page archives).
3. Update navigation in `_data/navigation.yml` to remove any “Blog/Posts/Archive” links so no blog section appears in the menu.
4. Disable feeds and post-specific defaults in `_config.yml` (e.g., hide RSS/Atom feed, remove post defaults , and set `future: false` to avoid scheduled-post behavior).