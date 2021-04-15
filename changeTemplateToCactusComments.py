import argparse
import contextlib
import difflib
import os.path
import shutil
import sys
from typing import Dict, List, Optional

dataDir = os.path.join(os.path.dirname(__file__), "data")


def cactusifyTemplate(templateLines: List[str], name: Optional[str] = None) -> List[str]:
    try:
        inc_l = next(i for i, ln in enumerate(templateLines) if "comments_helper.tmpl" in ln)
    except StopIteration:
        raise RuntimeError(f"Could not find a line that includes the 'comments_helper.tmpl' template in {name}")
    modLines = list(templateLines)
    if modLines[inc_l].lstrip().startswith("<%namespace"):
        engine = "mako"
    elif modLines[inc_l].lstrip().startswith("{% import"):
        engine = "jinja"
    else:
        raise RuntimeError("Could not deduce whether this is a mako or a jinja template")
    modLines[inc_l] = templateLines[inc_l].replace("comments_helper.tmpl", "comments_helper_cactus.tmpl")
    try:
        if engine == "mako":
            hdr_start_l = next(
                i for i, ln in enumerate(templateLines) if ln.lstrip().startswith("<%block") and "extra_head" in ln
            )
            hdr_len_ld = next(i for i, ln in enumerate(templateLines[hdr_start_l:]) if ln.strip() == "</%block>")
            modLines.insert(hdr_start_l + hdr_len_ld, "${comments.comment_extra_head()}\n")
        elif engine == "jinja":
            hdr_start_l = next(
                i for i, ln in enumerate(templateLines) if ln.lstrip().startswith("{% block") and "extra_head" in ln
            )
            hdr_len_ld = next(i for i, ln in enumerate(templateLines[hdr_start_l:]) if ln.strip() == "{% endblock %}")
            modLines.insert(hdr_start_l + hdr_len_ld, "{{ comments.comment_extra_head() }}\n")
    except StopIteration:
        raise RuntimeError(f"Could not find the 'extra_head' block in {name}")
    return engine, modLines


def changeTemplatesToCactusComments(templates: List[str], output: str, in_place: bool) -> None:
    patch: List[str] = []
    needHelper: Dict[str, str] = {}
    for template in templates:
        origLines = [ln for ln in open(template)]
        engine, modLines = cactusifyTemplate(origLines, name=template)
        if in_place:
            with open(template, "w") as f:
                print(*modLines, file=f, sep="", end="")
        else:
            patch += difflib.unified_diff(origLines, modLines, fromfile=template, tofile=template)
        dirName = os.path.dirname(template)
        if dirName not in needHelper:
            needHelper[dirName] = engine
        else:
            if engine != needHelper[dirName]:
                raise RuntimeError(
                    f"There are mako and jinja templates in '{dirname}', " "this would lead to name clashes"
                )
    if not in_place:
        helpers: Dict[str, List[str]] = {}
        for dirName, engine in needHelper.items():
            if engine not in helpers:
                helpers[engine] = [ln for ln in open(os.path.join(dataDir, f"comments_helper_cactus_{engine}.tmpl"))]
            patch += difflib.unified_diff(
                [], helpers[engine], tofile=os.path.join(dirName, "comments_helper_cactus.tmpl")
            )
        with open(output, "w") if output != "-" else contextlib.nullcontext(sys.stdout) as f:
            print(*patch, file=f, sep="", end="")
    else:
        for dirName, engine in needHelper.items():
            shutil.copyfile(
                os.path.join(dataDir, f"comments_helper_cactus_{engine}.tmpl"),
                os.path.join(dirName, "comments_helper_cactus.tmpl"),
            )


def main(args: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Try to modify the templates of a Nikola theme to use Cactus Comments https://cactus.chat/"
    )
    parser.add_argument("template", nargs="+", help="Template file to change")
    parser.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help=(
            "Edit the files in place. "
            "WARNING: this will overwrite your template files, please make sure to commit or back them up before."
        ),
    )
    parser.add_argument(
        "-o", "--output", default="-", help=("Patch output file " "(if not specified the diff is written to stdout)")
    )
    args = parser.parse_args()

    changeTemplatesToCactusComments(args.template, args.output, in_place=args.in_place)


if __name__ == "__main__":
    main()
