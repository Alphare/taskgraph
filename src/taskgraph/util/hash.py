# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import hashlib
from pathlib import Path

from taskgraph.util import path as mozpath
from taskgraph.util.memoize import memoize


@memoize
def hash_path(path):
    """Hash a single file.

    Returns the SHA-256 hash in hex form.
    """
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def hash_paths(base_path, patterns):
    """
    Give a list of path patterns, return a digest of the contents of all
    the corresponding files, similarly to git tree objects or mercurial
    manifests.

    Each file is hashed. The list of all hashes and file paths is then
    itself hashed to produce the result.
    """
    h = hashlib.sha256()

    found = set()
    for pattern in patterns:
        matches = _find_matching_files(base_path, pattern)
        if matches:
            found.update(matches)
        else:
            raise Exception("%s did not match anything" % pattern)
    for path in sorted(found):
        h.update(
            "{} {}\n".format(
                hash_path(mozpath.abspath(mozpath.join(base_path, path))),
                mozpath.normsep(path),
            ).encode("utf-8")
        )
    return h.hexdigest()


@memoize
def _find_matching_files(base_path, pattern):
    files = _get_all_files(base_path)
    return [path for path in files if mozpath.match(path, pattern)]


@memoize
def _get_all_files(base_path):
    return [
        mozpath.normsep(str(path))
        for path in Path(base_path).rglob("*")
        if path.is_file()
    ]
