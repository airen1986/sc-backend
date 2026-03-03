get_project_id = "SELECT ProjectId FROM S_Projects WHERE UserEmail=? AND ProjectName=?"

insert_new_project = " INSERT INTO S_Projects (UserEmail, ProjectName) VALUES (?, ?) RETURNING ProjectId"

get_current_project = "SELECT ProjectName FROM S_Projects WHERE UserEmail=? AND Status='active'"


set_project_status = """ UPDATE S_Projects SET Status=NULL WHERE UserEmail=?;
                        UPDATE S_Projects SET Status='active' WHERE UserEmail=? AND ProjectName=? """

get_project_models = """SELECT S_UserModels.ModelName
                        FROM S_UserModels, S_Projects
                        WHERE S_UserModels.ProjectId = S_Projects.ProjectId
                        AND S_Projects.UserEmail = S_UserModels.UserId
                        AND S_Projects.UserEmail = ?
                        AND S_Projects.ProjectName = ?"""

delete_project = "DELETE FROM S_Projects WHERE UserEmail=? AND ProjectName=?"