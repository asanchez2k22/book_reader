import streamlit as st
from pyzbar import pyzbar
import requests
import cv2
import numpy as np
import time
import matplotlib.image as mpimg



# Enable Testing
test_mode = False


def extract_barcode(frame):
    code = pyzbar.decode(frame)

    if code:
        for obj in code:
            if obj:
                isbn = obj.data.decode('utf-8')
            else:
                isbn = ""
    else:
        isbn = ""

    return isbn


def camera_capture():
    video = cv2.VideoCapture(0)
    video.set(3, 640)
    video.set(4, 480)
    time.sleep(1)

    isbn = ""

    # Distinguish between web-app and local app for testing
    if test_mode:
        while True:
            # Frame capturing
            success, frame = video.read()

            # Start processing the frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Display the image
            cv2.imshow('Testing-code-scan', frame)
            key = cv2.waitKey(1)

            if key == ord('q'):
                break

            isbn = extract_barcode(frame)

            if isbn != "":
                break

    else:
        while video.isOpened() and not stop_button_pressed:
            # Frame capturing
            success, frame = video.read()

            if not success:
                st.write("Video capture ended")
                break

            # Start processing the frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame, channels="RGB")

            key = cv2.waitKey(1)

            if key == ord("q") or stop_button_pressed:
                break

            isbn = extract_barcode(frame)

            if isbn != "":
                st.success("Barcode identified")
                break

    video.release()
    cv2.destroyAllWindows()

    return isbn


def load_image():
    # Distinguish between web-app and local app for testing
    if test_mode:
        # Load image
        image = mpimg.imread('test_barcode.png')

        # Extract isbn
        isbn = extract_barcode(image)

    else:
        up_file = st.file_uploader("Upload a barcode image", type=['png', 'jpg', 'jpeg'])

        if up_file:
            image = mpimg.imread(up_file)
            st.image(image, caption="Uploaded image", use_column_width=True)

            # Extract isbn
            isbn = extract_barcode(image)

    return isbn


def fetch_book_info(isbn, book_db):
    # Different book databases available
    # Google Database
    if book_db == "Google":
        GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
        response = requests.get(f"{GOOGLE_BOOKS_API}{isbn}")

        if response.status_code == 200:
            data = response.json()

            if "items" in data:
                return data["items"][0]['volumeInfo']

        return None

    # Open Library Database
    elif book_db == "OpenLibrary":
        count = 0
        """Fetches book information from Open Library."""
        url = f"http://openlibrary.org/api/volumes/brief/isbn/{isbn}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            if "records" in data:
                records = data.get('records', {})

                for record_key in records:
                    count += 1
                    record_data = records[record_key]

                    if count == 1:
                        return record_data
        return None


def store_data():
    return None


def filter_book_info(book_info, API):
    if API == "Google":
        title = book_info.get('title', 'N/A')
        author = book_info.get('authors', 'N/A')
    elif API == "OpenLibrary":
        title = book_info.get('data').get('title')
        author_data = book_info.get('data').get('authors')
        author = [author.get('name') for author in author_data]

    return title, author


# Main code
if test_mode:
    API = "OpenLibrary"
    source = "Camera"

    if source == "Camera":
        isbn = camera_capture()
    else:
        isbn = load_image()

    book_info = fetch_book_info(isbn, API)

    title, author = filter_book_info(book_info)

else:
    start_button_pressed = st.button("Start")

    if start_button_pressed:
        st.title("Book scanner")

        input_op = st.radio("Choose Input Method: ", ("Camera", "Load image"))
        book_API = st.radio("Choose book search API: ", ("Google", "OpenLibrary"))

        if input_op == "Camera":
            st.write("Please scan the barcode using your camera")
            frame_placeholder = st.empty()
            stop_button_pressed = st.button("Stop")

            isbn = camera_capture()

        if isbn != "":
            book_info = fetch_book_info(isbn, book_API)
            title, author = filter_book_info(book_info, book_API)

            st.write(f"Title: {title}")
            st.write(f"Author: {', '.join(author)}")

            print(f"Title: {title}")
            print(f"Author: {', '.join(author)}")

exit()

if "isbn" not in st.session_state:
    st.session_state.isbn = ""

if start_button_pressed:
    # Start infinite loop to capture video and look for barcode

    st.title("Escáner de libros")

    start_button_pressed = st.button("Scan")
    frame_placeholder = st.empty()
    stop_button_pressed = st.button("Stop")

    st.write("Fetching book information...")

    book_info = fetch_book_info(isbn)

    print(book_info)

    if book_info:
        st.write("### Book details")
        st.write(f"**Title:** {book_info.get('title', 'N/A')}")
        st.write(f"**Authors:** {', '.join(book_info.get('authors', 'N/A'))}")
        st.write(f"**Publisher:** {book_info.get('publisher', 'N/A')}")
        st.write(f"**Published Date:** {book_info.get('publishedDate', 'N/A')}")
        st.write(f"**Description:** {book_info.get('description', 'N/A')}")
    else:
        st.error("Book information not found.")
