from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import words
from collections import defaultdict
import json
import os

from src.nltk_config import TAGS, MODAL_VERBS

class DictionaryWorker:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.english_words = set(words.words())
        self.common_prefixes = {
            'un', 're', 'pre', 'dis', 'mis', 'non',
            'sub', 'super', 'anti', 'de', 'over'
        }
        self.common_suffixes = {
            'ed', 'ing', 'ly', 's', 'es', 'er', 'est',
            'tion', 'ment', 'ness', 'able', 'ible'
        }
        self.tag_dict = TAGS

    def get_word_info(self, word):
        pos = pos_tag([word])[0][1]
        if pos == 'MD' and word.lower() in MODAL_VERBS:
            lemma = MODAL_VERBS[word.lower()]
        else:
            pos_map = {
                'N': wn.NOUN,
                'V': wn.VERB,
                'J': wn.ADJ,
                'R': wn.ADV
            }
            pos_full = pos_map.get(pos[0], wn.NOUN)
            lemma = self.lemmatizer.lemmatize(word, pos=pos_full)
        morphemes = self.analyze_morphemes(word, lemma)
        tag_description = self.tag_dict.get(pos, 'Неизвестный тег')
        return {
            'word': word,
            'lemma': lemma,
            'morphemes': morphemes,
            'tag': pos,
            'tag_description': tag_description
        }

    def analyze_morphemes(self, word, lemma):
        original = word.lower()
        lemma_lower = lemma.lower()
        suffix = ''
        for s in sorted(self.common_suffixes, key=len, reverse=True):
            if original.endswith(s):
                suffix = s
                stem = original[:-len(s)]
                break
        else:
            stem = original
        if stem == lemma_lower:
            root = stem
            prefix = ''
        else:
            prefix = ''
            for p in sorted(self.common_prefixes, key=len, reverse=True):
                if stem.startswith(p) and len(stem) > len(p):
                    prefix = p
                    stem = stem[len(p):]
                    break
            if stem != lemma_lower:
                root = lemma_lower
                prefix = ''
            else:
                root = stem
        return {
            'prefix': prefix,
            'root': root,
            'suffix': suffix
        }

    def create_dictionary(self, text):
        tokens = word_tokenize(text)
        dictionary = defaultdict(list)
        for token in tokens:
            if token.isalpha():
                word_info = self.get_word_info(token)
                lemma = word_info['lemma']
                existing = next((item for item in dictionary[lemma] if item['word'] == word_info['word']), None)
                if existing is None:
                    dictionary[lemma].append(word_info)
        sorted_dict = dict(sorted(dictionary.items()))
        return sorted_dict

    def save_dictionary_file(self, dictionary, filename):
        filename = f"src/db/{filename}"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)
        return f"Словарь успешно сохранен {filename}"

    def list_dictionary_files(self):
        db_dir = "src/db/"
        try:
            files = os.listdir(db_dir)
            files = [f for f in files if os.path.isfile(os.path.join(db_dir, f))]
            return files if files else "В директории нет файлов словарей"
        except FileNotFoundError:
            return f"Директория {db_dir} не найдена"
        except Exception as e:
            return f"Ошибка при получении списка файлов: {str(e)}"

    def load_dictionary_file(self, filename):
        filename = f"src/db/{filename}"
        with open(filename, 'r', encoding='utf-8') as f:
            dictionary = json.load(f)
        return dictionary

    def delete_dictionary_file(self, filename):
        filename = f"src/db/{filename}"
        if os.path.exists(filename):
            os.remove(filename)
            return f"Словарь успешно удален {filename}"
        else:
            return f"Словарь не найден {filename}"

    def add_word_form(self, dictionary, lemma, word_form):
        if not word_form.isalpha():
            raise ValueError("Word form must contain only alphabetic characters")
        word_info = self.get_word_info(word_form)
        if word_info['lemma'].lower() != lemma.lower():
            raise ValueError(f"Word form '{word_form}' has lemma '{word_info['lemma']}', not '{lemma}'")
        if any(form['word'] == word_form for form in dictionary[lemma]):
            return dictionary
        dictionary[lemma].append(word_info)
        dictionary[lemma].sort(key=lambda x: x['word'])
        return dictionary
