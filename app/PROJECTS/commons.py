from . import queries as project_queries
from ..MODELS.commons import delete_model

def get_current_project(cursor, user_email: str):
    row = cursor.execute(project_queries.get_current_project, (user_email,)).fetchone()
    if not row:
        raise Exception("No active project found for the user")
    return row[0]

def add_new_project(cursor, user_email: str, project_name: str):
    project_id = get_project_id(cursor, user_email, project_name)
    if project_id:
        raise Exception("Project name already exists")
    row = cursor.execute(project_queries.insert_new_project, (user_email, project_name)).fetchone()
    if not row:
        raise Exception("Failed to create project")
    return row[0]

def open_project(cursor, user_email: str, project_name: str):
    project_id = get_project_id(cursor, user_email, project_name)
    if not project_id:
        raise Exception("Project not found")
    cursor.execute(project_queries.set_project_status, (user_email, user_email, project_name))
    return project_name

def delete_project(cursor, user_email: str, project_name: str):
    if project_name == 'default':
        raise Exception("Default project cannot be deleted")
    project_id = get_project_id(cursor, user_email, project_name)
    if not project_id:
        raise Exception("Project not found")
    
    all_models = cursor.execute(project_queries.get_project_models, (user_email, project_name)).fetchall()
    for (model_name,) in all_models:
        delete_model(cursor, user_email, project_name, model_name)

    cursor.execute(project_queries.delete_project, (user_email, project_name))
    row = cursor.execute(project_queries.get_current_project, (user_email,)).fetchone()
    if not row:
        open_project(cursor, user_email, "default")
    return project_name


# Common function to get project id, not exposed as an endpoint
def get_project_id(cursor, user_email: str, project_name: str):
    row = cursor.execute(project_queries.get_project_id, (user_email, project_name)).fetchone()
    return row[0] if row else None