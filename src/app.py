import remi

from subapps.header import Header
from subapps.subapp_hierarchy import SUBAPP_HIERARCHY, SubAppHierarchy

BACKGROUND_COLOR = "lightgray"


class MyApp(remi.server.App):
    performer_hierarchy: SubAppHierarchy = SUBAPP_HIERARCHY

    def main(self):
        """Gets called when the app is started"""
        # main container
        self.main_container = remi.gui.Container(width="100%", height="100%")
        self.main_container.css_background_color = BACKGROUND_COLOR

        # header container
        self.header = Header(name="header")
        self.main_container.append(self.header.container, "header")

        # content container
        self.content_container = remi.gui.VBox(
            width="100%", style={"margin": "23px 0px", "background": "none"}
        )
        self.main_container.append(self.content_container, "content")

        self.manage_sub_apps()
        return self.main_container

    def idle(self):
        """Gets called every update_interval seconds"""
        self.manage_sub_apps()

    def manage_sub_apps(self):
        """
        Recurses through the sub-app hierarchy in order to:
          1. add/remove sub-apps
          2. call do_stuff on active sub-apps
        """

        def _recursively_manage_sub_apps(
            subapp_hierarchy: SubAppHierarchy,
            parent_container: remi.gui.Container,
        ):
            """
            Does the following for any given sub-app:
                Case 1:
                    If the sub-appshould render and is not already on the stage:
                        1. Put it on the stage
                        2. Recurse into the sub-app's sub-performers
                        3. call the sub-app's do_stuff method
                Case 2:
                    If the sub-app should not render and is already on the stage:
                        1. Take it off the stage
                        2. DON'T recurse into the sub-app's children...
                        (a child sub-app should not be on the stage if its parent is not on the stage)
                Case 3:
                    If the sub-app should render and is already on the stage:
                        1. Do nothing (the sub-app is already where it should be)
                        2. Recurse into the sub-app's sub-app
                        3. call the sub-app's do_stuff method
            """
            for subapp, child_hierarchy in subapp_hierarchy.items():
                # case 1
                if (
                    subapp.should_be_on_stage()
                    and subapp.container not in parent_container.children
                ):
                    parent_container.append(subapp.container, subapp.name)
                    _recursively_manage_sub_apps(child_hierarchy, subapp.container)
                    subapp.do_stuff()
                # case 2
                elif (
                    not subapp.should_be_on_stage()
                    and subapp.container in parent_container.children.values()
                ):
                    parent_container.remove_child(subapp.container)
                # case 3
                else:
                    _recursively_manage_sub_apps(child_hierarchy, subapp.container)
                    subapp.do_stuff()

        # first, call the header's do_stuff method
        self.header.do_stuff()

        # then, call the recursive function to manage the app's content sub-apps
        _recursively_manage_sub_apps(self.performer_hierarchy, self.content_container)


if __name__ == "__main__":
    remi.start(
        MyApp,
        address="0.0.0.0",
        port=0,
        start_browser=True,
        username=None,
        password=None,
        update_interval=1,
    )
