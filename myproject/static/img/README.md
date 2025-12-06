# static/img — project image assets

Place site images here. Landing template expects the following filenames (you can replace with your own PNGs):

- logo.png                — recommended: 200x60 PNG (transparent background)
- collage.png             — recommended: 1200x800 PNG (used as hero illustration) — path used in template: img/images/collage.png
- trust-badge.png         — recommended: 96x96 PNG
- course-web.png          — recommended: 800x500 PNG
- course-python.png       — recommended: 800x500 PNG
- course-design.png       — recommended: 800x500 PNG

If you keep images in a nested folder, ensure the template path matches (example used: {% raw %}{% static 'img/images/collage.png' %}{% endraw %}).

Tips:
- For development, set DEBUG = True so runserver serves static files.
- Ensure settings.py includes STATICFILES_DIRS = [ BASE_DIR / 'static' ] (or equivalent).
- Test the asset directly in the browser at: /static/img/images/collage.png
- After adding images, for production run `python manage.py collectstatic`.
