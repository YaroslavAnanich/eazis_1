from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import words
from collections import defaultdict
import json, os
from nltk_tags_config import tag_dict


class DictionaryCreater:
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
        self.tag_dict = tag_dict

    def get_word_info(self, word):
        # Определение части речи
        pos = pos_tag([word])[0][1]
        pos_map = {
            'N': wn.NOUN,
            'V': wn.VERB,
            'J': wn.ADJ,
            'R': wn.ADV
        }
        pos_full = pos_map.get(pos[0], wn.NOUN)

        # Лемматизация
        lemma = self.lemmatizer.lemmatize(word, pos=pos_full)

        # Морфемный анализ
        morphemes = self.analyze_morphemes(word, lemma)

        # Расшифровка тега
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

        # Поиск суффикса
        suffix = ''
        for s in sorted(self.common_suffixes, key=len, reverse=True):
            if original.endswith(s):
                suffix = s
                stem = original[:-len(s)]
                break
        else:
            stem = original  # Если суффикс не найден, используем всё слово как корень

        # Если лемма совпадает со стемом, то это корень
        if stem == lemma.lower():
            root = stem
            prefix = ''
        else:
            # Поиск префикса
            prefix = ''
            for p in sorted(self.common_prefixes, key=len, reverse=True):
                if stem.startswith(p) and len(stem) > len(p):
                    prefix = p
                    stem = stem[len(p):]
                    break

            # Если после удаления префикса стем не совпадает с леммой, то используем лемму как корень
            if stem != lemma.lower():
                root = lemma.lower()
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
            if token.isalpha():  # Игнорируем не-слова
                word_info = self.get_word_info(token)
                lemma = word_info['lemma']

                # Проверка на существование такой же записи
                existing = next((item for item in dictionary[lemma] if item == word_info), None)
                if existing is None:
                    dictionary[lemma].append(word_info)  # Добавляем только если запись не существует

        # Сортировка по алфавиту
        sorted_dict = dict(sorted(dictionary.items()))
        return sorted_dict


class DictionaryWorker:

    def save_dictionary_file(self, dictionary, filename):
        """
        Сохраняет словарь в файл в формате JSON.

        :param dictionary: Словарь, который нужно сохранить.
        :param filename: Имя файла для сохранения.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)
        return {"message": f"Словарь успешно сохранен {filename}"}


    def load_dictionary_file(self, filename):
        """
        Загружает словарь из файла и возвращает его.

        :param filename: Имя файла для загрузки.
        :return: Загруженный словарь.
        """
        with open(filename, 'r', encoding='utf-8') as f:
            dictionary = json.load(f)
        return dictionary

    def delete_dictionary_file(self, filename):
        """
        Удаляет файл со словарем, если он существует.

        :param filename: Имя файла, который нужно удалить.
        :return: True, если файл был успешно удален, иначе False.
        """
        if os.path.exists(filename):
            os.remove(filename)
            return {"message": f"Словарь успешно удален {filename}"}
        else:
            return {"message": f"Словарь не найден {filename}"}


