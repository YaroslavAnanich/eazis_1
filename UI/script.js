const HOST = "http://127.0.0.1:8000";

document.addEventListener('DOMContentLoaded', () => {
    const saveBtn = document.getElementById('save-btn');
    const loadBtn = document.getElementById('load-btn');
    const deleteBtn = document.getElementById('delete-btn');
    const clearBtn = document.getElementById('clear-btn');
    const processBtn = document.getElementById('process-btn');
    const addWordBtn = document.getElementById('add-word-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');
    const textInput = document.getElementById('text-input');
    const filenameInput = document.getElementById('filename-input');
    const dictionaryOutput = document.getElementById('dictionary-output');
    const dictionariesDropdown = document.getElementById('dictionaries-dropdown');
    const lemmaInput = document.getElementById('lemma-input');
    const wordFormInput = document.getElementById('word-form-input');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');

    let currentDictionary = null;

    // Load list of dictionaries when page loads
    loadDictionaryList();

    // Process text and create dictionary
    processBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!text) {
            alert('Please enter some text to analyze');
            return;
        }

        try {
            const response = await fetch(HOST + '/create-dictionary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                throw new Error('Failed to analyze text');
            }

            const data = await response.json();
            currentDictionary = data.dictionary;
            renderDictionary(currentDictionary);
        } catch (error) {
            console.error('Error:', error);
            alert('Error analyzing text: ' + error.message);
        }
    });

    // Handle file upload for dictionary creation
    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', async () => {
        const file = fileInput.files[0];
        if (!file) return;

        // Check file extension
        if (!file.name.toLowerCase().endsWith('.txt') && !file.name.toLowerCase().endsWith('.rtf')) {
            alert('Please upload a TXT or RTF file');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(HOST + '/create-dictionary-from-file', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create dictionary from file');
            }

            const data = await response.json();
            currentDictionary = data.dictionary;
            renderDictionary(currentDictionary);

            // Set the filename input to the uploaded file's name (without extension)
            filenameInput.value = file.name.replace(/\.[^/.]+$/, "");

            // Clear the file input
            fileInput.value = '';

            alert('Dictionary created successfully from file');
        } catch (error) {
            console.error('Error:', error);
            alert('Error creating dictionary from file: ' + error.message);
        }
    });

    // Save dictionary
    saveBtn.addEventListener('click', async () => {
        // Collect the current dictionary data from the DOM
        const updatedDictionary = collectDictionaryData();

        if (!updatedDictionary || Object.keys(updatedDictionary).length === 0) {
            alert('No dictionary content to save');
            return;
        }

        const filename = filenameInput.value.trim();
        if (!filename) {
            alert('Please enter a dictionary name');
            return;
        }

        try {
            const response = await fetch(HOST + '/save-dictionary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    dictionary: updatedDictionary,
                    file_name: filename
                })
            });

            if (!response.ok) {
                throw new Error('Failed to save dictionary');
            }

            const data = await response.json();
            alert(data.message);
            currentDictionary = updatedDictionary;
            // Refresh the dictionary list after saving
            loadDictionaryList();
        } catch (error) {
            console.error('Error:', error);
            alert('Error saving dictionary: ' + error.message);
        }
    });

    // Load selected dictionary
    loadBtn.addEventListener('click', async () => {
        const selectedFile = dictionariesDropdown.value;
        if (!selectedFile) {
            alert('Please select a dictionary to load');
            return;
        }

        try {
            const response = await fetch(`${HOST}/load-dictionary?file_path=${encodeURIComponent(selectedFile)}`);

            if (!response.ok) {
                throw new Error('Failed to load dictionary');
            }

            const data = await response.json();
            currentDictionary = data.dictionary;
            renderDictionary(currentDictionary);
            filenameInput.value = selectedFile.replace('.json', '');
        } catch (error) {
            console.error('Error:', error);
            alert('Error loading dictionary: ' + error.message);
        }
    });

    // Delete selected dictionary
    deleteBtn.addEventListener('click', async () => {
        const selectedFile = dictionariesDropdown.value;
        if (!selectedFile) {
            alert('Please select a dictionary to delete');
            return;
        }

        if (!confirm(`Are you sure you want to delete "${selectedFile}"? This action cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch(HOST + '/delete-dictionary', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    file_path: selectedFile
                })
            });

            if (!response.ok) {
                throw new Error('Failed to delete dictionary');
            }

            const data = await response.json();
            alert(data.message);

            // Clear the current view if we deleted the loaded dictionary
            if (currentDictionary && filenameInput.value === selectedFile.replace('.json', '')) {
                dictionaryOutput.innerHTML = '';
                textInput.value = '';
                filenameInput.value = '';
                currentDictionary = null;
            }

            // Refresh the dictionary list
            loadDictionaryList();
        } catch (error) {
            console.error('Error:', error);
            alert('Error deleting dictionary: ' + error.message);
        }
    });

    // Clear all
    clearBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all content?')) {
            dictionaryOutput.innerHTML = '';
            textInput.value = '';
            filenameInput.value = '';
            currentDictionary = null;
            searchInput.value = '';
        }
    });

    // Add new word form
    addWordBtn.addEventListener('click', async () => {
        const lemma = lemmaInput.value.trim();
        const wordForm = wordFormInput.value.trim();

        if (!lemma || !wordForm) {
            alert('Please enter both lemma and word form');
            return;
        }

        if (!currentDictionary) {
            alert('No dictionary loaded. Please create or load a dictionary first.');
            return;
        }

        try {
            const response = await fetch(HOST + '/add-word-form', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    dictionary: currentDictionary,
                    lemma: lemma,
                    word_form: wordForm
                })
            });

            if (!response.ok) {
                throw new Error('Failed to add word form');
            }

            const data = await response.json();
            currentDictionary = data.dictionary;
            renderDictionary(currentDictionary);

            // Clear the input fields
            lemmaInput.value = '';
            wordFormInput.value = '';

            alert('Word form added successfully');
        } catch (error) {
            console.error('Error:', error);
            alert('Error adding word form: ' + error.message);
        }
    });

    // Search dictionary
    searchBtn.addEventListener('click', () => {
        const searchTerm = searchInput.value.trim().toLowerCase();
        if (!searchTerm) {
            alert('Please enter a search term');
            return;
        }

        if (!currentDictionary) {
            alert('No dictionary loaded to search');
            return;
        }

        searchDictionary(searchTerm);
    });

    // Search on Enter key press
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });

    // Load list of available dictionaries
    async function loadDictionaryList() {
        try {
            const response = await fetch(HOST + '/list-dictionaries');

            if (!response.ok) {
                throw new Error('Failed to fetch dictionary list');
            }

            const data = await response.json();
            updateDictionaryList(data.dictionaries);
        } catch (error) {
            console.error('Error loading dictionary list:', error);
            alert('Error loading dictionary list: ' + error.message);
        }
    }

    // Update the dropdown with dictionary list
    function updateDictionaryList(dictionaries) {
        dictionariesDropdown.innerHTML = '<option value="">Select a dictionary</option>';

        dictionaries.forEach(file => {
            const option = document.createElement('option');
            option.value = file;
            option.textContent = file.replace('.json', '');
            dictionariesDropdown.appendChild(option);
        });
    }

    // Render dictionary to the DOM
    function renderDictionary(dictionary) {
        dictionaryOutput.innerHTML = '';

        if (typeof dictionary !== 'object') {
            dictionaryOutput.textContent = dictionary;
            return;
        }

        for (const [word, entries] of Object.entries(dictionary)) {
            entries.forEach((entry, index) => {
                const wordCard = document.createElement('div');
                wordCard.className = 'word-card';
                wordCard.dataset.word = word;
                wordCard.dataset.index = index;

                wordCard.innerHTML = `
                    <div class="word-header">
                        <span>${word}</span>
                        <span>${entry.tag} (${entry.tag_description})</span>
                    </div>
                    <div class="word-content">
                        <div class="detail-row">
                            <span class="detail-label">Word:</span>
                            <span class="detail-value editable-field" contenteditable="true" data-field="word">${entry.word}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Lemma:</span>
                            <span class="detail-value editable-field" contenteditable="true" data-field="lemma">${entry.lemma}</span>
                        </div>
                        <div class="morphemes-container">
                            <div class="morpheme">
                                <span class="morpheme-label">Prefix:</span>
                                <span class="editable-field" contenteditable="true" data-field="prefix">${entry.morphemes.prefix || '—'}</span>
                            </div>
                            <div class="morpheme">
                                <span class="morpheme-label">Root:</span>
                                <span class="editable-field" contenteditable="true" data-field="root">${entry.morphemes.root}</span>
                            </div>
                            <div class="morpheme">
                                <span class="morpheme-label">Suffix:</span>
                                <span class="editable-field" contenteditable="true" data-field="suffix">${entry.morphemes.suffix || '—'}</span>
                            </div>
                        </div>
                    </div>
                `;

                dictionaryOutput.appendChild(wordCard);
            });
        }
    }

    // Collect data from DOM to reconstruct dictionary
    function collectDictionaryData() {
        const dictionary = {};
        const wordCards = document.querySelectorAll('.word-card');

        wordCards.forEach(card => {
            try {
                const word = card.dataset.word;
                if (!word) return;

                if (!dictionary[word]) {
                    dictionary[word] = [];
                }

                const wordElement = card.querySelector('[data-field="word"]');
                const lemmaElement = card.querySelector('[data-field="lemma"]');
                const headerElement = card.querySelector('.word-header span:last-child');
                const prefixElement = card.querySelector('[data-field="prefix"]');
                const rootElement = card.querySelector('[data-field="root"]');
                const suffixElement = card.querySelector('[data-field="suffix"]');

                if (!wordElement || !lemmaElement || !headerElement ||
                    !prefixElement || !rootElement || !suffixElement) {
                    return;
                }

                const tagMatch = headerElement.textContent.match(/^([^\s]+)/);
                const descMatch = headerElement.textContent.match(/\((.*?)\)/);

                const entry = {
                    word: wordElement.textContent,
                    lemma: lemmaElement.textContent,
                    tag: tagMatch ? tagMatch[1] : '',
                    tag_description: descMatch ? descMatch[1] : '',
                    morphemes: {
                        prefix: prefixElement.textContent.replace('—', '').trim() || null,
                        root: rootElement.textContent.trim(),
                        suffix: suffixElement.textContent.replace('—', '').trim() || null
                    }
                };

                dictionary[word].push(entry);
            } catch (error) {
                console.error('Error processing word card:', error);
            }
        });

        return dictionary;
    }

    // Search through dictionary content
    function searchDictionary(searchTerm) {
        // First remove any existing highlights
        const highlightedElements = document.querySelectorAll('.highlight');
        highlightedElements.forEach(el => {
            el.classList.remove('highlight');
            const parent = el.parentElement;
            parent.replaceChild(document.createTextNode(el.textContent), el);
        });

        if (!searchTerm) return;

        // Search through the dictionary content
        const wordCards = document.querySelectorAll('.word-card');
        let found = false;

        wordCards.forEach(card => {
            const word = card.dataset.word.toLowerCase();
            const wordField = card.querySelector('[data-field="word"]').textContent.toLowerCase();
            const lemma = card.querySelector('[data-field="lemma"]').textContent.toLowerCase();
            const prefix = card.querySelector('[data-field="prefix"]').textContent.toLowerCase();
            const root = card.querySelector('[data-field="root"]').textContent.toLowerCase();
            const suffix = card.querySelector('[data-field="suffix"]').textContent.toLowerCase();
            const tag = card.querySelector('.word-header span:last-child').textContent.toLowerCase();

            if (word.includes(searchTerm)) {
                highlightText(card.querySelector('.word-header span:first-child'), searchTerm);
                found = true;
            }
            if (wordField.includes(searchTerm)) {
                highlightText(card.querySelector('[data-field="word"]'), searchTerm);
                found = true;
            }
            if (lemma.includes(searchTerm)) {
                highlightText(card.querySelector('[data-field="lemma"]'), searchTerm);
                found = true;
            }
            if (prefix.includes(searchTerm)) {
                highlightText(card.querySelector('[data-field="prefix"]'), searchTerm);
                found = true;
            }
            if (root.includes(searchTerm)) {
                highlightText(card.querySelector('[data-field="root"]'), searchTerm);
                found = true;
            }
            if (suffix.includes(searchTerm)) {
                highlightText(card.querySelector('[data-field="suffix"]'), searchTerm);
                found = true;
            }
            if (tag.includes(searchTerm)) {
                highlightText(card.querySelector('.word-header span:last-child'), searchTerm);
                found = true;
            }
        });

        if (!found) {
            alert('No matches found for "' + searchTerm + '"');
        } else {
            // Scroll to the first highlighted element
            const firstHighlight = document.querySelector('.highlight');
            if (firstHighlight) {
                firstHighlight.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }
    }

    // Helper function to highlight text
    function highlightText(element, searchTerm) {
        const text = element.textContent;
        const regex = new RegExp(searchTerm, 'gi');
        const newText = text.replace(regex, match => `<span class="highlight">${match}</span>`);

        // Create a temporary element to parse the HTML
        const temp = document.createElement('div');
        temp.innerHTML = newText;

        // Replace the element's content with the highlighted version
        while (element.firstChild) {
            element.removeChild(element.firstChild);
        }

        while (temp.firstChild) {
            element.appendChild(temp.firstChild);
        }
    }
});