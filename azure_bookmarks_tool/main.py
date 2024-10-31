import logging
import os
import sys

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape

from azure_bookmarks_tool.azure import authenticate, get_resources
from azure_bookmarks_tool.config import load_config
from azure_bookmarks_tool.transform import transform

# Setup logging configuration
logger = logging.getLogger(__name__)


def load_browser_plugins():
    """
    Placeholder function to load browser plugins.
    Implement this function based on your plugin architecture.
    """
    return {"safari": SafariBookmarkPlugin}  # Replace with actual plugin class


def render_bookmarks_html(bookmarks, title="Azure Bookmarks"):
    """
    Renders the bookmarks to an HTML string using the Jinja2 template.

    :param bookmarks: The transformed bookmarks data structure.
    :param title: The title for the bookmarks HTML.
    :return: A string containing the rendered HTML.
    """
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("safari.html")
    return template.render(title=title, bookmarks=bookmarks)


def generate_bookmarks(transformed_tree, config, output_filename="bookmarks.html"):
    """
    Generates HTML bookmarks file from the transformed data.

    :param transformed_tree: The transformed bookmarks data structure.
    :param config: The configuration dictionary.
    :param output_filename: The name of the output HTML file.
    """
    title = "Azure Bookmarks"
    rendered_html = render_bookmarks_html(transformed_tree, title)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(rendered_html)
    logger.info(f"Bookmarks generated successfully in '{output_filename}'")


def setup_logging(verbose: int):
    """
    Configures logging based on the verbosity level.
    """
    log_level = logging.WARNING
    if verbose == 1:
        log_level = logging.INFO
    elif verbose >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger.debug(f"Logging configured. Level: {logging.getLevelName(log_level)}")


@click.command(context_settings={"ignore_unknown_options": True})
@click.option(
    "--force-reauth",
    is_flag=True,
    help="Force re-authentication, bypassing existing login session.",
)
@click.option(
    "--browser",
    help="Specify the browser for which to generate bookmarks.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity of logging output. Use -v for INFO, -vv for DEBUG.",
)
def main(force_reauth, browser, verbose):
    # Setup logging based on verbosity
    setup_logging(verbose)
    logger.debug("Starting the Azure Bookmarks Tool...")

    # Load configuration
    config = load_config()

    # Check if resource and subscription filters are correctly specified
    if "resource_filter" not in config or "subscription_filter" not in config:
        raise click.UsageError(
            "Error: Configuration must include both 'resource_filter' and 'subscription_filter'."
        )

    # Authenticate
    credential = authenticate(force_reauth)

    # Fetch resources based on configuration filters
    resources = get_resources(credential, config)
    logger.info(f"Generating bookmarks for {len(resources)} resources.")

    # Transform the data into the desired structure
    transformed_tree = transform(resources, config)

    # Generate the bookmarks HTML
    generate_bookmarks(transformed_tree, config)
    logger.info("Bookmarks generated successfully.")


# Placeholder for the SafariBookmarkPlugin class
class SafariBookmarkPlugin:
    description = "Safari Browser"

    def generate_bookmarks(self, resources, config):
        transformed_tree = transform(resources, config)
        generate_bookmarks(transformed_tree, config)


if __name__ == "__main__":
    main()
