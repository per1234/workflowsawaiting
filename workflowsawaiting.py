import argparse
import itertools
import json
import os
import sys

import fastcore.all
import ghapi.core
import ghapi.page
import yaml
import yaml.parser

if "GITHUB_TOKEN" not in os.environ:
    print("ERROR: required environment variable GITHUB_TOKEN not set.")
    sys.exit(1)

gh_api = ghapi.core.GhApi(token=os.environ["GITHUB_TOKEN"])
username = gh_api.users.get_authenticated().login


def main():
    """The primary function."""
    with open(file=argument.configuration_path, mode="r", encoding="utf-8") as configuration_file:
        configuration_list = yaml.load(stream=configuration_file, Loader=yaml.SafeLoader)

    awaiting_count = 0

    repositories_report = []
    repositories_data = get_repositories_data(configuration_list=configuration_list)
    for repository_data in repositories_data:
        verbose_print("Getting workflow runs for", repository_data["object"].full_name)
        verbose_print("permissions:", repository_data["permissions"])
        repository_report = {
            "name": repository_data["object"].full_name,
            "permissions": repository_data["permissions"],
            "runs": get_runs(repository_data=repository_data),
        }

        if repository_report["runs"]:
            # There were workflow runs awaiting approval
            awaiting_count += len(repository_report["runs"])
            repositories_report.append(repository_report)

    report = {"repositories": repositories_report, "summary": {"awaitingCount": awaiting_count}}

    if awaiting_count:
        verbose_print("Workflow runs awaiting approval were found")

    if argument.report_path:
        verbose_print("writing report to", argument.report_path)
        with open(file=argument.report_path, mode="w", encoding="utf-8") as report_file:
            json.dump(obj=report, fp=report_file, indent=2)


def get_repositories_data(configuration_list):
    """Return data for the repositories defined by the configuration.

    Keyword arguments:
    configuration_list -- the list of configuration objects specified by the user's configuration file
    """
    verbose_print("Generating list of repositories")
    repositories_data = []
    for configuration_element in configuration_list:
        # Handle ignored repos:
        if "action" in configuration_element and configuration_element["action"] == "ignore":
            # Remove any matching repos from the list
            repositories_data[:] = list(
                itertools.filterfalse(
                    predicate=(
                        lambda repository: configuration_element["name"] == repository["object"].full_name
                        or configuration_element["name"] == repository["object"].owner.login,
                    ),
                    iterable=repositories_data,
                )
            )

            continue

        split_name = configuration_element["name"].split(sep="/", maxsplit=1)
        owner_name = split_name[0]
        repository_name = None
        if len(split_name) > 1:
            repository_name = split_name[1]

        if repository_name:
            repository_data = {"object": gh_api.repos.get(owner=owner_name, repo=repository_name)}
            repository_data["permissions"] = get_permissions(repository_object=repository_data["object"])
            if in_scope(repository_data=repository_data, configuration_element=configuration_element):
                repositories_data.append(repository_data)
        else:
            user = gh_api.users.get_by_username(username=owner_name)
            if user.type == "Organization":
                repositories_pages = ghapi.page.pages(
                    oper=gh_api.repos.list_for_org, n_pages=gh_api.last_page(), org=owner_name
                )
            else:
                repositories_pages = ghapi.page.pages(
                    oper=gh_api.repos.list_for_user, n_pages=gh_api.last_page(), username=owner_name
                )
            for repositories_page in repositories_pages:
                for repository_object in repositories_page:
                    repository_data = {
                        "object": repository_object,
                        "permissions": get_permissions(repository_object=repository_object),
                    }
                    if in_scope(repository_data=repository_data, configuration_element=configuration_element):
                        repositories_data.append(repository_data)

    return repositories_data


def get_permissions(repository_object):
    """Return the user's permissions level in the repository.

    Keyword arguments:
    repository_object -- a GitHub API repository object
    """
    try:
        return gh_api.repos.get_collaborator_permission_level(
            owner=repository_object.owner.login, repo=repository_object.name, username=username
        ).permission
    except fastcore.all.HTTP403ForbiddenError:
        return None


def in_scope(repository_data, configuration_element):
    """Return whether the given repository is in scope for the configuration.

    Keyword arguments:
    repository_data -- data for the repository
    configuration_element -- the configuration object that yielded the repository
    """
    if "scope" in configuration_element and configuration_element["scope"] == "all":
        return True

    # Determine if user has sufficient permissions in the repository_data to approve the workflow run
    return not repository_data["object"].archived and (
        repository_data["permissions"] == "write" or repository_data["permissions"] == "admin"
    )


def get_runs(repository_data):
    """Return a list of URLs for workflow runs awaiting approval in the given repo.

    Keyword arguments:
    repository_data -- data for the repository
    """
    run_urls = []
    runs_pages = ghapi.page.pages(
        oper=gh_api.actions.list_workflow_runs_for_repo,
        n_pages=gh_api.last_page(),
        owner=repository_data["object"].owner.login,
        repo=repository_data["object"].name,
        event="pull_request",
        status="action_required",
    )
    for runs_page in runs_pages:
        # if not runs_page.workflow_runs:
        #     # The paged generator gets stuck in an infinite loop on the total_count key after all the runs are
        #     # iterated over
        #     break
        for run in runs_page.workflow_runs:
            print("Run", run.html_url, "needs approval")
            run_urls.append(run.html_url)

    return run_urls


def verbose_print(*print_arguments):
    """Print output when in verbose mode."""
    if argument.verbose:
        print(*print_arguments)


# Only execute the following code if the script is run directly, not imported
if __name__ == "__main__":
    # parse command line arguments
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "configuration_path",
        help="Path to a YAML file formatted file defining the repositories to monitor workflows in.",
        metavar="CONFIG_PATH",
    )
    argument_parser.add_argument(
        "--report-path", dest="report_path", help="Path to output a report to.", metavar="REPORT_PATH"
    )
    argument_parser.add_argument("--verbose", action="store_true", help="Enable debug output")
    argument = argument_parser.parse_args()

    main()  # pragma: no cover
