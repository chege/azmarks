import sys
import click
import yaml
import importlib
import pkgutil
import logging  # Import the logging module
from azure.identity import AzureCliCredential, InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure_bookmarks_tool import browsers

# Setup logging configuration
logger = logging.getLogger(__name__)


def setup_logging(verbose: int):
    """
    Configures logging based on the verbosity level.
    """
    log_level = logging.WARNING  # Default log level
    if verbose == 1:
        log_level = logging.INFO
    elif verbose >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger.debug(f"Logging configured. Level: {logging.getLevelName(log_level)}")


def load_plugins():
    logger.debug("Loading plugins...")
    plugins = {}
    for _, module_name, _ in pkgutil.iter_modules(browsers.__path__):
        module = importlib.import_module(f"azure_bookmarks_tool.browsers.{module_name}")
        logger.debug(f"Imported module: {module_name}")
        for attr in dir(module):
            cls = getattr(module, attr)
            if isinstance(cls, type) and hasattr(cls, "name") and hasattr(cls, "generate_bookmarks"):
                plugins[cls.name.lower()] = cls
                logger.debug(f"Registered plugin: {cls.name}")
    logger.info(f"Total plugins loaded: {len(plugins)}")
    return plugins


def load_config():
    logger.debug("Loading configuration from 'config.yaml'...")
    try:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
            logger.debug(f"Configuration loaded: {config}")
            return config
    except FileNotFoundError:
        logger.error("Configuration file 'config.yaml' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing 'config.yaml': {e}")
        sys.exit(1)


def authenticate(force_reauth):
    logger.debug(f"Authenticating. Force reauth: {force_reauth}")

    if force_reauth:
        logger.info("Forcing re-authentication using InteractiveBrowserCredential.")
        credential = InteractiveBrowserCredential()
    else:
        try:
            logger.debug("Attempting to authenticate using AzureCliCredential.")
            credential = AzureCliCredential()
            # Test the credential
            subscription_client = SubscriptionClient(credential)
            list(subscription_client.subscriptions.list())
            logger.info("Authenticated using Azure CLI credentials.")
        except Exception as e:
            logger.warning(f"Azure CLI authentication failed: {e}. Falling back to InteractiveBrowserCredential.")
            credential = InteractiveBrowserCredential()
    return credential


def get_resources(credential, config):
    logger.debug("Fetching resources from Azure subscriptions...")

    subscription_client = SubscriptionClient(credential)
    resources = []

    for subscription in subscription_client.subscriptions.list():
        subscription_id = subscription.subscription_id
        subscription_name = subscription.display_name

        logger.debug(f"Processing subscription: {subscription_name} ({subscription_id})")

        resource_client = ResourceManagementClient(credential, subscription_id)

        try:
            for resource in resource_client.resources.list():
                resource_type = resource.type
                resource_name = resource.name
                logger.debug(f"Found resource: {resource_name} of type {resource_type}")

                # Apply filtering based on config
                filter_type = config.get("filter_type")
                resource_filters = config.get("resources", [])
                if filter_type == "include" and resource_type not in resource_filters:
                    logger.debug(
                        f"Excluding resource '{resource_name}' of type '{resource_type}' based on 'include' filter.")
                    continue
                if filter_type == "exclude" and resource_type in resource_filters:
                    logger.debug(
                        f"Excluding resource '{resource_name}' of type '{resource_type}' based on 'exclude' filter.")
                    continue

                resources.append(
                    {
                        "subscription_name": subscription_name,
                        "subscription": subscription_name,
                        "resource_type": resource_type,
                        "resource_name": resource_name,
                        "resource": resource_name,
                        "resource_id": resource.id,
                        "location": resource.location,
                    }
                )
        except Exception as e:
            logger.error(f"Failed to list resources for subscription '{subscription_name}': {e}")
    logger.info(f"Total resources fetched: {len(resources)}")
    return resources


@click.command(context_settings={"ignore_unknown_options": True})
@click.option(
    "--force-reauth",
    is_flag=True,
    help="Force re-authentication, bypassing existing login session."
)
@click.option(
    "--browser",
    help="Specify the browser for which to generate bookmarks.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity of logging output. Use -v for INFO, -vv for DEBUG."
)
def main(force_reauth, browser, verbose):
    """Azure Bookmarks Tool CLI with dynamically loaded browser plugins."""

    # Setup logging based on verbosity
    setup_logging(verbose)
    logger.debug("Starting the Azure Bookmarks Tool...")

    # Load all available plugins dynamically
    plugins = load_plugins()

    if not plugins:
        logger.error("No browser plugins found.")
        raise click.UsageError("No browser plugins found.")

    # If no browser option is provided, list available browsers
    if browser is None:
        click.echo("Please specify a browser. Available browsers are:")
        for name, plugin_class in plugins.items():
            click.echo(f"--{name}: {plugin_class.description}")
        sys.exit(1)

    # Load the selected plugin
    plugin_class = plugins.get(browser.lower())
    if plugin_class is None:
        click.echo(f"Browser plugin '{browser}' not found.")
        sys.exit(1)

    logger.info(f"Selected browser plugin: {browser}")

    config = load_config()
    filter_type = config.get("filter_type")

    if filter_type not in ["include", "exclude"]:
        logger.error("Invalid 'filter_type' in config.yaml. Must be either 'include' or 'exclude'.")
        raise click.UsageError("Error: 'filter_type' in config.yaml must be either 'include' or 'exclude'.")

    credential = authenticate(force_reauth)
    resources = get_resources(credential, config)

    logger.info(f"Generating bookmarks for {len(resources)} resources using '{browser}' plugin.")

    # Instantiate the selected plugin and generate bookmarks
    plugin = plugin_class()
    try:
        plugin.generate_bookmarks(resources, config)
        logger.info("Bookmarks generated successfully.")
    except Exception as e:
        logger.error(f"Failed to generate bookmarks: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()