import re
import os
import pypandoc
from collections import OrderedDict
import requests
import shutil
import uuid
from datetime import datetime


def beautify_name(name):
    name = name.split("_")[1]
    slug = "-".join(name.split("-")[:-1])
    name = " ".join(slug.split("-"))
    return name, slug


def build_frontmatter(name):
    if name.startswith("draft"):
        now = datetime.utcnow()
        date = now.strftime("%Y-%m-%d")
        draft = "true"
    else:
        draft = "false"
        date = name.split("_")[0]
    title, slug = beautify_name(name)
    return (
        f"+++\n"
        f'date = "{date}"\n'
        f'title = "{title}"\n'
        f'slug = "{slug}"\n'
        f"draft = {draft}\n" 
        f"+++"
    )


def download_image(url, dir):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        loc = f"{uuid.uuid4()}.jpeg"
        with open(f"{dir}/{loc}", "wb") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        return loc


regexes = OrderedDict(
    {
        "get_imgs": re.compile(r"(<img\nsrc=\"(.*?)\"(.|\n)*?/>)\n((.|\n)*?)(</figure>|</figcaption>)", re.MULTILINE),
        "replace_header": re.compile("(^#.*)({.*name?})", re.MULTILINE),
        "remove_colons": re.compile("(:::.*\W?)", re.MULTILINE),
        "remove_markup": re.compile("({\.markup[\w\W]*?})", re.MULTILINE),
        "remove_figure": re.compile("(<figure.*>?|</figure>?)"),
        "remove_div": re.compile("(<div>|</div>)", re.MULTILINE),
        "remove_header_style": re.compile('^#\W+.*({#?.*"}$)', re.MULTILINE),
    }
)

for root, dirs, filenames in os.walk("posts"):
    for filename in filenames:
        fpath = os.path.join(root, filename)
        output = pypandoc.convert_file(fpath, "md")
        _, slug = beautify_name(filename)
        try:
            os.mkdir(slug)
        except FileExistsError:
            pass
        new_output = output
        for name, regex in regexes.items():
            for match in regex.finditer(new_output):
                if name == "get_imgs":
                    img_tag, url, _, caption, __, type = match.groups()
                    loc = download_image(url, slug)
                    caption = caption.replace("<figcaption>", "") if caption else loc
                    new_output = new_output.replace(img_tag, f"![{caption}]({loc})")
                elif name == "replace_header":
                    name, garbage = match.groups()
                    new_output = new_output.replace(garbage, "")
                else:
                    if not match:
                        continue
                    if len(match.groups()) == 0:
                        continue
                    new_output = new_output.replace(match.groups()[0], "")

        with open(f"{slug}/index.md", "w") as f:
            frontmatter = build_frontmatter(filename)
            new_output = frontmatter + new_output
            f.write(new_output), fpath
