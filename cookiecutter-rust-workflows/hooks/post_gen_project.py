#!/usr/bin/env python3
"""Post-generation hook for the rust-workflows cookiecutter template.

Removes optional files that were rendered but not requested, so a project that
does not need (say) the Pages or coverage workflow does not end up with a
stray wrapper calling a feature it never enabled. Also prints the manual
follow-up steps (secrets to configure, Pages setup) for the options that
were turned on.
"""

import os

ENABLE_PAGES = "{{ cookiecutter.enable_pages }}" == "yes"
ENABLE_COVERAGE = "{{ cookiecutter.enable_coverage }}" == "yes"
ENABLE_CRATES = "{{ cookiecutter.enable_crates }}" == "yes"
ENABLE_DOCKER = "{{ cookiecutter.enable_docker }}" == "yes"
ENABLE_HOMEBREW = "{{ cookiecutter.enable_homebrew }}" == "yes"
HOMEBREW_TAP_REPO = "{{ cookiecutter.homebrew_tap_repo }}"

OPTIONAL_FILES = [
    (ENABLE_PAGES, ".github/workflows/pages.yml"),
    (ENABLE_COVERAGE, ".github/workflows/coverage.yml"),
]


def main() -> None:
    for enabled, rel in OPTIONAL_FILES:
        if enabled:
            continue
        path = os.path.join(os.getcwd(), rel)
        if os.path.exists(path):
            os.remove(path)

    print("\nProject initialised.")
    print("Next steps:")
    print("  1. Review and commit the generated .github/workflows/*.")
    print("  2. Configure the repository secrets the release job needs:")
    if ENABLE_CRATES:
        print("       CARGO_TOKEN          - crates.io API token")
    if ENABLE_DOCKER:
        print("       DOCKERHUB_USERNAME   - Docker Hub username")
        print("       DOCKERHUB_TOKEN      - Docker Hub access token")
    if ENABLE_HOMEBREW:
        print(f"       HOMEBREW_TAP_TOKEN   - PAT with push access to {HOMEBREW_TAP_REPO}")
    if ENABLE_PAGES:
        print("  3. Enable Pages: Settings -> Pages -> Source: GitHub Actions.")
    print("  Release with: git tag 1.0.0 && git push --tags\n")


if __name__ == "__main__":
    main()
