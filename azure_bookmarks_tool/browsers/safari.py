import datetime
import logging  # Import the logging module

from azure_bookmarks_tool.browser import BrowserPlugin


class SafariPlugin(BrowserPlugin):
    """Safari browser plugin to generate bookmarks."""
    name = "safari"
    description = "Generate bookmarks for Safari browser."

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initialized SafariPlugin.")

    def generate_bookmarks(self, resources, config):
        """Generates bookmarks for Safari in HTML format."""
        self.logger.info("Starting bookmark generation for Safari.")

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"bookmarks_safari_{timestamp}.html"
        include_metadata = config.get("include_metadata", False)
        structure = config.get("structure", "{subscription}/{resource_type}/{resource}")

        self.logger.debug(f"Generated filename: {filename}")
        self.logger.debug(f"Include metadata: {include_metadata}")
        self.logger.debug(f"Structure: {structure}")

        # Build the folder hierarchy
        bookmark_tree = {}

        for resource in resources:
            # Prepare resource mapping for placeholders
            resource_mapping = {
                "subscription": resource["subscription"],
                "resource_type": resource["resource_type"],
                "resource": resource["resource"],
            }

            try:
                path = structure.format(**resource_mapping)
                self.logger.debug(f"Formatted path for resource '{resource['resource_name']}': {path}")
            except KeyError as e:
                self.logger.error(f"Placeholder {e} not found in resource data for resource '{resource['resource_name']}'. Skipping.")
                continue

            # Split the path into components
            path_parts = path.strip("/").split("/")
            self.logger.debug(f"Path parts for resource '{resource['resource_name']}': {path_parts}")

            # Build the nested dictionary
            current_level = bookmark_tree

            for part in path_parts[:-1]:  # All parts except the last one
                if part not in current_level:
                    self.logger.debug(f"Creating new folder: {part}")
                current_level = current_level.setdefault(part, {})

            # Add the bookmark at the last level
            title_parts = [resource["resource_name"]]

            if include_metadata:
                title_parts.append(f"({resource['resource_type']}, {resource['location']})")

            title = " ".join(title_parts)
            url = f"https://portal.azure.com/{resource['resource_id']}"

            self.logger.debug(f"Adding bookmark: Title='{title}', URL='{url}'")

            # Initialize the '_bookmarks' list if it doesn't exist
            bookmarks = current_level.setdefault("_bookmarks", [])
            bookmarks.append((title, url))

        # Now, write a recursive function to output the bookmark_tree to HTML
        try:
            with open(filename, "w") as f:
                self.logger.debug(f"Opening file '{filename}' for writing bookmarks.")
                f.write("<!DOCTYPE NETSCAPE-Bookmark-file-1>\n")
                f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
                f.write("<TITLE>Bookmarks</TITLE>\n")
                f.write("<H1>Bookmarks</H1>\n")

                def write_bookmarks(tree, indent=0):
                    f.write("    " * indent + "<DL><p>\n")
                    for key, value in tree.items():
                        if key == "_bookmarks":
                            for title, url in value:
                                f.write(
                                    "    " * (indent + 1)
                                    + f'<DT><A HREF="{url}">{title}</A>\n'
                                )
                                self.logger.debug(f"Written bookmark to HTML: Title='{title}', URL='{url}'")
                        else:
                            f.write(
                                "    " * (indent + 1) + f"<DT><H3>{key}</H3>\n"
                            )
                            self.logger.debug(f"Written folder to HTML: {key}")
                            write_bookmarks(value, indent + 1)
                    f.write("    " * indent + "</DL><p>\n")

                write_bookmarks(bookmark_tree)
                self.logger.info(f"Bookmarks file '{filename}' has been generated successfully.")
        except Exception as e:
            self.logger.error(f"Failed to write bookmarks to file '{filename}': {e}")
            raise