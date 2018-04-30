#!/bin/sh

set -eu

main () {
    sanity_check "$@"
    version=$1
    ./test
    patch_changelog
    bump_version
    git_commit_and_tag
    clean
    build
    git_push
    upload
}

sanity_check() {
    if [ "$#" -ne 1 ]; then
        echo >&2 'usage: ./tools/release.sh <version>'
        exit 1
    fi

    grep UNRELEASED CHANGELOG.md \
        || (echo >&2 'No changes noted in CHANGELOG'; exit 1)

    set +e
    git diff-index --quiet --cached HEAD
    local has_staged_changes=$?
    git diff-files --quiet
    local has_unstaged_changes=$?
    set -e
    if [ $has_staged_changes -ne 0 -o $has_unstaged_changes -ne 0 ]; then
        echo >&2 "You have a dirty index, please stash or commit your changes before releasing"
        exit 1
    fi
}

patch_changelog() {
    # Doesn't use sed -i since it's not portable
    sed "s/UNRELEASED/$version - $(date -u +'%Y-%m-%d')/" CHANGELOG.md \
        > tmp-changelog
    mv tmp-changelog CHANGELOG.md
}

bump_version() {
    sed "s/version='.*',/version='$version',/" setup.py \
        > tmp-setup
    mv tmp-setup setup.py
}

git_commit_and_tag() {
    git add CHANGELOG.md setup.py
    git commit -m "Release $version"
    git tag -m "Release $version" "v$version"
}

git_push() {
    git push
    git push --tags
}

clean () {
    rm -rf dist
}

build () {
    ./venv/bin/python setup.py sdist
}

upload () {
    ./venv/bin/twine upload dist/*
}

main "$@"
