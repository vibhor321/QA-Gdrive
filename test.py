from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os.path
import streamlit as st
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from utils.helpers import (
    get_text_from_google_doc,
    list_files_in_folder,
    get_text_from_google_doc,
)


# def get_drive_service(access_token):
#     credentials = Credentials(
#         token="ya29.a0AfB_byBN4T5sxu662hHuGVastgOMQDzYn_8s1XRYfY_mHSNj9Jz1PItVbYHk79a3QVbpPnd7-sCkrPFd38MUDh19n0Wleuj-uMfAu-JBQGpuU-c02oOdJ4QI5z6A1HLqtcnhE3h2V2Ov2RhYk6Qb7Z583pToszAnTIXEaCgYKAQwSARMSFQHGX2Mieer51PjnAiD1CHAwGnzdPA0171",
#         refresh_token="1//0gp_ClumnL5lvCgYIARAAGBASNwF-L9Ir6wXAnKZ_VzTfXS-EUWsv1L3EPpRjE74zYII3VdzhEclYp3v2Y-lZ0RiYT4sy-8CbFk4",
#         token_uri="https://www.googleapis.com/oauth2/v3/token",
#         client_id=st.secrets["oauth"]["client_id"],
#         client_secret=st.secrets["oauth"]["client_secret"],
#     )
#     # Build the Drive service using the access token
#     service = build("drive", "v3", credentials=credentials)
#     print("service---", service)
#     # Set the access token in the request headers
#     # service._http.headers["Authorization"] = f"Bearer {access_token}"
#     return service


# def list_files_in_folder(folder_id, access_token):
#     # Get the Drive service
#     drive_service = get_drive_service(access_token)

#     # Call the Drive API to list files in the folder
#     results = (
#         drive_service.files()
#         .list(q=f"'{folder_id}' in parents and trashed=false", fields="files(id, name)")
#         .execute()
#     )

#     # Extract and print file names and IDs
#     files = results.get("files", [])
#     if not files:
#         print("No files found.")
#     else:
#         print("Files:")
#         for file in files:
#             print(f"{file['name']} ({file['id']})")


# Example usage

# list_files_in_folder(
#     "1c6Am2xJs_i74p2MD7K0kbNFxrGXNuK5r",
#     "ya29.a0AfB_byBN4T5sxu662hHuGVastgOMQDzYn_8s1XRYfY_mHSNj9Jz1PItVbYHk79a3QVbpPnd7-sCkrPFd38MUDh19n0Wleuj-uMfAu-JBQGpuU-c02oOdJ4QI5z6A1HLqtcnhE3h2V2Ov2RhYk6Qb7Z583pToszAnTIXEaCgYKAQwSARMSFQHGX2Mieer51PjnAiD1CHAwGnzdPA0171",
# )


def test():
    id = "1FJmBMJbiSbqRIpFg1DUeDBgReToRV5Iv"
    token = "ya29.a0AfB_byDDlH2np1biGLL8lRoSj0lsFGQgxUovyI6ivGbg_M3z5jPSlmZD5aK3YVAj9mGMpad93Cfm0OBlk1K3udw8xVjTztm_eLOg2S5q0PE-8vUnel_avA-g8GridaAt0Kpc2isNey14tj-OABi8ufU9hadTCMI-Gj-UaCgYKAcYSARMSFQHGX2MieDJ9lA5oNb58R1SA05y7Bw0171"
    access_token = "1//0gYjh0WhYTvmBCgYIARAAGBASNwF-L9IrqNVZsKW2IEQIsHEDecBjOZwi1-gGRicVHWnXv9lxLowvrG27zPoNmrQ5pbGjvvn64rg"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    # print(list_files_in_folder(id, token, access_token))
    print(
        get_text_from_google_doc(
            "1eDFhyiLdB5dF0UhTG8ikD6oj2bXcrAZovPWGmaTnJdc", headers
        )
    )


test()
