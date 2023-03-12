import remi

from performer_hierarchy import (
    PerformerTypeHierarchy,
    PerformerHierarchy,
    PERFORMER_TYPE_HIERARCHY,
)


class MyApp(remi.server.App):
    performer_type_hierarchy: PerformerTypeHierarchy = PERFORMER_TYPE_HIERARCHY
    performer_hierarchy: PerformerHierarchy = {}

    def main(self):
        """Gets called when the app is started"""
        self.main_container = remi.gui.VBox(
            width=1000, height=600, style={"margin": "10px auto"}
        )
        self.instantiate_performers()
        self.implement_stage_management()
        return self.main_container

    def idle(self):
        """Gets called every update_interval seconds"""
        self.implement_stage_management()

    def instantiate_performers(self):
        """
        Uses _recursively_instantiate_performers() to instantiate objects of each performer type in
        self.performer_type_hierarchy and store them in self.performer_hierarchy
        """

        def _recursively_instantiate_performers(
            performer_type_hierarchy: PerformerTypeHierarchy,
        ) -> PerformerHierarchy:
            """
            Instantiates objects of each performer type at the current level of the hierarchy and recurses inwards
            """
            performer_hierarchy = {}
            for (
                performer_type,
                sub_performer_type_hierarchy,
            ) in performer_type_hierarchy.items():
                performer = performer_type(
                    name=performer_type.__name__, app_instance=self
                )
                performer_hierarchy[performer] = _recursively_instantiate_performers(
                    sub_performer_type_hierarchy
                )
            return performer_hierarchy

        self.performer_hierarchy = _recursively_instantiate_performers(
            self.performer_type_hierarchy
        )

    def implement_stage_management(self):
        """
        Uses a recursive function to navigate self.performer_hierarchy and implement "stage management"
        """

        def _recursively_put_on_or_take_off_the_stage(
            performer_hierarchy: PerformerHierarchy,
            parent_container: remi.gui.Container,
        ):
            """
            Case 1:
                If the performer should render and is not already on the stage:
                    1. Put it on the stage
                    2. Recurse into the performer's sub-performers
            Case 2:
                If the performer should not render and is already on the stage:
                    1. Take it off the stage
                    2. DON'T recurse into the performer's sub-performers...
                    (a child performer should not be on the stage if its parent is not on the stage)
            Case 3:
                If the performer should render and is already on the stage:
                    1. Do nothing (the performer is already where it should be)
                    2. Recurse into the performer's sub-performers
            """
            for performer, sub_performer_hierarchy in performer_hierarchy.items():
                # case 1
                if (
                    performer.should_be_on_stage()
                    and performer.container not in parent_container.children
                ):
                    parent_container.append(performer.container, performer.container.name)
                    _recursively_put_on_or_take_off_the_stage(
                        sub_performer_hierarchy, performer.container
                    )
                # case 2
                elif (
                    not performer.should_be_on_stage()
                    and performer.container in parent_container.children.values()
                ):
                    parent_container.remove_child(performer.container)
                # case 3
                else:
                    _recursively_put_on_or_take_off_the_stage(
                        sub_performer_hierarchy, performer.container
                    )

        _recursively_put_on_or_take_off_the_stage(
            self.performer_hierarchy, self.main_container
        )


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
