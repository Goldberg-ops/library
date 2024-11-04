# Web Application Project

## Description

This is a Flask-based digital library web application that allows users to browse and search for books. It utilizes a SQLite database for data storage, serves static files, and uses HTML templates for rendering pages. The application features a paginated home page displaying books, book categorization, search functionality, and individual book result pages.

## Project Structure
- `application.py`: Main entry point of the application
- `book.sqlite`: SQLite database file
- `requirements.txt`: List of Python package dependencies
- `startup.txt`: Initial setup or configuration file
- `static/`: Directory containing static files (CSS, JavaScript)
- `templates/`: Directory containing HTML templates

## Setup and Installation

1. Clone the repository:
   - ```shell
     git clone https://github.com/Goldberg-ops/library.git
   - ```
     cd libray-master

3. Create and activate a virtual environment:
   - `python -m venv venv`
   - `source venv/bin/activate`  # On Windows, use venv\Scripts\activate

4. Install the required packages:
   - `pip install -r requirements.txt`

5. Set up the database:
(Include instructions for initializing the SQLite database if necessary)

6. Run the application:
   `python application.py`

## Usage
After running the application, you can access it by opening a web browser and navigating to `http://127.0.0.1:5000` (or whichever port your application is configured to use).

- Home page: View a paginated list of books
- Search: Use the search functionality to find specific books
- Book details: Click on a book to view its detailed information

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
