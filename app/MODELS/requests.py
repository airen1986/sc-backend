from fastapi import APIRouter, Response, Depends, UploadFile, File
from .methods import Models_database
from app.PROJECTS.modals import *
from app.CORE.utility import *
from app.CORE.DB import with_master_cursor
from app.SCHEMA.schema_info import schema_info
from .models import *
from fastapi.responses import FileResponse

Model_router = APIRouter(prefix="/models")

# make all endpoint requests as camel case, to be consistent with frontend. 
# Also, make the function names consistent with the endpoint names. 
# Either both should have _ or both should be camel case. 

@Model_router.post("/user_templates")
def get_user_templates( #change name - DONE
    response: Response,
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):

    schema_list = Models_database.get_user_templates(cursor=cursor)

    return {
        "schemas": schema_list
    }

@Model_router.post("/add_new_model")
def add_new_model(
    payload: AddNewModelPayload,  #to be changed to AddNewModelPayload - DONE
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.add_new_model(
        cursor=cursor,
        payload=payload,
        owner_email=email
    )

    

@Model_router.post("/add_existing_model")
def add_existing_model(
    payload: AddExistingModelPayload, #to be changed to AddExistingModelPayload - DONE
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.add_existing_model(
        cursor=cursor,
        payload=payload,
        owner_email=email
    )
    
    


@Model_router.post("/get_user_models")
def get_user_models(
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.get_user_models(
        cursor=cursor,
        user_email=email
    )
    
    

@Model_router.post("/get_user_models_by_project")
def get_user_models_by_project(
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.get_user_models_by_project(
        cursor=cursor,
        user_email=email
    )
    
    

@Model_router.post("/save_as_model")
def save_as_model(
    payload: SaveAsModelPayload, #payload - DONE
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.save_as_model(
        cursor=cursor,
        payload=payload,
        owner_email=email
    )



#
@Model_router.post("/rename_model")
def rename_model(
    payload: RenameModelPayload, #payload - DONE
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.rename_model(
        cursor=cursor,
        payload=payload,
        owner_email=email
    )



@Model_router.post("/delete_model")
def delete_model(
    payload: DeleteModelPayload, #payload - DONE
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.delete_model(
        cursor=cursor,
        payload=payload,
        owner_email=email
    )



@Model_router.post("/move_model_to_project") #to be changed to /move_model_to_project - DONE
def move_model_to_project(
    payload: MoveModelToProjectPayload,  #payload - DONE
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.move_model_to_project( 
        cursor=cursor,
        payload=payload,
        owner_email=email
    )


@Model_router.post("/download_model", response_class=FileResponse)
def download_model(
    payload: DownloadModelPayload, #payload - DONE
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.download_model(
        cursor=cursor,
        payload=payload,
        owner_email=email
    )



@Model_router.post("/upload_model") #to be changed to /upload_model - DONE
def upload_model(
    payload: UploadModelPayload = Depends(upload_payload),
    file: UploadFile = File(...),
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.upload_model(
        cursor=cursor,
        payload=payload,
        file=file,
        owner_email=email
    )


# Kahin per payload, kahin pe Model, thoda consistent karna hoga. Payload zyada sahi lagta h.



@Model_router.post("/backup_model") #to be changed to /backup_model - DONE
def Backup_Model(    #name changes?? Backup_MOdel - DONE
    payload: BackupModelPayload,
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):

    return Models_database.backup_model( #backup_model - DONE
        cursor=cursor,
        payload=payload,
        owner_email=email
    )


@Model_router.post("/restore_model") #to be changed to /restore_model - DONE
def restore_model( #restore_model - DONE
    payload: RestoreModelPayload,
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):

    return Models_database.restore_model( # to be changed to restore_model - DONE
        cursor=cursor,
        payload=payload,
        owner_email=email
    )    


@Model_router.post("/share_model") #to be changed to /share_model - DONE
def share_model(
    payload: ShareModelPayload,
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.share_model( #to be changed to share_model
        cursor=cursor,
        payload=payload,
        owner_email=email
    )


@Model_router.post("/get_notifications") #/get_notifications - DONE
def Get_Notifications(
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.Get_Notifications(
        cursor=cursor,
        owner_email=email
    )


@Model_router.post("/is_accepted") #/is_accepted - DONE
def is_share_model_request_accepted(
    payload: IsAcceptedModelPayload,
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.is_share_model_request_accepted(
        cursor=cursor,
        payload=payload,
        owner_email=email
    )   


@Model_router.post("/get_model_backups") #/get_model_backups - DONE
def get_model_backups(
    payload: ModelBackupPayload,
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.get_model_backups(
        payload= payload,
        cursor=cursor,
        owner_email=email
    )


@Model_router.post("/get_all_user_emails") #/get_all_user_emails - DONE
def get_model_backups(
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):
    return Models_database.get_all_user_emails(
        cursor=cursor,
        current_user_email=email
    )


#added
@Model_router.post("/reject_model_share") #/reject_model_share - DONE
def Reject_Request_For_Model_Share(
    payload: RejectModelSharePayload,
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):

    return Models_database.Reject_Request_For_Model_Share(
        payload= payload,
        cursor=cursor,
        current_user_email=email
    )
    

#added
@Model_router.post("/cancel_model_share") #/cancel_model_share - DONE
def Cancel_Request_For_Model_Share(
    payload: CancelModelSharePayload,
    email: str = Depends(get_current_user_email),
    cursor = Depends(with_master_cursor)
):

    return Models_database.Cancel_Request_For_Model_Share(
        payload= payload,
        cursor=cursor,
        current_user_email=email
    )
    