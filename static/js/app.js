document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const resultContainer = document.getElementById('result-container');
    const booksContainer = document.getElementById('books-container');

    // Load all books on page load
    fetch('/api/books')
        .then(response => response.json())
        .then(books => {
            displayBooks(books);
        });

    searchButton.addEventListener('click', () => {
        const title = searchInput.value;
        if (title) {
            fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title: title }),
            })
                .then(response => response.json())
                .then(book => {
                    if (book.error) {
                        resultContainer.innerHTML = `<p>${book.error}</p>`;
                    } else {
                        resultContainer.innerHTML = createBookHTML(book);
                    }
                });
        }
    });

    function displayBooks(books) {
        booksContainer.innerHTML = books.map(book => createBookHTML(book)).join('');
    }

    function createBookHTML(book) {
        return `
            <div class="book">
                <img src="${book.image}" alt="${book.title}">
                <h3>${book.title}</h3>
                <a href="${book.link}" target="_blank">Download</a>
            </div>
        `;
    }
});