# DB Lab 3 

## 1. Student
Gasser ibrahim shalaby  2304106  
Seif El-Din Amr Abd El-Fattah 2304205 


## 2. Technology
- **Back end:** Python 3 + Flask, PyMySQL , bcrypt, python-dotenv
- **Front end:** Jinja templates, plain HTML / CSS / JavaScript
- **Database:** MySQL. Three databases: `company` (Problem 1), `library` (Problem 2) and `registration` .

## 3. How to run it, step by step
1. Install **Python 3.10+**, **MySQL Server** and **Git**.
2. Clone the repository and enter it: `git clone <url>` then `cd <folder>`.
3. Build the databases with the MySQL client:
   ```
   mysql -u root -p < problem1_DDL.sql
   mysql -u root -p < problem1_DML.sql
   mysql -u root -p < problem2_DDL.sql
   mysql -u root -p < problem2_DML.sql
   mysql -u root -p < website/database/reigister.sql
   ```
   Every DDL script starts with `DROP DATABASE IF EXISTS ...`, so they can be re-run at any time.
   To look at Problem 1 by hand: `mysql -u root -p company`.
   *(With MySQL Workbench: File → Open SQL Script, then press the ⚡ button, for each file in the same order.)*
4. Prepare the website:
   ```
   open VS code then click on file select open folder and select folder books and authors
   cd website
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  #if error happened use it 
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` (Windows: `copy .env.example .env`) and write your MySQL password and any long random text as `SECRET_KEY`. `DB_NAME=registration` and `DB_LIBRARY=library` stay as they are.
6. Start the server: `python app.py`
7. Open <http://localhost:5000>. The site is private, so **register an account first**, then use the menu: **To-Do**, **Books**, **Authors**.

## 4. Features
**Problem 2 – new pages (F2.1 – F2.5)**
- **F2.1 Show:** the *Books* page shows the table of books (with the `author_id` of each book, and the author's name next to it); the *Authors* page shows the table of authors.
- **F2.2 Add:** a form at the top of each page adds a book (title, price, author chosen from a list) or an author (name, country).
- **F2.3 Edit:** the *Edit* button of each row opens a form with the current values.
- **F2.4 Remove a book** and **F2.5 remove an author**, both after an "Are you sure?" question. Removing an author also removes all its books (`ON DELETE CASCADE` in the DDL).
- Inputs are checked in the browser (`static/app.js`) and again on the server (`app.py`). If the server finds an error it shows the same page with the messages and does not touch the database. A book for an author that does not exist is refused by the foreign key and shown as "This author does not exist".

**Bonus – images for books and authors**
- Each book can have a **cover** and each author a **photo** (new column `book.cover` and `author.photo`, both `NULL` when there is no image).
- The *Add* forms have an optional file field; the *Edit* pages show the current image, let you **replace** it, or **remove** it with a checkbox. The tables show a small thumbnail.

**From Lab 2 (still there):** register, login / logout, private to-do list (add, edit, done, delete), bcrypt hashes, light / dark button, filters and counter of open to-dos.

## 5. Problem 1 
The full SQL and outputs are in `problem1_Answers.txt`.

