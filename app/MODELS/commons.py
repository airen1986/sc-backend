from . import queries as model_queries
from app.CONFIG.config import DATA_FOLDER, BACKUP_FOLDER, MAX_BACKUPS
import os, uuid, sqlite3, apsw, json


def get_project_id(cursor, user_name: str, project_name: str):
    row = cursor.execute(model_queries.get_project_id, (user_name, project_name)).fetchone()
    return row[0] if row else None

def add_new_model(cursor, model_name: str, project_name: str, user_name: str, template_name: str):

    project_id = get_project_id(cursor, user_name, project_name)
    if not project_id:
        raise Exception("Project does not exist for user")
    
    model_id, _ = get_model_id_and_path(cursor, model_name, project_name, user_name)
    if model_id:
        raise Exception("Model already exists in project for user")

    template_sql_file = get_template_sql_file(cursor, user_name, template_name)
    
    db_uid = str(uuid.uuid4())
    db_path = os.path.join(DATA_FOLDER, f"{db_uid}.sqlite3")
    if os.path.exists(db_path):
        raise Exception("Model with same UID already exists")
    with sqlite3.connect(db_path) as model_db:
            with open(template_sql_file, "r") as f:
                model_db.executescript(f.read())

    role = "owner"
    model_id = cursor.execute(model_queries.insert_models, (db_uid, db_path, user_name, template_name)).fetchone()[0]   
    cursor.execute(model_queries.insert_user_models, (model_id, user_name, project_id, role, model_name))

def get_model_id_and_path(cursor, model_name: str, project_name: str, user_name: str):
    row = cursor.execute(model_queries.get_model_id_and_path, (project_name, model_name, user_name)).fetchone()
    if row:
        return row[0], row[1]
    return None, None

def move_model_to_project(cursor, user_email: str, model_name: str, old_project_name: str, new_project_name: str) -> int:
    old_model_id, _ = get_model_id_and_path(cursor, model_name, old_project_name, user_email)
    if not old_model_id:
        raise Exception("Model not found in the old project")
    
    new_model_id, _ = get_model_id_and_path(cursor, model_name, new_project_name, user_email)
    if new_model_id:
        raise Exception("Model already exists in the new project")
    
    new_project_id = get_project_id(cursor, user_email, new_project_name)
    if not new_project_id:
        raise Exception("New project not found")

    old_project_id = get_project_id(cursor, user_email, old_project_name)

    row = cursor.execute(model_queries.update_user_model_project, (new_project_id, old_model_id, user_email, old_project_id)).fetchone()

    if not row:        
        raise Exception("Failed to move model to new project")
    
    return 1
     
def get_model_templates(cursor, user_email: str):
    rows = cursor.execute(model_queries.get_model_templates, (user_email,)).fetchall()
    return [row[0] for row in rows]

def get_template_sql_file(cursor, user_email: str, template_name: str, with_data: bool = False):
    all_templates = get_model_templates(cursor, user_email)
    if template_name not in all_templates:
        raise Exception("User dont have access to the template")
    
    column_name = "TemplateSQLWithData" if with_data else "TemplateSQL"
    this_query = model_queries.get_template_sql_file.format(column_name=column_name)
    row = cursor.execute(this_query, (template_name,)).fetchone()

    if not row:
        raise Exception("Template not found")
    
    file_name = row[0]
    this_parent_dir = os.path.dirname(os.path.abspath(__file__))
    this_parent_dir = os.path.dirname(this_parent_dir)
    schema_dir = os.path.join(this_parent_dir, "SCHEMA")

    sql_file = os.path.join(schema_dir, file_name)

    if not os.path.isfile(sql_file):
        raise Exception("SQL file for template not found")

    return sql_file

def get_user_models_by_project(cursor, user_email: str):
    rows = cursor.execute(model_queries.get_user_models_by_project, (user_email,)).fetchall()
    models_by_project = {}
    for project_name, model_name, access_level in rows:
        if project_name not in models_by_project:
            models_by_project[project_name] = {}
        if model_name is not None:
            models_by_project[project_name][model_name] = access_level
    return models_by_project

def save_as_model(cursor, user_email: str, model_name: str, project_name: str, 
                  new_model_name: str, new_project_name: str, new_user_email: str):
    
    old_model_id, old_model_path = get_model_id_and_path(cursor, model_name, project_name, user_email)
    if not old_model_id:
        raise Exception("Model not found in the old project")
    
    new_model_id, new_model_path = get_model_id_and_path(cursor, new_model_name, new_project_name, new_user_email)
    if new_model_id:
        raise Exception("Model already exists in the new project")
    
    template_name = cursor.execute(model_queries.get_template_name, (old_model_id,)).fetchone()[0]

    db_uid = str(uuid.uuid4())
    new_model_path = os.path.join(DATA_FOLDER, f"{db_uid}.sqlite3")
    if os.path.exists(new_model_path):
        raise Exception("Model with same UID already exists")
    
    new_project_id = get_project_id(cursor, new_user_email, new_project_name)
    if not new_project_id:
        raise Exception("New project not found")
    
    role = "owner"
    model_id = cursor.execute(model_queries.insert_models, (db_uid, new_model_name, new_user_email, template_name)).fetchone()[0]   
    cursor.execute(model_queries.insert_user_models, (model_id, new_user_email, new_project_id, role, new_model_name))
    
    if model_id:
        connection = apsw.Connection(old_model_path)
        connection.execute(f"VACUUM INTO '{new_model_path}'")
        connection.close()
        return 1
    raise Exception("Failed to create new model")

def rename_model(cursor, user_email: str, model_name: str, project_name: str, new_model_name: str):
    model_id, _ = get_model_id_and_path(cursor, model_name, project_name, user_email)
    if not model_id:
        raise Exception("Model not found")
    
    existing_model_id, _ = get_model_id_and_path(cursor, new_model_name, project_name, user_email)
    if existing_model_id:
        raise Exception("Model with the new name already exists")
    
    cursor.execute(model_queries.rename_model, (new_model_name, model_id, user_email))
    return 1

def delete_model(cursor, user_email: str, model_name: str, project_name: str):
    model_id, model_path = get_model_id_and_path(cursor, model_name, project_name, user_email)
    if not model_id:
        raise Exception("Model not found")
    
    access_level = cursor.execute(model_queries.get_access_level, (model_id, user_email)).fetchone()[0]
    if access_level != "owner":
        cursor.execute(model_queries.delete_user_model, (model_id, user_email))
        return 1

    cursor.execute(model_queries.delete_model_for_all_users, (model_id, model_id))

    if os.path.exists(model_path):
        os.remove(model_path)

    all_backups = cursor.execute(model_queries.get_model_backups, (model_id,)).fetchall()
    for backup in all_backups:
        backup_path = backup[0]
        if os.path.exists(backup_path):
            os.remove(backup_path)
    cursor.execute(model_queries.delete_model_backup, (model_id, 'NA'))
    
    return 1

def create_model_backup(cursor, user_email: str, model_name: str, project_name: str):
    model_id, model_path = get_model_id_and_path(cursor, model_name, project_name, user_email)
    if not model_id:
        raise Exception("Model not found")
    
    access_level = cursor.execute(model_queries.get_access_level, (model_id, user_email)).fetchone()[0]
    
    if access_level != "owner":
        raise Exception("Only owner can create backup")
    
    all_backups = cursor.execute(model_queries.get_model_backups, (model_id,)).fetchall()

    if len(all_backups) >= MAX_BACKUPS:
        oldest_backup_path = all_backups[0][0]
        if os.path.exists(oldest_backup_path):
            os.remove(oldest_backup_path)
        cursor.execute(model_queries.delete_model_backup, ('NA', oldest_backup_path))


    
    backup_uid = str(uuid.uuid4())
    backup_path = os.path.join(BACKUP_FOLDER, f"{backup_uid}.sqlite3")
    if os.path.exists(backup_path):
        raise Exception("Backup with same UID already exists")
    
    connection = apsw.Connection(model_path)
    connection.execute(f"VACUUM INTO '{backup_path}'")
    connection.close()

    cursor.execute("INSERT INTO S_ModelBackups (ModelId, BackupPath) VALUES (?, ?)", (model_id, backup_path))

def get_model_backups(cursor, user_email: str, model_name: str, project_name: str):
    model_id, _ = get_model_id_and_path(cursor, model_name, project_name, user_email)
    if not model_id:
        raise Exception("Model not found")
    
    access_level = cursor.execute(model_queries.get_access_level, (model_id, user_email)).fetchone()[0]
    
    if access_level != "owner":
        raise Exception("Only owner can get backups")
    
    all_backups = cursor.execute(model_queries.get_model_backup_details, (model_id,)).fetchall()
    
    return all_backups

def restore_model_from_backup(cursor, user_email: str, model_name: str, project_name: str, backup_id: str):
    model_id, model_path = get_model_id_and_path(cursor, model_name, project_name, user_email)
    if not model_id:
        raise Exception("Model not found")
    
    access_level = cursor.execute(model_queries.get_access_level, (model_id, user_email)).fetchone()[0]
    
    if access_level != "owner":
        raise Exception("Only owner can restore from backup")
    
    backup_row = cursor.execute(model_queries.get_model_backup_path, (backup_id,)).fetchone()
    if not backup_row:
        raise Exception("Backup not found")
    
    backup_path = backup_row[0]

    if not os.path.exists(backup_path):
        raise Exception("Backup file not found on disk")

    backup_connection = apsw.Connection(backup_path)

    this_connection = apsw.Connection(model_path)

    with this_connection.backup("main", backup_connection, "main") as backup:
            backup.step()  # copy entire database in one step

    this_connection.close()
    backup_connection.close()

def share_model(cursor, from_user_email: str, to_user_email: str, model_name: str, project_name: str, 
                access_level: str):
    model_id, model_path = get_model_id_and_path(cursor, model_name, project_name, from_user_email)
    if not model_id:
        raise Exception("Model not found")
    
    from_user_access_level = cursor.execute(model_queries.get_access_level, (model_id, from_user_email)).fetchone()[0]
    
    if from_user_access_level != "owner":
        raise Exception("Only owner can share the model")
    
    notification_data = {model_id: model_id, model_name: model_name, 
                            project_name: project_name, access_level: access_level}
    title = "Model Share Request"
    message = f"{from_user_email} wants to share the model '{model_name}' in project '{project_name}' with you. Do you accept?"
    notification_type = "model_share_request"
    notifications = cursor.execute(model_queries.add_user_notifications, (from_user_email, to_user_email, title, message, 
                                                          notification_type, json.dumps(notification_data))).fetchone()
    if not notifications:
        raise Exception("Failed to create notification for model share")
    
def read_notification(cursor, notification_id: int, user_email: str):
    cursor.execute(model_queries.read_notification, (notification_id, user_email))

def accept_model_share(cursor, notification_id: int, new_model_name: str, new_project_name: str, 
                       user_email: str, accept: bool, create_copy: bool = False):
    notification_row = cursor.execute(model_queries.get_notification_params, (notification_id, user_email)).fetchone()
    if not notification_row:
        raise Exception("Notification not found")
    
    to_user_email = user_email
    from_user_email = notification_row[0]
    notification_params = json.loads(notification_row[1])
    model_id = notification_params.get("model_id")
    model_name = notification_params.get("model_name")
    project_name = notification_params.get("project_name")
    access_level = notification_params.get("access_level")

    old_model_id, _ = get_model_id_and_path(cursor, model_name, project_name, from_user_email)

    if not old_model_id:
        raise Exception("Model not found for sharing")
    
    if old_model_id != model_id:
        raise Exception("Model ID mismatch")

    if accept:
        if create_copy:
            save_as_model(cursor, from_user_email, model_name, project_name, 
                          new_model_name, new_project_name, user_email)
        else:
            project_id = get_project_id(cursor, user_email, new_project_name)
            if not project_id:
                raise Exception("Project not found for user")
            new_model_id, _ = get_model_id_and_path(cursor, new_model_name, new_project_name, to_user_email)
            if new_model_id:
                raise Exception("User already has a model with the same name in the project")
            cursor.execute(model_queries.insert_user_models, (model_id, to_user_email, project_id, access_level, 
                                                              new_model_name))
        cursor.execute(model_queries.accept_notification, (1, notification_id, user_email))
    else:
        # If user rejects the share request, we can optionally delete the notification or mark it as rejected. For now, we will just mark it as read.
        cursor.execute(model_queries.accept_notification, (0, notification_id, user_email))