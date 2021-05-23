# workflowsawaiting

Check for [GitHub Actions](https://github.com/features/actions) workflow runs which are awaiting approval.

From https://docs.github.com/en/actions/managing-workflow-runs/approving-workflow-runs-from-public-forks

> workflows on pull requests are not run automatically if they are received from first-time contributors, and must be approved first

This policy puts a large burden on repository maintainers. Even with an active maintainer, it can result in will be significant delays in the important feedback cycle between contributors and the CI system for first PRs, which are the very ones that benefit the most from an automated validation system. It can be easy for maintainers to overlook that a push to a PR necessitates another approval.

For this reason, it's useful to have a tool to monitor repositories for unapproved workflows.

## Table of Contents

<!-- toc -->

- [Usage](#usage)
  - [Arguments](#arguments)
    - [`CONFIG_PATH`](#config_path)
  - [Options](#options)
    - [`--report-path`](#--report-path)
    - [`--verbose`](#--verbose)
  - [Environment variables](#environment-variables)
    - [`GITHUB_TOKEN`](#github_token)
- [Configuration file](#configuration-file)
  - [`name`](#name)
  - [`action`](#action)
  - [`scope`](#scope)

<!-- tocstop -->

## Usage

```
poetry run python workflowsawaiting.py [OPTION]... CONFIG_PATH
```

### Arguments

#### `CONFIG_PATH`

**Required**

Path to a [YAML](https://en.wikipedia.org/wiki/YAML) formatted file defining the repositories to monitor workflows in.

See the [Configuration file](#configuration-file) section for details on the file format.

### Options

#### `--report-path`

**Optional**

Path to output a [JSON](https://www.json.org/) format report of the results to.

#### `--verbose`

**Optional**

Output debug information.

### Environment variables

#### `GITHUB_TOKEN`

**Required**

[GitHub access token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) to use for the GitHub API requests.

## Configuration file

The repositories to monitor workflows in are defined by a [YAML](https://en.wikipedia.org/wiki/YAML) formatted file.

It is a list of configuration objects, which support the following keys:

### `owner`

Repository owner. If an owner, the configuration applies to all that owner's repositories, though subsequent configuration objects can modify that list.

### `repo`

Repository name. If no `repo` is specified by a configuration object, the `action` is applied to all the owner's repositories which are in the `scope`, though subsequent configuration objects can modify that list.

### `action`

Supported values:

- **`monitor`** (default)
- **`ignore`**

### `scope`

Supported values:

- **`maintaining`**: (default) monitor only repositories where the owner of [`GITHUB_TOKEN`](#github_token) has permissions.
- **`all`**: monitor all repositories
