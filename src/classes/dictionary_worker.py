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
        # Определение части речи
        pos = pos_tag([word])[0][1]

        # Специальная обработка модальных глаголов
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
        lemma_lower = lemma.lower()

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
        if stem == lemma_lower:
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
            if token.isalpha():  # Игнорируем не-слова
                word_info = self.get_word_info(token)
                lemma = word_info['lemma']

                # Проверка на существование такой же записи
                existing = next((item for item in dictionary[lemma] if item['word'] == word_info['word']), None)
                if existing is None:
                    dictionary[lemma].append(word_info)

        # Сортировка по алфавиту
        sorted_dict = dict(sorted(dictionary.items()))
        return sorted_dict

    def save_dictionary_file(self, dictionary, filename):
        """
        Сохраняет словарь в файл в формате JSON.

        :param dictionary: Словарь, который нужно сохранить.
        :param filename: Имя файла для сохранения.
        """
        filename = f"src/db/{filename}"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)
        return {"message": f"Словарь успешно сохранен {filename}"}

    def load_dictionary_file(self, filename):
        """
        Загружает словарь из файла и возвращает его.

        :param filename: Имя файла для загрузки.
        :return: Загруженный словарь.
        """
        filename = f"src/db/{filename}"
        with open(filename, 'r', encoding='utf-8') as f:
            dictionary = json.load(f)
        return dictionary

    def delete_dictionary_file(self, filename):
        """
        Удаляет файл со словарем, если он существует.

        :param filename: Имя файла, который нужно удалить.
        :return: True, если файл был успешно удален, иначе False.
        """
        filename = f"./"
        if os.path.exists(filename):
            os.remove(filename)
            return {"message": f"Словарь успешно удален {filename}"}
        else:
            return {"message": f"Словарь не найден {filename}"}

    def add_word_form(self, dictionary, lemma, word_form):
        """
        Добавляет новую словоформу к существующей лексеме в словаре

        :param dictionary: словарь (defaultdict(list)), в который нужно добавить словоформу
        :param lemma: лемма, к которой добавляем словоформу
        :param word_form: новая словоформа (строка)
        :return: обновленный словарь
        """
        if not word_form.isalpha():
            raise ValueError("Word form must contain only alphabetic characters")

        # Получаем информацию о новой словоформе
        word_info = self.get_word_info(word_form)

        # Проверяем, что лемма совпадает с указанной
        if word_info['lemma'].lower() != lemma.lower():
            raise ValueError(f"Word form '{word_form}' has lemma '{word_info['lemma']}', not '{lemma}'")

        # Проверяем, есть ли уже такая словоформа в словаре
        if any(form['word'] == word_form for form in dictionary[lemma]):
            return dictionary  # Словоформа уже существует

        # Добавляем новую словоформу
        dictionary[lemma].append(word_info)

        # Сортируем словоформы по алфавиту
        dictionary[lemma].sort(key=lambda x: x['word'])

        return dictionary

    def generate_word_form(self, lemma, tag):
        """
        Генерирует словоформу на основе леммы и тега

        :param lemma: базовая форма слова
        :param tag: тег части речи (например, 'VBD' для глагола в прошедшем времени)
        :return: сгенерированная словоформа или None, если генерация невозможна
        """
        # Приводим к нижнему регистру для унификации
        lemma = lemma.lower()
        tag = tag.upper()

        # Правила для глаголов
        if tag.startswith('VB'):
            if tag == 'VBD' or tag == 'VBN':  # Прошедшее время
                if lemma in ('be', 'have', 'do'):
                    return {
                        'be': 'was' if tag == 'VBD' else 'been',
                        'have': 'had',
                        'do': 'did'
                    }.get(lemma)
                elif lemma.endswith('e'):
                    return lemma + 'd'
                else:
                    return lemma + 'ed'

            elif tag == 'VBG':  # Причастие настоящего времени
                if lemma.endswith('e') and not lemma.endswith('ee'):
                    return lemma[:-1] + 'ing'
                elif lemma.endswith('ie'):
                    return lemma[:-2] + 'ying'
                else:
                    return lemma + 'ing'

            elif tag == 'VBZ':  # 3-е лицо единственного числа
                if lemma in ('be', 'have', 'do'):
                    return {
                        'be': 'is',
                        'have': 'has',
                        'do': 'does'
                    }.get(lemma)
                elif lemma.endswith(('s', 'sh', 'ch', 'x', 'z')):
                    return lemma + 'es'
                elif lemma.endswith('y') and lemma[-2] not in 'aeiou':
                    return lemma[:-1] + 'ies'
                else:
                    return lemma + 's'

        # Правила для существительных
        elif tag.startswith('NN'):
            if tag == 'NNS':  # Множественное число
                irregular_plurals = {
                    'child': 'children',
                    'foot': 'feet',
                    'tooth': 'teeth',
                    'mouse': 'mice',
                    'person': 'people'
                }
                if lemma in irregular_plurals:
                    return irregular_plurals[lemma]
                elif lemma.endswith(('s', 'sh', 'ch', 'x', 'z')):
                    return lemma + 'es'
                elif lemma.endswith('y') and lemma[-2] not in 'aeiou':
                    return lemma[:-1] + 'ies'
                elif lemma.endswith('f'):
                    return lemma[:-1] + 'ves'
                elif lemma.endswith('fe'):
                    return lemma[:-2] + 'ves'
                else:
                    return lemma + 's'

        # Правила для прилагательных
        elif tag.startswith('JJ'):
            if tag == 'JJR':  # Сравнительная степень
                if lemma in ('good', 'bad', 'far'):
                    return {
                        'good': 'better',
                        'bad': 'worse',
                        'far': 'farther'
                    }.get(lemma)
                elif lemma.endswith('e'):
                    return lemma + 'r'
                elif lemma.endswith('y') and lemma[-2] not in 'aeiou':
                    return lemma[:-1] + 'ier'
                elif len(lemma) >= 3 and lemma[-1] not in 'aeiou' and lemma[-2] in 'aeiou' and lemma[-3] not in 'aeiou':
                    return lemma + lemma[-1] + 'er'
                else:
                    return lemma + 'er'

            elif tag == 'JJS':  # Превосходная степень
                if lemma in ('good', 'bad', 'far'):
                    return {
                        'good': 'best',
                        'bad': 'worst',
                        'far': 'farthest'
                    }.get(lemma)
                elif lemma.endswith('e'):
                    return lemma + 'st'
                elif lemma.endswith('y') and lemma[-2] not in 'aeiou':
                    return lemma[:-1] + 'iest'
                elif len(lemma) >= 3 and lemma[-1] not in 'aeiou' and lemma[-2] in 'aeiou' and lemma[-3] not in 'aeiou':
                    return lemma + lemma[-1] + 'est'
                else:
                    return lemma + 'est'

        return None

    def add_word_form_by_tag(self, dictionary, lemma, tag):
        """
        Генерирует и добавляет словоформу на основе леммы и тега

        :param dictionary: словарь (defaultdict(list)), в который нужно добавить словоформу
        :param lemma: лемма, к которой добавляем словоформу
        :param tag: тег части речи (например, 'VBD' для глагола в прошедшем времени)
        :return: обновленный словарь
        """
        word_form = self.generate_word_form(lemma, tag)
        if word_form is None:
            raise ValueError(f"Cannot generate word form for lemma '{lemma}' with tag '{tag}'")

        return self.add_word_form(dictionary, lemma, word_form)