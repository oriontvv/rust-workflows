# cookiecutter-rust-workflows

A [cookiecutter](https://cookiecutter.readthedocs.io/) template that scaffolds the
`.github/` for a Rust project wired up to the reusable workflows in
[`oriontvv/rust-workflows`](https://github.com/oriontvv/rust-workflows).

Rather than copy-pasting YAML, the generated project gets thin wrapper workflows that call the
shared ones with `uses:`.

## Usage

```sh
# uv/uvx (no install needed)
uvx cookiecutter path/to/rust-workflows/cookiecutter-rust-workflows
```

Or straight from GitHub:

```sh
uvx cookiecutter gh:oriontvv/rust-workflows --directory cookiecutter-rust-workflows
```

Requires [`uv`](https://docs.astral.sh/uv/) and `git`. Prefer `uv tool install cookiecutter` if you
scaffold often:

```sh
uv tool install cookiecutter
cookiecutter gh:oriontvv/rust-workflows --directory cookiecutter-rust-workflows
```

You are prompted for the options below; every `enable_*` toggle adds or removes a wrapper workflow.
Run it inside an existing repo (it writes into the current directory tree as
`<project_slug>/.github/...`) or in an empty directory to start fresh.

## Options

| Variable | Default | Meaning |
|---|---|---|
| `project_name` | `My Rust Project` | Human-readable name |
| `project_slug` | derived | Repo / directory slug |
| `binary_name` | `project_slug` | Crate and binary name (`Cargo.toml` `name`) |
| `description` | `A Rust project` | Short description (also the Homebrew `desc`) |
| `github_owner` | `oriontvv` | GitHub user/org that owns the generated repo |
| `default_branch` | `master` | Branch CI and coverage run on |
| `rust_workflows_repo` | `oriontvv/rust-workflows` | `owner/repo` of the shared reusable workflows |
| `rust_workflows_ref` | `master` | Ref of that repo to call — pass a tag/SHA to pin |
| `enable_coverage` | `yes` | Add the `coverage` branch publishing workflow |
| `enable_audit` | `yes` | Run the cargo security audit job in CI |
| `enable_nix` | `no` | Build the Nix flake package in CI |
| `enable_wasm` | `no` | Build/test a wasm (web) target in CI |
| `enable_pages` | `no` | Deploy the wasm build to GitHub Pages on tag |
| `enable_crates` | `yes` | Publish to crates.io on tag |
| `enable_docker` | `no` | Build/push a multi-arch Docker image on tag |
| `enable_homebrew` | `no` | Bump the Homebrew tap formula on tag |
| `enable_wix_msi` | `no` | Build a Windows `.msi` on tag |
| `docker_image` | `owner/binary_name` | Docker Hub image (when `enable_docker`) |
| `homebrew_tap_repo` | `owner/homebrew-tap` | Tap repo (when `enable_homebrew`) |
| `homebrew_license` | `Apache-2.0` | Formula license |

## What gets generated

```
<project_slug>/
└── .github/
    ├── dependabot.yml            # cargo + github-actions, weekly
    └── workflows/
        ├── ci.yml                # always
        ├── coverage.yml          # if enable_coverage
        ├── pages.yml             # if enable_pages
        └── release.yml           # always
```

The post-generation hook deletes the optional files that were not requested and prints the
secrets you still need to configure (see the "Environment variables / secrets" table in the
[rust-workflows README](../README.md)).
