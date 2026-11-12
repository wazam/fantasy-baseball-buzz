# Releasing

How a new version of Buzz goes from `main` to published Docker images and a GitHub Release. Replace `X.Y.Z` with the new version throughout.

## 1. Choose the version

No file holds the app version. The git tag `vX.Y.Z` is the version: the Docker Publish workflow reads it to tag the images and to set the image's `org.opencontainers.image.version` label.

Follow [semver](https://semver.org/). While Buzz is on `0.x`, bump the minor version (`0.Y.0`) for any change that requires existing users to edit their `compose.yaml`, `.env`, or `data` folder, and the patch version (`0.Y.Z`) for everything else.

### If the release changes the Python version

Python's version appears in five files. They must agree on the minor version, `3.N`; only `.tool-versions` also pins the patch:

| File | Setting | Pins |
|------|---------|------|
| [`.tool-versions`](.tool-versions) | `python 3.N.P` | Full patch, the version asdf installs for local linting |
| [`Dockerfile`](Dockerfile) | `ARG DOCKER_PYTHON_V=3.N-alpine` | Minor only, so each image build picks up the latest `3.N` patch |
| [`Pipfile`](Pipfile) | `python_version = "3.N"` | Minor only, so pipenv accepts any `3.N.x` patch, locally and in the image |
| [`Pipfile.lock`](Pipfile.lock) | `_meta.requires.python_version` and `_meta.hash` | Rewritten by pipenv; never edit by hand |
| [`.github/workflows/lint.yml`](.github/workflows/lint.yml) | `python-version: ["3.N"]` | Minor only, matching the Pipfile |

After editing the other four files, regenerate the lock file so its Python version and hash match the new Pipfile:

```bash
pipenv lock --clear
```

Plain `pipenv update` can keep old versions, so use `pipenv lock --clear` for dependency updates too.

## 2. Write the release notes in CHANGELOG.md

Notes collect under `## Unreleased` at the top of [CHANGELOG.md](CHANGELOG.md) as changes land on `main`. Rename that heading to the new version, and go over its notes against the rules below. If there's no Unreleased section, add the version's section at the top, under the intro paragraph:

```markdown
## [vX.Y.Z](https://github.com/wazam/fantasy-baseball-buzz/releases/tag/vX.Y.Z) (YYYY-MM-DD)

### Upgrading

- ...

### What's New

- ...

### Bug Fixes

- ...
```

- Use the date the release goes live, in local time (America/New_York).
- Leave out any section with nothing in it.
- The heading link stays broken until the GitHub Release exists in step 7.
- After the release, start a new empty `## Unreleased` section only when the next change lands, so the top of the file never shows an empty heading.

Writing rules:

- Write the notes fresh for people running Buzz. Never copy commit messages. Group changes by what users will notice, put the most significant first, and use plain language instead of commit-speak.
- Call out anything users must do when upgrading (a renamed setting, a removed service, a new folder) under `### Upgrading`, which always comes first. Say what to do, not just what changed, and name both the old and new values.
- This section is the only source of the notes. The GitHub Release in step 7 is copied from it, so make any wording changes here first.

## 3. Test the commit locally

Build fresh and start the stack, then open [http://localhost:9108/](http://localhost:9108/) and run each supported trend once from the Index page:

```bash
docker compose build --pull --no-cache && docker compose up -d
```

Inside the repo, `docker compose` also loads `compose.override.yaml`, so this runs the local build, not the published image.

**What ships isn't exactly what was tested.** Docker Publish builds the images again after the tag is pushed. Python packages can't change, since `Pipfile.lock` pins them, but the base image (`python:3.14-alpine`) and the Alpine packages (`firefox-esr`, `geckodriver`) can move to newer versions between the local build, Compose Test and the publish. The GHCR and Docker Hub images are also separate builds. The published-image test in step 6 runs both registries' images on amd64 and arm64 right after publishing, which is the closest check.

## 4. Commit and tag

Commit the release, including `CHANGELOG.md` so the tagged commit carries its own notes. A release commit that bundles unrelated changes gets one prefixed line per change:

```bash
git add CHANGELOG.md <other changed files>
git commit -m "release: vX.Y.Z" -m "feat: ..." -m "fix: ..."
git tag -a vX.Y.Z -m "vX.Y.Z"
```

The tag is annotated, so it records who tagged the release and when, and `git describe` finds it.

## 5. Push `main`, wait for CI, then push the tag

Pushing the tag starts the Docker Publish workflow ([`.github/workflows/docker.yml`](.github/workflows/docker.yml)) right away, and it doesn't wait for any other workflow. So push `main` on its own first, and push the tag only once Python Lint and Compose Test pass on the release commit:

```bash
git push origin main
sleep 15  # give GitHub a moment to queue the runs
for wf in lint.yml compose-test.yml; do
  gh run watch --exit-status "$(gh run list --workflow $wf --commit "$(git rev-parse HEAD)" --limit 1 --json databaseId -q '.[0].databaseId')"
done
git push origin vX.Y.Z
git ls-remote --tags origin | grep vX.Y.Z
git remote -v  # SSH only, no token in any URL
```

If either workflow fails, fix the cause, commit it, move the tag to the new commit (`git tag -fa vX.Y.Z -m "vX.Y.Z"`), and repeat this step.

Push one tag at a time. Tags pushed together publish in parallel, and `latest` can end up on whichever finishes last.

## 6. Watch the images publish, then the published-image test

Docker Publish builds the image for `linux/amd64` and `linux/arm64`, and pushes it to both registries with a GitHub build provenance attestation for each:

- `ghcr.io/wazam/fantasy-baseball-buzz`
- `wazam123/fantasy-baseball-buzz` on Docker Hub

Each gets four tags: `X.Y.Z`, `X.Y`, `latest`, and `main`. Follow the run until both jobs pass:

```bash
sleep 15  # give GitHub a moment to queue the run
gh run watch --exit-status "$(gh run list --workflow docker.yml --commit "$(git rev-parse HEAD)" --limit 1 --json databaseId -q '.[0].databaseId')"
```

The `--commit` filter keeps an earlier release's run from being picked up: without it, `gh run list` can return the previous release's finished Docker Publish run, and `gh run watch` passes at once.

If a job fails, fix the cause on `main`, then move the tag to the fixed commit before rerunning (`git tag -fa vX.Y.Z -m "vX.Y.Z"` and `git push -f origin vX.Y.Z`), so the images and the tag match.

When Docker Publish succeeds, it starts one Compose Test run with four jobs: it pulls `X.Y.Z` from GHCR and from Docker Hub, on amd64 and on arm64, and runs the same checks as on every push. All four must pass:

```bash
sleep 15  # give GitHub a moment to queue the run
gh run watch --exit-status "$(gh run list --workflow compose-test.yml --event workflow_run --commit "$(git rev-parse HEAD)" --limit 1 --json databaseId -q '.[0].databaseId')"
```

The commit filter works because `main` and the tag point at the same commit; push nothing else to `main` until this run finishes. If no run appears, check that `gh workflow list` shows Compose Test as active: GitHub disables scheduled workflows after 60 days without repo activity, and a disabled workflow skips this run too (`gh workflow enable compose-test.yml`).

### If the published image is bad

Point `latest` back at the previous version's images, which are already built, then fix forward with a new patch version instead of re-pushing the tag:

```bash
docker buildx imagetools create -t ghcr.io/wazam/fantasy-baseball-buzz:latest ghcr.io/wazam/fantasy-baseball-buzz:<previous>
docker buildx imagetools create -t wazam123/fantasy-baseball-buzz:latest wazam123/fantasy-baseball-buzz:<previous>
```

Do the same for `main`, and for `X.Y` if it moved.

## 7. Create the GitHub Release

Pull the notes for this version out of `CHANGELOG.md`, without its `##` line, and create the release from them:

```bash
awk '/^## \[vX.Y.Z\]/{f=1;next} /^## /{f=0} f' CHANGELOG.md \
  | gh release create vX.Y.Z --title "vX.Y.Z" --latest --notes-file -
```

Then check that every older release page still matches its `CHANGELOG.md` section. Pages edited on GitHub drift:

```bash
for v in $(git tag -l 'v*'); do
  diff <(gh release view $v --json body -q .body | tr -d '\r' | sed '/^$/d') \
       <(awk "/^## \\[$v\\]/{f=1;next} /^## /{f=0} f" CHANGELOG.md | sed '/^$/d') >/dev/null \
    && echo "$v matches" || echo "$v DIFFERS"
done
```

For a page that differs, move anything it has that `CHANGELOG.md` lacks into `CHANGELOG.md` first (commit it as `docs: sync vX.Y.Z notes with its release page`), then overwrite the page from it:

```bash
awk "/^## \\[$v\\]/{f=1;next} /^## /{f=0} f" CHANGELOG.md | gh release edit $v --notes-file -
```

## 8. Check the published image

```bash
docker buildx imagetools inspect ghcr.io/wazam/fantasy-baseball-buzz:X.Y.Z
docker buildx imagetools inspect wazam123/fantasy-baseball-buzz:X.Y.Z
for image in ghcr.io/wazam/fantasy-baseball-buzz:X.Y.Z wazam123/fantasy-baseball-buzz:X.Y.Z; do
  gh attestation verify oci://$image --repo wazam/fantasy-baseball-buzz \
    --signer-workflow wazam/fantasy-baseball-buzz/.github/workflows/docker.yml --source-ref refs/tags/vX.Y.Z
done
```

Both registries should list `linux/amd64` and `linux/arm64` and nothing else, and both attestations should verify.

`docker.yml` attests each pushed image with `actions/attest` (since v0.4.0). The attestations live in GitHub's attestation store, not in the registries, and both build steps set `provenance: false`, so buildx adds no unsigned provenance manifests (`unknown/unknown`) to the index. Each release therefore adds only its image to GHCR, and the package page's header shows it. Up to v0.3.3, `docker.yml` signed GHCR's images with cosign instead: the signature, pushed last as a `sha256-<digest>.sig` tag in the image's package, became the version the page showed. Those signatures were deleted from the package on 2026-11-11, so v0.3.3 and older can't be checked with `cosign verify` (their entries in Sigstore's transparency log remain).

Then the labels and GHCR's description annotation, in both registries. Each platform should show the same 12 labels: the Dockerfile's 9 (title, description, url, source, documentation, licenses, authors, vendor, base.name), plus `created`, `revision` equal to `git rev-parse vX.Y.Z^{commit}`, and `version` `X.Y.Z`. The index should hold the description:

```bash
for image in ghcr.io/wazam/fantasy-baseball-buzz:X.Y.Z wazam123/fantasy-baseball-buzz:X.Y.Z; do
  docker buildx imagetools inspect $image --format '{{json .Image}}' | python3 -c "import json,sys; d=json.load(sys.stdin); [print(p, json.dumps(v['config']['Labels'], indent=1, sort_keys=True)) for p, v in d.items()]"
  docker buildx imagetools inspect $image --raw | python3 -c "import json,sys; print(json.load(sys.stdin).get('annotations'))"
done
```

Then open [the GHCR package page](https://github.com/wazam/fantasy-baseball-buzz/pkgs/container/fantasy-baseball-buzz) and check that its header shows the `X.Y.Z` image, not a `sha256-...sig` tag, with the description and a `docker pull` command for the image.

### GHCR package versions

GHCR lists every manifest as a version. A release adds three: its tagged index and, untagged, the amd64 and arm64 images the index points to. v0.3.0 to v0.3.3 also have untagged `unknown/unknown` provenance manifests, one per platform. Never delete an untagged version that a tagged index lists: pulls of that release, or tools that read the whole index, break. Docker Hub's Image Management page lists the same manifests under the same rule, its "Preview and delete" also takes everything a selected index references, and its deletions can't be undone. To see what each version is:

```bash
gh api --paginate '/users/wazam/packages/container/fantasy-baseball-buzz/versions?per_page=100' \
  --jq '.[] | "\(.id) \(.name) \(.metadata.container.tags|join(","))"'
docker buildx imagetools inspect --raw ghcr.io/wazam/fantasy-baseball-buzz:X.Y.Z   # the digests the index lists
```

Listing needs a token with `read:packages` and deleting one with `delete:packages` (`gh auth refresh -h github.com -s read:packages,delete:packages`, then `-r` to drop them). GitHub can restore a deleted version for 30 days.

## 9. Update the Docker Hub page and GitHub About

GHCR's package page shows the README by itself. Docker Hub's page and GitHub's About description don't update on their own, so copy them from the README whenever its intro, features, quick start, settings table, or screenshots changed:

- **Docker Hub overview:** on hub.docker.com, open the repository's General tab and update the overview. It copies the README in this order, with every link and image absolute:
  - a first line `GitHub: https://github.com/wazam/fantasy-baseball-buzz`, then the README's intro paragraph without its icon (Docker Hub shows the repository's avatar)
  - `## Quick Start`: Run via Docker Compose, with the two registries, the `compose.yaml`, and the numbered steps, without Build from Source
  - `## Features`, then `## Issues and Feature Requests` with the issues sentence from the README's Contributing section

  Then check the public page, [hub.docker.com/r/wazam123/fantasy-baseball-buzz](https://hub.docker.com/r/wazam123/fantasy-baseball-buzz).
- **One-line description:** one sentence of at most 100 characters (Docker Hub's limit) saying what the README's first sentence says, used as both Docker Hub's short description and GitHub's About description:

    ```bash
    gh repo edit wazam/fantasy-baseball-buzz --description "<sentence>"
    ```

    The Dockerfile's `org.opencontainers.image.description` label holds the same sentence, and the published images and GHCR's package page take it from there, so a new sentence goes into the Dockerfile in the release's own commits.

## 10. Verify

- [ ] Buzz runs from the published image: healthy, logs normal, trends run.
- [ ] The [release](https://github.com/wazam/fantasy-baseball-buzz/releases) shows as Latest with the notes from step 2, and the `CHANGELOG.md` heading link now opens it.
- [ ] The loop in step 7 prints `matches` for every tag.
- [ ] The README's badges show the new version, and its compose example, setup steps, and screenshots still match the release.
- [ ] The Docker Hub page and the About description match the README.
