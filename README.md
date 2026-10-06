# rust-workflows

Common, reusable GitHub Actions workflows for Rust projects: CI (check/test/fmt/clippy/wasm/nix/audit),
coverage publishing, GitHub Pages (wasm) deploy and a full release pipeline (GitHub Release +
crates.io + Docker + Homebrew tap). Extracted from [convfmt](https://github.com/oriontvv/convfmt).

Each file in [`.github/workflows/`](.github/workflows) is a [reusable workflow](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
(`on: workflow_call`). A consuming repo doesn't copy the YAML — it calls it with `uses:` and a few
inputs/secrets.

## How to inherit

In your project's repo, create thin wrapper workflows under `.github/workflows` that call the ones
here. Pin to a tag/SHA for stability, or `@master` to always get the latest version.

### Scaffolding with cookiecutter

Instead of writing the wrappers by hand, use the bundled
[`cookiecutter-rust-workflows`](./cookiecutter-rust-workflows) template — it generates the wrapper
workflows and `dependabot.yml` from a short questionnaire:

```sh
# uv/uvx (no install needed)
uvx cookiecutter gh:oriontvv/rust-workflows --directory cookiecutter-rust-workflows
```

Requires [`uv`](https://docs.astral.sh/uv/) and `git`. Prefer `uv tool install cookiecutter` if you
scaffold often and don't want to re-resolve the environment each run.

See [its README](./cookiecutter-rust-workflows/README.md) for the full option list.

### `.github/workflows/ci.yml`

```yaml
name: CI
on: [push, pull_request]

jobs:
  ci:
    uses: oriontvv/rust-workflows/.github/workflows/ci.yml@master
    with:
      enable-wasm: false   # set true if the project has a web/wasm target
      enable-nix: false    # set true if the project ships a flake.nix package
      enable-audit: true
```

### `.github/workflows/coverage.yml`

```yaml
name: Coverage
on:
  push:
    branches: [master]   # only your default branch

jobs:
  coverage:
    uses: oriontvv/rust-workflows/.github/workflows/coverage.yml@master
    permissions:
      contents: write     # required: the job force-pushes the coverage branch
    with:
      coverage-branch: coverage
      # override if you already have your own target, e.g. `make coverage`
      # coverage-command: make coverage
```

### `.github/workflows/pages.yml` (optional, wasm projects only)

```yaml
name: Pages
on:
  push:
    tags: ['*.*.*']
  workflow_dispatch:

jobs:
  pages:
    uses: oriontvv/rust-workflows/.github/workflows/pages.yml@master
    permissions:
      contents: read
      pages: write
      id-token: write
```

Requires enabling **Settings → Pages → Source: GitHub Actions** once in the consuming repo.

### `.github/workflows/release.yml`

```yaml
name: Release
on:
  push:
    tags: ['*.*.*']

jobs:
  release:
    uses: oriontvv/rust-workflows/.github/workflows/release.yml@master
    with:
      binary-name: convfmt
      enable-crates: true
      enable-docker: true
      enable-homebrew: true
      docker-image: oriontvv/convfmt
      homebrew-tap-repo: oriontvv/homebrew-tap
      homebrew-description: "CLI tool which can convert different formats"
      homebrew-homepage: "https://github.com/oriontvv/convfmt"
    secrets:
      CARGO_TOKEN: ${{ secrets.CARGO_TOKEN }}
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
      HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}
```

## Inputs reference

### `ci.yml`

| Input | Type | Default | Description |
|---|---|---|---|
| `rust-check-versions` | string (JSON array) | `["stable","beta","nightly"]` | Toolchains for the `check` matrix job |
| `enable-wasm` | boolean | `false` | Run the `wasm` job (build/test a web target) |
| `enable-nix` | boolean | `false` | Run the `nix` job (`nix build` of your flake) |
| `enable-audit` | boolean | `true` | Run `cargo audit` via `actions-rs/audit-check` |
| `wasm-tools-command` | string | `make web-tools` | Installs wasm target + matching `wasm-bindgen-cli` |
| `wasm-test-command` | string | `make web-test` | Runs tests of the wasm wrapper crate |
| `wasm-build-command` | string | `make web-build` | Builds the wasm bundle |
| `nix-build-command` | string | `nix build --print-build-logs` | Builds the flake package |

Jobs always run: `check` (matrix), `test`, `fmt`, `clippy`.

### `coverage.yml`

| Input | Type | Default | Description |
|---|---|---|---|
| `coverage-branch` | string | `coverage` | Branch the HTML report is force-pushed to |
| `coverage-command` | string | `grcov`-based shell pipeline (see below) | Shell command producing `./htmlcov` |

Needs `permissions: contents: write` on the calling job to push the coverage branch.

### `pages.yml`

| Input | Type | Default | Description |
|---|---|---|---|
| `wasm-tools-command` | string | `make web-tools` | Installs wasm target + tooling |
| `wasm-build-command` | string | `make web-build` | Builds the wasm bundle |
| `pages-artifact-path` | string | `web/static` | Directory uploaded as the Pages artifact |

### `release.yml`

| Input | Type | Default | Description |
|---|---|---|---|
| `binary-name` | string | **required** | Crate/binary name, used in archive and tap formula names |
| `enable-binaries` | boolean | `true` | Build the binary archives and create the GitHub Release from them. Set `false` for a crate without a binary, e.g. a dprint plugin |
| `enable-dprint-plugin` | boolean | `false` | Build a dprint Wasm plugin and attach `plugin.wasm` + `schema.json` to the GitHub Release |
| `dprint-plugin-features` | string | `wasm` | Cargo features that build the crate as a Wasm plugin (passed to `wasm.yml`) |
| `dprint-schema-path` | string | `deployment/schema.json` | Config schema; the `0.0.0` in its `$id` is replaced by the tag |
| `enable-crates` | boolean | `true` | Run `cargo publish` |
| `enable-docker` | boolean | `false` | Build & push a multi-arch Docker image |
| `enable-homebrew` | boolean | `false` | Bump the formula in a Homebrew tap repo |
| `enable-wix-msi` | boolean | `false` | Build a Windows `.msi` via `cargo-wix` (needs a `wix/` dir) |
| `docker-image` | string | `''` | e.g. `oriontvv/convfmt`; required if `enable-docker` |
| `homebrew-tap-repo` | string | `oriontvv/homebrew-tap` | `owner/repo` of the tap |
| `homebrew-formula-class` | string | `''` | Ruby class name; defaults to `Capitalize(binary-name)` |
| `homebrew-description` | string | `''` | Formula `desc` |
| `homebrew-homepage` | string | `''` | Formula `homepage` |
| `homebrew-license` | string | `Apache-2.0` | Formula `license` |

With `enable-binaries` (the default) it builds GitHub Release assets for `ubuntu-latest` (musl),
`macos-latest` and `windows-latest`, then creates a GitHub Release via `softprops/action-gh-release`,
pulling release notes from `CHANGELOG.md` via `ffurrer2/extract-release-notes`.


### `wasm.yml`

Builds a crate as a WebAssembly module and uploads it as an artifact. It knows nothing about dprint or
releases, so it is usable on its own, e.g. to check in CI that a crate still compiles for Wasm, or as the
first step of a custom release:

```yaml
jobs:
  wasm:
    uses: oriontvv/rust-workflows/.github/workflows/wasm.yml@master
    with:
      features: wasm
  publish:
    needs: wasm
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: ${{ needs.wasm.outputs.artifact-name }}
      - run: ls -l ${{ needs.wasm.outputs.wasm-file }}
```

The module is the `cdylib` target of the package, so `[lib]` needs `crate-type = ["cdylib"]`.

| Input | Type | Default | Description |
|---|---|---|---|
| `features` | string | `''` | Cargo features, comma separated |
| `target` | string | `wasm32-unknown-unknown` | Rust target, e.g. `wasm32-wasip1` |
| `package` | string | `''` | Package to build (`-p`); empty for the crate in the repository root |
| `run-tests` | boolean | `false` | Run `cargo test` and `cargo clippy -D warnings` first |
| `artifact-name` | string | `wasm` | Name of the uploaded artifact |
| `artifact-retention-days` | number | `7` | How long the artifact is kept |

| Output | Description |
|---|---|
| `crate-name` | Name of the built package |
| `version` | Version of the built package |
| `wasm-file` | File name of the module inside the artifact |
| `artifact-name` | Name of the artifact that holds the module |

## Environment variables / secrets

| Name | Used by | Required when | Purpose |
|---|---|---|---|
| `GITHUB_TOKEN` | `ci.yml` (`sec`), `release.yml` (`release-github`) | always (auto-provided) | Security audit + creating the GitHub Release |
| `CARGO_TOKEN` | `release.yml` (`release-crates`) | `enable-crates: true` | `cargo publish` auth token from crates.io |
| `DOCKERHUB_USERNAME` | `release.yml` (`release-docker`) | `enable-docker: true` | Docker Hub login |
| `DOCKERHUB_TOKEN` | `release.yml` (`release-docker`) | `enable-docker: true` | Docker Hub access token |
| `HOMEBREW_TAP_TOKEN` | `release.yml` (`bump-homebrew`) | `enable-homebrew: true` | PAT (repo scope) with push access to the tap repo |

`CARGO_TERM_COLOR=always` is set internally in `ci.yml`/`coverage.yml`; no action needed.


## Publishing to the `oriontvv/homebrew-tap` Homebrew tap

The `bump-homebrew` job in `release.yml` runs after `release-github` succeeds, and only for
non-prerelease tags (tags without a `-`, e.g. `2.4.0` but not `2.4.0-rc1`). Steps it performs:

1. Determine the version from the pushed tag (`refs/tags/<version>`).
2. Download `<binary-name>-mac.tar.gz` and `<binary-name>-linux-musl.tar.gz` from the just-created
   GitHub Release and compute their SHA256 sums.
3. Render a Homebrew formula (`<binary-name>.rb`) with `on_macos`/`on_linux` blocks pointing at those
   two archives, using `homebrew-description`, `homebrew-homepage` and `homebrew-license` inputs.
4. Checkout `homebrew-tap-repo` (default `oriontvv/homebrew-tap`) using `HOMEBREW_TAP_TOKEN`.
5. Copy the formula into `Formula/<binary-name>.rb`, commit and push straight to the tap's default
   branch.

What you need to set up beforehand for this to work:

- A GitHub repo `oriontvv/homebrew-tap` (or your own tap) with a `Formula/` directory.
- A Personal Access Token with push access to that repo, stored as the `HOMEBREW_TAP_TOKEN` secret
  in the *project* repo (not the tap).
- Your release job must actually produce `<binary-name>-mac.tar.gz` and
  `<binary-name>-linux-musl.tar.gz` assets — this is already the case in `release.yml`'s
  `release-github` job, as long as `binary-name` matches your crate/binary name.
- `enable-homebrew: true` and the `homebrew-*` inputs set on the call site.

Once installed, users consume it with:

```sh
brew tap oriontvv/tap
brew install <binary-name>
```
