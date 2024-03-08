from chimerax.core.toolshed import BundleAPI

class _Notes_API(BundleAPI):

    api_version = 1

    @staticmethod
    def start_tool(session, bi, ti):
        """
        start tools
        """
        if ti.name == "My Notes":
            from .tools.notes import NotesTool
            tool = NotesTool(session, ti.name)
            return tool

    @staticmethod
    def get_class(name):
        if name == "NotesTool":
            from .tools.notes import NotesTool
            return NotesTool

bundle_api = _Notes_API()
