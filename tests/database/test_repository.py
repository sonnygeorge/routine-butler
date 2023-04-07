from sqlmodel import Session

from routine_butler.database.repository import Repository
from routine_butler.database.models import User


TEST_USER_USERNAME = "test"


class TestRepository:
    def test_engine_created(self, repository: Repository):
        assert repository.engine is not None


## OLD CODE

# import pytest
# from sqlmodel import SQLModel

# from database import database
# from models import Routine, RoutineElement, Alarm, User

# # TODO: mock a test database for tests


# def get_parent_new_context(child: SQLModel, parent_attr_name: str) -> SQLModel:
#     """Checks that a parent is accessible from child in this context"""
#     return getattr(child, parent_attr_name)


# class TestDatabase:
#     @pytest.mark.parametrize("data_model", [User(), Routine(), Alarm()])
#     def test_gets_nothing_after_delete(self, data_model):
#         # add data model to db
#         database.commit(data_model)
#         # delete data model
#         database.delete(data_model)
#         # check that data model is no longer in db
#         assert database.get(data_model.__class__, data_model.id) is None

#     def test_delete_deletes_children_too(self):
#         # user with one routine with one alarm
#         alarm = Alarm()
#         routine = Routine(alarms=[alarm])
#         user = User(routines=[routine])
#         # add user to db
#         database.commit(user)
#         # delete user
#         database.delete(user)
#         # check that user is no longer in db
#         assert database.get(User, user.id) is None
#         # check that routine is no longer in db
#         assert database.get(Routine, routine.id) is None
#         # check that alarm is no longer in db
#         assert database.get(Alarm, alarm.id) is None

#     def test_parent_relationship_accessible_from_child_in_new_context(self):
#         # user with one routine with one alarm and one program
#         alarm = Alarm()
#         routine_program = RoutineElement()
#         routine = Routine(alarms=[alarm], programs=[routine_program])
#         user = User(routines=[routine])
#         # add user to db
#         database.commit(user)
#         # check that user is accessible from routine
#         assert isinstance(get_parent_new_context(routine, "user"), User)
#         # check that routine is accessible from alarm
#         assert isinstance(get_parent_new_context(alarm, "routine"), Routine)
#         # check that routine is accessible from program
#         assert isinstance(
#             get_parent_new_context(routine_program, "routine"), Routine
#         )
#         # delete user
#         database.delete(user)

#     def test_delete_does_not_delete_parents(self):
#         # user with one routine with one alarm
#         alarm = Alarm()
#         routine = Routine(alarms=[alarm])
#         user = User(routines=[routine])
#         # add user to db
#         database.commit(user)
#         # delete alarm
#         database.delete(alarm)
#         # check that user is still in db
#         assert database.get(User, user.id) is not None
#         # check that routine is still in db
#         assert database.get(Routine, routine.id) is not None
#         # check that alarm is no longer in db
#         assert database.get(Alarm, alarm.id) is None
#         # clean up leftover user and routine from db
#         database.delete(user)

#     @pytest.mark.parametrize("data_model", [User(), Routine(), Alarm()])
#     def test_model_has_id_after_add(self, data_model):
#         # add data model to db
#         database.commit(data_model)
#         # check that data model now has an id
#         assert data_model.id is not None
#         # delete data model
#         database.delete(data_model)

#     def test_children_have_id_after_add(self):
#         # user with one routine with one alarm
#         alarm = Alarm()
#         routine = Routine(alarms=[alarm])
#         user = User(routines=[routine])
#         # add user to db
#         database.commit(user)
#         # check that routine and alarm have ids
#         assert routine.id is not None
#         assert alarm.id is not None
#         # delete user
#         database.delete(user)

#     @pytest.mark.parametrize("data_model", [User(), Routine(), Alarm()])
#     def test_get_returns_same_model_after_add(self, data_model):
#         # add data model to db
#         database.commit(data_model)
#         # check that database.get() returns the same object
#         assert database.get(data_model.__class__, data_model.id) == data_model
#         # delete data model
#         database.delete(data_model)

#     def test_get_returns_same_children_after_add(self):
#         # user with one routine with one alarm
#         alarm = Alarm()
#         routine = Routine(alarms=[alarm])
#         user = User(routines=[routine])
#         # add user to db
#         database.commit(user)
#         # check that database.get() returns the same routine
#         assert database.get(Routine, routine.id) == routine
#         # check that database.get() returns the same alarm
#         assert database.get(Alarm, alarm.id) == alarm
#         # delete user
#         database.delete(user)

#     def test_get_returns_updated_model_after_commit(self):
#         routine = Routine()
#         # add data model to db
#         database.commit(routine)
#         # change title
#         new_title = "ScJpHgjJX4LQJZUh"
#         routine.title = new_title
#         database.commit(routine)
#         # check if data_model comes back with new title
#         assert database.get(routine.__class__, routine.id).title == new_title
#         # delete data model
#         database.delete(routine)

#     def test_get_returns_updated_children_after_commit(self):
#         # user with one routine with one alarm
#         alarm = Alarm(hour=0, minute=0)
#         routine = Routine(title="Old Title", alarms=[alarm])
#         user = User(routines=[routine])
#         # add user to db
#         database.commit(user)
#         # change routine title
#         new_title = "New Title"
#         routine.title = new_title
#         # change alarm hour and minute
#         alarm.hour = 5
#         alarm.minute = 25
#         # commit parent user
#         database.commit(user)
#         # check if routine comes back with new title
#         assert database.get(Routine, routine.id).title == new_title
#         # check if alarm comes back with new hour and minute
#         assert database.get(Alarm, alarm.id).hour == 5
#         assert database.get(Alarm, alarm.id).minute == 25
#         # delete user
#         database.delete(user)

#     def test_commit_does_not_create_new_row_after_model_change(self):
#         num_rows_before = database.num_rows_in_table(Routine)
#         routine = Routine(title="Old Title")
#         # add data model to db
#         database.commit(routine)
#         # change title
#         new_title = "New Title"
#         routine.title = new_title
#         database.commit(routine)
#         # delete data model
#         database.delete(routine)

#         num_rows_after = database.num_rows_in_table(Routine)
#         # if num rows is different, then a new row was created
#         assert num_rows_before == num_rows_after

#     def test_commit_does_not_create_new_row_after_child_change(self):
#         num_alarms_before = database.num_rows_in_table(Alarm)
#         num_routines_before = database.num_rows_in_table(Routine)
#         # user with one routine with one alarm
#         alarm = Alarm(hour=0, minute=0)
#         routine = Routine(title="Old Title", alarms=[alarm])
#         user = User(routines=[routine])
#         # add user to db
#         database.commit(user)
#         # change routine title
#         new_title = "New Title"
#         routine.title = new_title
#         # change alarm hour and minute
#         alarm.hour = 5
#         alarm.minute = 25
#         # commit parent user
#         database.commit(user)
#         # delete user
#         database.delete(user)

#         num_alarms_after = database.num_rows_in_table(Alarm)
#         num_routines_after = database.num_rows_in_table(Routine)
#         # if num rows is different, then a new row was created
#         assert num_alarms_before == num_alarms_after
#         assert num_routines_before == num_routines_after

#     def test_child_appended_to_children_list_has_id_after_parent_commit(self):
#         # user with one routine
#         routine = Routine()
#         user = User(routines=[routine])
#         # add user to db
#         database.commit(user)
#         # add alarm to routine
#         alarm = Alarm()
#         routine.alarms.append(alarm)
#         # commit user
#         database.commit(user)
#         # check that alarm has an id
#         assert alarm.id is not None
#         # delete user
#         database.delete(user)

#     def test_child_appended_to_children_list_comes_back_same_after_parent_commit(
#         self,
#     ):
#         # user with one routine
#         routine = Routine()
#         user = User(routines=[routine])
#         # add user to db
#         database.commit(user)
#         # add alarm to routine
#         alarm = Alarm()
#         routine.alarms.append(alarm)
#         # commit user
#         database.commit(user)
#         # check that alarm comes back the same
#         assert database.get(Alarm, alarm.id) == alarm
#         # delete user
#         database.delete(user)

#     def test_removed_child_is_removed_after_parent_commit(self):
#         # user with one routine with one alarm
#         alarm = Alarm()
#         routine = Routine(alarms=[alarm])
#         user = User(routines=[routine])
#         # add user to db
#         database.commit(user)
#         # store alarm id for later retrieval
#         alarm_id = alarm.id
#         # remove alarm from routine
#         routine.alarms.remove(alarm)
#         # commit user
#         database.commit(user)
#         # retrieve supposedly orphaned alarm
#         orphaned_alarm = database.get(Alarm, alarm_id)
#         # check that alarm has no foreign key
#         assert orphaned_alarm is None

#     def test_update_parent_after_append_child_adds_child(self):
#         # user with one routine with one alarm
#         alarm = Alarm()
#         routine = Routine(alarms=[alarm])
#         user = User(routines=[routine])
#         # add user to db
#         database.commit(user)
#         # add routine to user
#         new_routine = Routine()
#         user.routines.append(new_routine)
#         # commit user
#         database.commit(user)
#         assert new_routine.id is not None
#         assert database.get(Routine, new_routine.id) == new_routine
#         # delete user
#         database.delete(user)
