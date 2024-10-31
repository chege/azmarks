import logging

from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient

# Set up logging configuration
logger = logging.getLogger(__name__)


def get_resources(credential, config):
    """
    Fetch resources from Azure and return them in the intermediate flat format.

    :param credential: An authenticated credential object.
    :param config: A dictionary containing 'resource_filter', 'subscription_filter', and related keys.
    :return: A list of dictionaries representing resources in the intermediate format.
    """
    subscriptions = get_subscriptions(credential, config)
    resource_filter = config.get("resource_filter", {})
    resource_types = resource_filter.get("resources", [])
    filter_type = resource_filter.get("filter_type", "include").lower()

    intermediate_data = []

    for subscription in subscriptions:
        subscription_id = subscription.subscription_id
        subscription_name = subscription.display_name

        resources = get_resources_for_subscription(
            credential, subscription_id, resource_types, filter_type
        )

        for resource in resources:
            resource_info = {
                "subscription_id": subscription_id,
                "subscription_name": subscription_name,
                "resource_group": extract_resource_group_from_id(resource.id),
                "provider": extract_provider_from_type(resource.type),
                "resource_type": extract_resource_type_from_type(resource.type),
                "resource_name": resource.name,
                "location": resource.location,
            }
            intermediate_data.append(resource_info)

    return intermediate_data


def get_subscriptions(credential, config):
    """
    Fetch subscriptions from Azure, applying inclusion/exclusion filters from the config.

    :param credential: An authenticated credential object.
    :param config: A dictionary containing 'subscription_filter' for subscription inclusion/exclusion.
    :return: A list of Subscription objects.
    """
    subscription_filter = config.get("subscription_filter", {})
    filter_type = subscription_filter.get("filter_type", "include").lower()
    allowed_subscriptions = set(subscription_filter.get("subscriptions", []))

    subscription_client = SubscriptionClient(credential)
    all_subscriptions = list(subscription_client.subscriptions.list())

    # Apply include/exclude filter on subscriptions
    if filter_type == "include":
        return [
            sub
            for sub in all_subscriptions
            if sub.subscription_id in allowed_subscriptions
        ]
    elif filter_type == "exclude":
        return [
            sub
            for sub in all_subscriptions
            if sub.subscription_id not in allowed_subscriptions
        ]
    return all_subscriptions


def get_resources_for_subscription(
    credential, subscription_id, resource_types, filter_type
):
    """
    Fetch resources for a subscription, filtered by resource types.

    :param credential: An authenticated credential object.
    :param subscription_id: The ID of the subscription.
    :param resource_types: A list of resource types to include or exclude.
    :param filter_type: 'include' or 'exclude' to specify filtering behavior.
    :return: A list of Resource objects.
    """
    resource_client = ResourceManagementClient(credential, subscription_id)

    filter_str = None
    if resource_types:
        if filter_type == "include":
            filter_conditions = [f"resourceType eq '{rt}'" for rt in resource_types]
            filter_str = " or ".join(filter_conditions)
        elif filter_type == "exclude":
            filter_conditions = [f"resourceType ne '{rt}'" for rt in resource_types]
            filter_str = " and ".join(filter_conditions)

    resources = resource_client.resources.list(filter=filter_str)
    return list(resources)


def authenticate(force_reauth=False):
    """
    Authenticate with Azure using DefaultAzureCredential or InteractiveBrowserCredential.

    :param force_reauth: If True, forces reauthentication via InteractiveBrowserCredential.
    :return: An authenticated credential object.
    """
    logger.debug(f"Authenticating. Force reauth: {force_reauth}")

    if force_reauth:
        logger.info("Forcing re-authentication using InteractiveBrowserCredential.")
        credential = InteractiveBrowserCredential()
    else:
        try:
            logger.debug("Attempting to authenticate using DefaultAzureCredential.")
            credential = DefaultAzureCredential(
                exclude_interactive_browser_credential=False
            )
            # Test the credential
            subscription_client = SubscriptionClient(credential)
            list(subscription_client.subscriptions.list())
            logger.info("Authenticated using DefaultAzureCredential.")
        except Exception as e:
            logger.warning(
                f"DefaultAzureCredential authentication failed: {e}. Falling back to InteractiveBrowserCredential."
            )
            credential = InteractiveBrowserCredential()
    return credential


def extract_resource_group_from_id(resource_id):
    """
    Extract the resource group from the resource ID.

    :param resource_id: The resource ID string.
    :return: The resource group name.
    """
    parts = resource_id.split("/")
    try:
        rg_index = parts.index("resourceGroups")
        return parts[rg_index + 1]
    except ValueError:
        return None


def extract_provider_from_type(resource_type):
    """
    Extract the provider from the resource type.

    :param resource_type: The full resource type string.
    :return: The provider namespace.
    """
    return resource_type.split("/", 1)[0]


def extract_resource_type_from_type(resource_type):
    """
    Extract the resource type from the resource type string.

    :param resource_type: The full resource type (e.g., 'virtualMachines').
    """
    return resource_type.split("/", 1)[1] if "/" in resource_type else resource_type
