import streamlit as st
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from langchain_community.embeddings import HuggingFaceEmbeddings


def ends_with_subdomain(email, subdomains):
    for subdomain in subdomains:
        if email.endswith(subdomain):
            return True
    return False


def get_text_from_google_doc(doc_id, headers):
    response = requests.get(
        f"https://docs.googleapis.com/v1/documents/{doc_id}",
        headers=headers,
    )
    if response.status_code == 200:
        document = response.json()
        text_content = ""
        for element in document["body"]["content"]:
            if "paragraph" in element:
                for paragraph in element["paragraph"]["elements"]:
                    if "textRun" in paragraph:
                        text = paragraph["textRun"]["content"].strip()
                        if text:  # Check if the text is not empty after stripping
                            text_content += text + " "
                    elif "inlineObjectElement" in paragraph:
                        # Handle inline objects if needed
                        pass
            elif "table" in element:
                table = element["table"]
                for row in table["tableRows"]:
                    for cell in row["tableCells"]:
                        for content in cell["content"]:
                            if "paragraph" in content:
                                for paragraph in content["paragraph"]["elements"]:
                                    if "textRun" in paragraph:
                                        text = paragraph["textRun"]["content"].strip()
                                        if (
                                            text
                                        ):  # Check if the text is not empty after stripping
                                            text_content += text + " "
                                    elif "inlineObjectElement" in paragraph:
                                        # Handle inline objects if needed
                                        pass
        return text_content
    else:
        print("Failed to fetch document:", response.status_code)
        return None


def get_drive_service(access_token, refresh_token):
    credentials = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://www.googleapis.com/oauth2/v3/token",
        client_id=st.secrets["oauth"]["client_id"],
        client_secret=st.secrets["oauth"]["client_secret"],
    )
    # Build the Drive service using the access token
    service = build("drive", "v3", credentials=credentials)
    return service


def list_files_in_folder(folder_id, access_token, refresh_token):
    # Get the Drive service
    drive_service = get_drive_service(access_token, refresh_token)

    # Call the Drive API to fetch files in the folder
    results = (
        drive_service.files()
        .list(
            q=f"'{folder_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.document'",
            fields="files(id, name)",
        )
        .execute()
    )

    files = results.get("files", [])
    if not files:
        return None
    else:
        return [file["id"] for file in files]


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


def update_vector_store(text_chunks, name):
    # sentence transformers to be used in vector store
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/msmarco-distilbert-base-v4",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": False},
    )
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local(name)


def get_conversational_chain():
    prompt_template = """
    You’re an HR specialist at a multinational tech company known for your exceptional ability to handle queries of employees regarding technical, work policies, and any other aspect within the company. Your expertise lies in providing clear and concise responses that address concerns effectively, fostering a positive work environment.
    Your task is to assist employees with their queries by providing detailed and informative responses. Address technical issues, work policies, and any other inquiries they may have to ensure a smooth and productive work environment.
    Please keep in mind the importance of maintaining confidentiality when addressing specific technical issues or personal inquiries. Be empathetic in your responses and strive to provide valuable assistance to all employees seeking clarification on various aspects within the company.
    For example, if an employee asks about the company's remote work policy, you could respond by outlining the guidelines set by the company and providing tips for effectively working from home. Additionally, if an employee seeks technical assistance with a software tool, you could offer step-by-step instructions on how to troubleshoot the issue.  \n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
    )
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain


def query_db(user_question, name):
    # embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/msmarco-distilbert-base-v4",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": False},
    )

    new_db = FAISS.load_local(name, embeddings)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain(
        {"input_documents": docs, "question": user_question}, return_only_outputs=True
    )

    # print("response", response)
    get_user_chat(user_question, response["output_text"])
    # st.write("Reply: ", response["output_text"])


def get_user_chat(input, output):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if input:
        # Display user message in chat message container
        st.chat_message("user").markdown(input)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": input})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(output)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": output})
