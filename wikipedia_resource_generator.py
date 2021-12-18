import os.path

import wikipediaapi
import pycountry

import re
import requests


# This file only needs to be run in order to generate the lexical resources in the /lexical_resources directory

wiki = wikipediaapi.Wikipedia('en')


def getredirectsfor(p):
    # lifted from https://www.mediawiki.org/wiki/API:Redirects
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"

    PARAMS = {
        "action": "query",
        "format": "json",
        "titles": p,
        "prop": "redirects"
    }

    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()

    PAGES = DATA["query"]["pages"]

    out = []
    for k, v in PAGES.items():
        for re in v["redirects"]:
            out.append(re["title"])
    return out


def make_redirects_lexical_resource(filename):
    with open(filename, "wt") as f:
        for c in pycountry.countries:
            print(c)
            if hasattr(c,"official_name"):
                o_name = c.official_name
            else:
                o_name = c.name
            page_py = wiki.page(o_name)
            title = page_py.title
            displaytitle = page_py.displaytitle
            twoletter = c.alpha_2
            print(title, displaytitle)
            aliases = [displaytitle] + getredirectsfor(displaytitle)
            for a in aliases:
                print("\t".join([twoletter, displaytitle, a]))
                f.write("\t".join([twoletter, displaytitle, a]) + "\n")



UNNEEDED_PREFIXES = {
"administrative subdivisions", "air force", "architecture", "arrondissements and communes", "autonomous province",
"biodiversity", "capital", "caribbean islands", "caribbean special municipalities", "chief justice", "cockpit",
"commune", "countries", "departements", "districts and dependencies", "environment", "extreme points",
"federal states", "greek cypriot administration", "imperial principality", "judiciary",
"indigenous cultures, kingdoms and ethnic groups", "integral overseas areas", "islamic govermnet", "island area",
"overseas collectivity", "political history", "proposed state", "quarters", "special municipality", "states",
"subdivision", "tfyr", "the souvereign military order", "trust territory", "climate", "list", "navy", "regions",
"collectivity", "districts", "foreign relations", "government", "parishes", "politics", "provinces", "principality",
"transnational issues", "people", "bibliography", "culture", "languages", "demographics", "economy", "geography",
"etymology", "history", "name", "administrative divisions", "subdivisions", "military"}


def extraneous(s:str, displaytitle=""):
    # some of these are redundant because of dev process and showing working.
    if re.match(".*\Ws$", s):
        return True
    if s.startswith(displaytitle + "/"):
        return True
    if s.startswith("ISO "):
        return True
    if "/" in s:
        return True
    if " in " in s:
        return True
    if " of " in s:
        #some are needed eg "Kingdom of X" whereas some are not eg "Demographics of X".
        before_of = re.sub(" of .*", "", s)
        # we print this then we  $cat x | sort | uniq -c | sort -h | cut -c9-
        if before_of.lower() in UNNEEDED_PREFIXES:
            return True
    for prefix in ["draft:" , "national office"]:
        if s.lower().startswith(prefix):
            return True

    for suffix in ["legends", "cultural practices", "news agency", "facts", "culture", "people", "goods",
                   "(country)", "(state)", "(song)", "(disambiguation)", "(nation)", "(island)"]:
        if s.lower().endswith(suffix):
            return True

    if re.search("\d+", s): # years, mainly
            return True

    if re.search("\(", s): # years, mainly
            return True

    return False


#################################

if not os.path.exists("src/pycountry/lexical_resources/existingcountries_wikipedia_redirects.tab"):
    make_redirects_lexical_resource("src/pycountry/lexical_resources/existingcountries_wikipedia_redirects.tab")

with open("src/pycountry/lexical_resources/existingcountries_wikipedia_redirects.tab", "rt") as f_in:
    with open("src/pycountry/lexical_resources/existingcountries_wikipedia_redirects.cleaned.tab", "wt") as f_out:
        for line in f_in:
            [twoletter, displaytitle, alias] = line.strip().split("\t")
            rv = extraneous(alias, displaytitle)
            if rv:
                print("ignoring '{}'".format(alias))
            else:
                f_out.write(line)

