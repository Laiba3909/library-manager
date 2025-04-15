import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

st.set_page_config(page_title="Library Manager", layout="wide")

if 'db' not in st.session_state:
    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": st.secrets["FIREBASE_TYPE"],
            "project_id": st.secrets["FIREBASE_PROJECT_ID"],
            "private_key_id": st.secrets["FIREBASE_PRIVATE_KEY_ID"],
            "private_key": st.secrets["FIREBASE_PRIVATE_KEY"],
            "client_email": st.secrets["FIREBASE_CLIENT_EMAIL"],
            "client_id": st.secrets["FIREBASE_CLIENT_ID"],
            "auth_uri": st.secrets["FIREBASE_AUTH_URI"],
            "token_uri": st.secrets["FIREBASE_TOKEN_URI"],
            "auth_provider_x509_cert_url": st.secrets["FIREBASE_AUTH_PROVIDER_X509_CERT_URL"],
            "client_x509_cert_url": st.secrets["FIREBASE_CLIENT_X509_CERT_URL"],
        })
        firebase_admin.initialize_app(cred)
    st.session_state.db = firestore.client()

db = st.session_state.db

def add_book(book_name):
    db.collection("books").add({"title": book_name})

def get_books():
    books = db.collection("books").stream()
    books_list = []
    
    for book in books:
        book_data = book.to_dict()
        
        if "title" not in book_data:
            book.reference.update({"title": "Untitled Book"})
            st.warning(f"Book document with ID {book.id} was missing a title field. Added 'Untitled Book'.")
            book_data["title"] = "Untitled Book"
        
        books_list.append(book_data["title"])
    
    return books_list

def update_book(old_name, new_name):
    docs = db.collection("books").where("title", "==", old_name).stream()
    for doc in docs:
        doc.reference.update({"title": new_name})

def delete_book(book_name):
    docs = db.collection("books").where("title", "==", book_name).stream()
    for doc in docs:
        doc.reference.delete()

st.title("Library Manager 📚")
st.divider()

menu = st.sidebar.radio("Choose an action", ["Add Book", "View Books", "Update Book", "Delete Book"])

if menu == "Add Book":
    book_name = st.text_input("Enter the book name:")
    if st.button("Add Book"):
        if book_name:
            add_book(book_name)
            st.success(f"Book '{book_name}' added!")
        else:
            st.warning("Please enter a book name.")

elif menu == "View Books":
    books = get_books()
    if books:
        st.write("Books in Library:")
        for book in books:
            st.markdown(f"- {book}")
    else:
        st.warning("No books available.")

elif menu == "Update Book":
    books = get_books()
    if books:
        old_name = st.selectbox("Select a book to update", books)
        new_name = st.text_input("New Book Name", value=old_name)
        if st.button("Update Book"):
            if new_name and new_name != old_name:
                update_book(old_name, new_name)
                st.success(f"Book updated: '{old_name}' to '{new_name}'")
            elif new_name == old_name:
                st.warning("New name can't be the same as the old name.")
    else:
        st.warning("No books to update.")

elif menu == "Delete Book":
    books = get_books()
    if books:
        book_to_delete = st.selectbox("Select a book to delete", books)
        if st.button("Delete Book"):
            delete_book(book_to_delete)
            st.success(f"Book '{book_to_delete}' deleted!")
    else:
        st.warning("No books to delete.")
