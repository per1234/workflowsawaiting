# workflowsawaiting

Check for [GitHub Actions](https://github.com/features/actions) workflow runs which are awaiting approval.

From https://docs.github.com/en/actions/managing-workflow-runs/approving-workflow-runs-from-public-forks

> workflows on pull requests are not run automatically if they are received from first-time contributors, and must be approved first

This policy puts a large burden on repository maintainers. Even with an active maintainer, there will be significant delays in the important feedback cycle between contributors and the CI system for first PRs, which are the very ones that benefit the most from an automated validation system. It can be easy for maintainers to miss a push to a PR.

For this reason, it's useful to have a tool to monitor repositories for unapproved workflows.

