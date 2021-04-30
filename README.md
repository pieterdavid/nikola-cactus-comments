# Add [Cactus Comments](https://cactus.chat) to [Nikola](https://getnikola.com) templates

**UPDATE** it is now ([getnikola/nikola#3546](https://github.com/getnikola/nikola/pull/3546),
in current master and releases after v8.1.3) possible to add a comment system to Nikola
through a plugin. [Cactus Comments](https://cactus.chat) is the first comment system
to take advantage of this, see the [plugin page](https://plugins.getnikola.com/v8/cactuscomments/)
for usage instructions.

The script below is not recommended anymore, but left in case it is useful for anyone
trying to do something similar.

---

~~The [Nikola](https://getnikola.com) static site generator is
[not accepting new comments systems](https://github.com/getnikola/nikola/pull/3543#issuecomment-819746263),
but~~ it is relatively straightforward to adapt most Mako and Jinja2 templates written for it
to use [Cactus Comments](https://cactus.chat).

This scripts automates that process: it adds a helper template
for [Cactus Comments](https://cactus.chat) and inserts the loading of
the additional script and stylesheet in the appropriate place.
The main downside of this approach is that currently it removes the option
to change comment systems from the configuration, but with the theme included
in the site repository and the patch corresponding to a git commit,
that may still be an acceptable solution in practice (at least it is for me).

**Usage**:

```bash
git clone https://github.com/pieterdavid/nikola-cactus-comments.git
python nikola-cactus-comments/changeTemplateToCactusComments.py \
    my_site/themes/theme_name/templates/post.tmpl \
    my_site/themes/theme_name/templates/index.tmpl
```

Without additional flags a patch will be written to stdout.
The ``-o`` and ``-i`` options can be used to write to a file instead,
or to modify the files in place, respectively.

## Configuration

The settings for [Cactus Comments](https://cactus.chat) can be passed as follows
(see the [quickstart guide](https://cactus.chat/docs/getting-started/quick-start/)
and [configuration reference](https://cactus.chat/docs/reference/web-client/#configuration)
for more details):

```python
COMMENT_SYSTEM = "cactus"
COMMENT_SYSTEM_ID = "<YOUR-SITE_NAME>"
GLOBAL_CONTEXT = {
    ...
    "cactus_config": {
        "defaultHomeserverUrl": "https://matrix.cactus.chat:8448",
        "serverName": "cactus.chat"
        }
    }
```
