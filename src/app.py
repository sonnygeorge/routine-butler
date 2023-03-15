import remi

from subapps.header import Header
from subapps.subapp_hierarchy import PERFORMER_HIERARCHY, PerformerHierarchy


class MyApp(remi.server.App):
    performer_hierarchy: PerformerHierarchy = PERFORMER_HIERARCHY

    def main(self):
        """Gets called when the app is started"""
        # main container contains everything as is always the full screen
        self.main_container = remi.gui.Container(width="100%", height="100%")

        # header container containers header sub-app
        self.header = Header(name="header")
        self.main_container.append(self.header.container, "header")
        
        # content container contains the hierarchy of other sub-apps
        self.content_container = remi.gui.VBox(
            width="100%", style={"margin": "23px 23px"}
        )
        self.css_background_color = "lightgray"
        self.main_container.append(self.content_container, "content")

        # self.instantiate_performers()
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
            performer_hierarchy: PerformerHierarchy,
            parent_container: remi.gui.Container,
        ):
            """
            Does the following for any given sub-app:
                Case 1:
                    If the performer should render and is not already on the stage:
                        1. Put it on the stage
                        2. Recurse into the performer's sub-performers
                        3. call the performer's do_stuff method
                Case 2:
                    If the performer should not render and is already on the stage:
                        1. Take it off the stage
                        2. DON'T recurse into the performer's sub-performers...
                        (a child performer should not be on the stage if its parent is not on the stage)
                Case 3:
                    If the performer should render and is already on the stage:
                        1. Do nothing (the performer is already where it should be)
                        2. Recurse into the performer's sub-performers
                        3. call the performer's do_stuff method
            """
            for performer, sub_performer_hierarchy in performer_hierarchy.items():
                # case 1
                if (
                    performer.should_be_on_stage()
                    and performer.container not in parent_container.children
                ):
                    parent_container.append(performer.container, performer.name)
                    _recursively_manage_sub_apps(
                        sub_performer_hierarchy, performer.container
                    )
                    performer.do_stuff()
                # case 2
                elif (
                    not performer.should_be_on_stage()
                    and performer.container in parent_container.children.values()
                ):
                    parent_container.remove_child(performer.container)
                # case 3
                else:
                    _recursively_manage_sub_apps(
                        sub_performer_hierarchy, performer.container
                    )
                    performer.do_stuff()

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
