"""The release metadata agree with each other and with the code.

Zenodo reads .zenodo.json and ignores CITATION.cff when both are present;
GitHub's "Cite this repository" reads CITATION.cff. The two must name the
same software, version and authors, and the version must be the package's.
The checks on the release date and the DOI apply once CITATION.cff carries
them, which is on release day.
"""
import json
import re
from pathlib import Path

import maplepy

ROOT = Path(__file__).resolve().parents[1]
CFF = (ROOT / 'CITATION.cff').read_text(encoding='utf-8')
ZEN = json.loads((ROOT / '.zenodo.json').read_text(encoding='utf-8'))
NIK = '0000-0002-1061-1230'


def cff(field):
    m = re.search(rf'^{field}:\s*"?(.*?)"?\s*$', CFF, re.M)
    return m.group(1) if m else None


def software_authors():
    block = CFF.split('\nauthors:\n', 1)[1].split('\nversion:', 1)[0]
    return re.findall(r'family-names: (.+)\n\s+given-names: (.+)', block)


def test_zenodo_and_citation_files_agree():
    assert ZEN['version'] == cff('version') == maplepy.__version__
    assert ZEN['title'] == cff('title')
    assert ZEN['upload_type'] == 'software' and ZEN['license'] == 'mit'
    assert cff('license') == 'MIT'
    names = [f'{f}, {g}' for f, g in software_authors()]
    assert names == [c['name'] for c in ZEN['creators']]
    assert ZEN['creators'][0]['orcid'] == NIK
    assert f'orcid: "https://orcid.org/{NIK}"' in CFF


def test_the_engine_versions_are_named_where_the_release_is_described():
    for text in (CFF, ZEN['description']):
        assert maplepy.MAPLEPY_VERSION in text and maplepy.HOPPER_VERSION in text


def test_package_version_matches_pyproject():
    toml = (ROOT / 'pyproject.toml').read_text(encoding='utf-8')
    assert re.search(r'^version = "(.*)"', toml, re.M).group(1) == maplepy.__version__


def test_every_released_version_has_a_changelog_entry():
    log = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    released = cff('date-released')
    for v in (f'maplepy {maplepy.__version__}', maplepy.MAPLEPY_VERSION,
              maplepy.HOPPER_VERSION):
        m = re.search(rf'^### {re.escape(v)} – (.+)$', log, re.M)
        assert m, v
        if released:      # on release day the entries must be dated
            assert m.group(1) != 'unreleased', (v, 'CHANGELOG says unreleased')
    if released:
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', released)


def test_the_readme_gives_the_citation_doi_once_there_is_one():
    doi = cff('doi')
    if doi:
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        assert f'https://doi.org/{doi}' in readme, doi


def test_the_licence_names_the_author_and_the_university():
    text = (ROOT / 'LICENSE').read_text(encoding='utf-8')
    assert 'Copyright (c) 2026 Nik Reeves-McLaren, University of Sheffield' in text
