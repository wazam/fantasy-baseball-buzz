# Contributing to Buzz

First off, thanks for taking the time to contribute! 🎉  
This project benefits from community feedback, bug reports, ideas, and pull requests.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally

    ```bash
    git clone https://github.com/your-username/fantasy-baseball-buzz.git
    cd fantasy-baseball-buzz
    ```

3. **Install dependencies** with [Pipenv](https://pipenv.pypa.io/en/latest/)

    ```bash
    pipenv install
    pipenv shell
    ```

4. **Set up Docker** if testing full-stack behavior

    ```bash
    docker compose up -d
    ```

## Types of Contributions

- **Bug Reports:** Found a scraping error? Bad column value? Broken UI component? File an [issue](https://github.com/wazam/fantasy-baseball-buzz/issues).
- **Feature Requests:** Think something's missing? We’d love to hear it.
- **Code Improvements:** Optimize, refactor, or modernize pieces of the app.
- **Docs & README:** Better clarity is always welcome. Even small fixes help!

## Style Guide

- Use **4-space** indentation (Python)
- Follow **PEP8** and **Black** formatting where possible
- Keep functions small and focused
- Use descriptive variable names
- Prefer `f""`-style string formatting

## Pull Requests

1. Create a new branch

    ```bash
    git checkout -b your-feature-name
    ```

2. Make your changes and **commit clearly**

    ```bash
    git commit -m "Add feature: support for CBS leagues"
    ```

3. Push and open a PR from your forked repo

    ```bash
    git push origin your-feature-name
    ```

4. Describe your changes in the PR:
    - What does it do?
    - Why is it useful?
    - Any dependencies or breaking changes?

---

Thanks again! 🙌
