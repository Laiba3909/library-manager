import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

st.set_page_config(page_title="📚 Library Manager", layout="wide")

if 'db' not in st.session_state:
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
            st.session_state.db = firestore.client()
            st.success("Firebase Initialized Successfully!")
        else:
            st.session_state.db = firestore.client()
            st.success("Firebase already initialized!")
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")

def add_book(book_name):
    if 'db' not in st.session_state:
        st.error("Firebase not initialized!")
        return
    doc_ref = st.session_state.db.collection("books").document(book_name)
    doc_ref.set({"name": book_name})

def get_books():
    if 'db' not in st.session_state:
        st.error("Firebase not initialized!")
        return []
    books = st.session_state.db.collection("books").stream()
    return [doc.to_dict()["name"] for doc in books]

def update_book(old_name, new_name):
    if 'db' not in st.session_state:
        st.error("Firebase not initialized!")
        return
    doc_ref = st.session_state.db.collection("books").document(old_name)
    doc = doc_ref.get()

    if doc.exists:
        doc_ref.update({"name": new_name})
    else:
        st.error(f"Book '{old_name}' does not exist anymore.")

def delete_book(book_name):
    if 'db' not in st.session_state:
        st.error("Firebase not initialized!")
        return
    doc_ref = st.session_state.db.collection("books").document(book_name)
    doc_ref.delete()

st.markdown("""
    <style>
    .main {
        background-color: #f4f4f9;
        font-family: 'Arial', sans-serif;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #41228e;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #deab7f;
    }
    .sidebar .sidebar-content {
        background-color: #41228e;
        color: white;
    }
    h1 {
        color: #41228e;
        font-size: 2.5rem;
        font-weight: bold;
    }
    h3, h5 {
        color: #41228e;
    }
    .stSelectbox {
        background-color: #deab7f;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📚 Firebase Book Library")
st.markdown("<hr>", unsafe_allow_html=True)

menu = st.sidebar.radio("Choose Action", ["Add Book", "Search Book", "Edit Book", "Delete Book"])

if menu == "Add Book":
    st.subheader("Add a New Book")
    book = st.text_input("Book Name")
    if st.button("Add Book"):
        if book:
            add_book(book)
            st.success(f"Successfully added: {book}")
            st.rerun()
        else:
            st.warning("Please enter a book name.")

elif menu == "Search Book":
    st.subheader("Books Available in Library:")
    books = get_books()
    if books:
        for book in books:
            st.markdown(f"- {book}")
    else:
        st.warning("No books found in the library.")

elif menu == "Edit Book":
    st.subheader("Edit an Existing Book")
    books = get_books()
    if books:
        selected_book = st.selectbox("Choose a Book to Edit", books)
        new_name = st.text_input("Enter New Name for the Book", value=selected_book)
        if st.button("Update Book"):
            if new_name and new_name != selected_book:
                update_book(selected_book, new_name)
                st.success(f"Successfully updated: {selected_book} to {new_name}")
                st.rerun()
            elif new_name == selected_book:
                st.warning("New name cannot be the same as the old name.")
    else:
        st.warning("No books found to edit.")

elif menu == "Delete Book":
    st.subheader("Delete a Book")
    books = get_books()
    if books:
        selected_book = st.selectbox("Choose a Book to Delete", books)
        if st.button("Delete Book"):
            delete_book(selected_book)
            st.success(f"Successfully deleted: {selected_book}")
            st.rerun()
    else:
        st.warning("No books found to delete.")
