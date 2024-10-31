from azure_bookmarks_tool.transform import transform


def test_transform_1():
    # Load the config from the same directory as the test
    config = {
        "base_url": "https://portal.azure.com/#@ksatno.onmicrosoft.com",
        "links": [
            {"overview": "/resource/subscriptions/{subscription_id}/overview"},
            {"resources": "/resource/subscriptions/{subscription_id}/resources"},
            {"deployments": "/resource/subscriptions/{subscription_id}/subdeployments"},
            {
                "resource": "/resource/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/{provider}/{resource_type}/{resource_name}/"
            },
        ],
        "structure": [
            {
                "{field:subscription_name}": [
                    {"Overview": "{link:overview}"},
                    {"Resources": "{link:resources}"},
                    {"Deployments": "{link:deployments}"},
                    {
                        "{field:resource_type}": [
                            {"{field:resource_name}": "{link:resource}"}
                        ]
                    },
                ]
            }
        ],
    }
    intermediate_data = [
        {
            "subscription_id": "sub1",
            "subscription_name": "Subscription One",
            "resource_group": "rg-infra-dev-kogs",
            "provider": "Microsoft.Compute",
            "resource_type": "virtualMachines",
            "resource_name": "vm1",
            "location": "westus",
        },
        {
            "subscription_id": "sub1",
            "subscription_name": "Subscription One",
            "resource_group": "rg-infra-dev-kogs",
            "provider": "Microsoft.Compute",
            "resource_type": "virtualMachines",
            "resource_name": "vm2",
            "location": "westus",
        },
        {
            "subscription_id": "sub1",
            "subscription_name": "Subscription One",
            "resource_group": "rg-infra-dev-kogs",
            "provider": "Microsoft.Storage",
            "resource_type": "storageAccounts",
            "resource_name": "storage1",
            "location": "eastus",
        },
        {
            "subscription_id": "sub2",
            "subscription_name": "Subscription Two",
            "resource_group": "rg-infra-prod-kogs",
            "provider": "Microsoft.Sql",
            "resource_type": "servers",
            "resource_name": "sqlserver1",
            "location": "centralus",
        },
    ]

    expected_output = {
        "Subscription One": {
            "Overview": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/overview",
            "Resources": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resources",
            "Deployments": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/subdeployments",
            "virtualMachines": {
                "vm1": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resourceGroups/rg-infra-dev-kogs/providers/Microsoft.Compute/virtualMachines/vm1/",
                "vm2": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resourceGroups/rg-infra-dev-kogs/providers/Microsoft.Compute/virtualMachines/vm2/",
            },
            "storageAccounts": {
                "storage1": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resourceGroups/rg-infra-dev-kogs/providers/Microsoft.Storage/storageAccounts/storage1/"
            },
        },
        "Subscription Two": {
            "Overview": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/overview",
            "Resources": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/resources",
            "Deployments": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/subdeployments",
            "servers": {
                "sqlserver1": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/resourceGroups/rg-infra-prod-kogs/providers/Microsoft.Sql/servers/sqlserver1/"
            },
        },
    }

    output = transform(intermediate_data, config)

    assert output == expected_output


def test_transform_2():
    # Load the config from the same directory as the test
    config = {
        "base_url": "https://portal.azure.com/#@ksatno.onmicrosoft.com",
        "links": [
            {"overview": "/resource/subscriptions/{subscription_id}/overview"},
            {"resources": "/resource/subscriptions/{subscription_id}/resources"},
            {"deployments": "/resource/subscriptions/{subscription_id}/subdeployments"},
            {"events": "/resource/subscriptions/{subscription_id}/events"},
            {
                "resource": "/resource/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/{provider}/{resource_type}/{resource_name}/"
            },
        ],
        "structure": [
            {
                "{field:subscription_name}": [
                    {"Overview": "{link:overview}"},
                    {"Resources": "{link:resources}"},
                    {"Deployments": "{link:deployments}"},
                    {"Events": "{link:deployments}"},
                    {
                        "{field:resource_group}": [
                            {"{field:resource_name}": "{link:resource}"}
                        ]
                    },
                ]
            }
        ],
    }
    intermediate_data = [
        {
            "subscription_id": "sub1",
            "subscription_name": "Subscription One",
            "resource_group": "rg-infra-dev-kogs",
            "provider": "Microsoft.Compute",
            "resource_type": "virtualMachines",
            "resource_name": "vm1",
            "location": "westus",
        },
        {
            "subscription_id": "sub1",
            "subscription_name": "Subscription One",
            "resource_group": "rg-infra-dev-kogs",
            "provider": "Microsoft.Compute",
            "resource_type": "virtualMachines",
            "resource_name": "vm2",
            "location": "westus",
        },
        {
            "subscription_id": "sub1",
            "subscription_name": "Subscription One",
            "resource_group": "rg-infra-dev-kogs",
            "provider": "Microsoft.Storage",
            "resource_type": "storageAccounts",
            "resource_name": "storage1",
            "location": "eastus",
        },
        {
            "subscription_id": "sub2",
            "subscription_name": "Subscription Two",
            "resource_group": "rg-infra-prod-kogs",
            "provider": "Microsoft.Sql",
            "resource_type": "servers",
            "resource_name": "sqlserver1",
            "location": "centralus",
        },
    ]

    expected_output = {
        "Subscription One": {
            "Overview": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/overview",
            "Resources": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resources",
            "Deployments": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/subdeployments",
            "Events": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/subdeployments",
            "rg-infra-dev-kogs": {
                "vm1": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resourceGroups/rg-infra-dev-kogs/providers/Microsoft.Compute/virtualMachines/vm1/",
                "vm2": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resourceGroups/rg-infra-dev-kogs/providers/Microsoft.Compute/virtualMachines/vm2/",
                "storage1": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resourceGroups/rg-infra-dev-kogs/providers/Microsoft.Storage/storageAccounts/storage1/",
            },
        },
        "Subscription Two": {
            "Overview": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/overview",
            "Resources": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/resources",
            "Deployments": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/subdeployments",
            "Events": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/subdeployments",
            "rg-infra-prod-kogs": {
                "sqlserver1": "https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/resourceGroups/rg-infra-prod-kogs/providers/Microsoft.Sql/servers/sqlserver1/"
            },
        },
    }

    output = transform(intermediate_data, config)

    assert output == expected_output
