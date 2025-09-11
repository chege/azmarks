import pytest
from bs4 import BeautifulSoup

from azmarks.main import render_bookmarks_html


def test_render_bookmarks_html():
    # Sample transformed data (expected_output)
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

    # Expected HTML output
    expected_html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<HTML>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Test Bookmarks</TITLE>
<H1>Test Bookmarks</H1>
<DL><p>
    <DT><H3 FOLDED>Subscription One</H3>
    <DL><p>
        <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/overview">Overview</A>
        <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resources">Resources</A>
        <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/subdeployments">Deployments</A>
        <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/subdeployments">Events</A>
        <DT><H3 FOLDED>rg-infra-dev-kogs</H3>
        <DL><p>
            <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resourceGroups/rg-infra-dev-kogs/providers/Microsoft.Compute/virtualMachines/vm1/">vm1</A>
            <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resourceGroups/rg-infra-dev-kogs/providers/Microsoft.Compute/virtualMachines/vm2/">vm2</A>
            <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub1/resourceGroups/rg-infra-dev-kogs/providers/Microsoft.Storage/storageAccounts/storage1/">storage1</A>
        </DL><p>
    </DL><p>
    <DT><H3 FOLDED>Subscription Two</H3>
    <DL><p>
        <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/overview">Overview</A>
        <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/resources">Resources</A>
        <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/subdeployments">Deployments</A>
        <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/subdeployments">Events</A>
        <DT><H3 FOLDED>rg-infra-prod-kogs</H3>
        <DL><p>
            <DT><A HREF="https://portal.azure.com/#@ksatno.onmicrosoft.com/resource/subscriptions/sub2/resourceGroups/rg-infra-prod-kogs/providers/Microsoft.Sql/servers/sqlserver1/">sqlserver1</A>
        </DL><p>
    </DL><p>
</DL><p>
</HTML>"""

    # Render the HTML
    html_output = render_bookmarks_html(expected_output, title="Test Bookmarks")

    # Normalize the HTML strings using BeautifulSoup
    soup_expected = BeautifulSoup(expected_html, "html.parser")
    soup_output = BeautifulSoup(html_output, "html.parser")

    # Compare the normalized HTML structures
    assert soup_expected.prettify() == soup_output.prettify()
