
from datetime import datetime
from transformers import pipeline


# Загрузка отзывов из файла
def load_reviews(filename):
    reviews = []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                review = line.strip()

                if review:
                    reviews.append(review)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")

    return reviews


# Анализ одного отзыва
def analyze_review(analyzer, review):
    result = analyzer(review, truncation=True)[0]

    return result["label"], result["score"]


# Анализ всех отзывов
def analyze_reviews(analyzer, reviews):
    statistics = {
        "Положительный": 0,
        "Отрицательный": 0,
        "Нейтральный": 0
    }

    results = []

    for index, review in enumerate(reviews, start=1):
        label, score = analyze_review(analyzer, review)

        sentiment = normalize_sentiment(label)
        statistics[sentiment] += 1

        result = {
            "text": review,
            "label": label,
            "score": score
        }

        results.append(result)

        print(f"\nОтзыв #{index}")
        print(f"Текст: {review}")
        print(f"Тональность: {label}")
        print(f"Уверенность: {score:.2%}")

    return results, statistics


# Сохранение результатов анализа в файл
def save_results(results, statistics=None, mode="Manual"):
    try:
        with open("results.txt", "a", encoding="utf-8") as file:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            file.write("\n================================\n")
            file.write(f"Анализ: {mode}\n")
            file.write(f"Дата: {current_time}\n")
            file.write("================================\n")

            for index, result in enumerate(results, start=1):
                if mode == "Manual":
                    file.write("\nОтзыв:\n")
                else:
                    file.write(f"\nОтзыв #{index}\n")

                file.write(f"Текст: {result['text']}\n")
                file.write(f"Тональность: {result['label']}\n")
                file.write(f"Уверенность: {result['score']:.2%}\n")

            if statistics is not None:
                file.write("\n================================\n")
                file.write("СТАТИСТИКА\n")
                file.write("================================\n")
                file.write(f"Всего проанализировано: {sum(statistics.values())}\n")
                file.write(f"Положительные: {statistics['Положительный']}\n")
                file.write(f"Отрицательные: {statistics['Отрицательный']}\n")
                file.write(f"Нейтральные: {statistics['Нейтральный']}\n")

        print("Результаты анализа успешно сохранены в 'results.txt'.")

    except OSError as error:
        print(f"Ошибка при сохранении результатов: {error}")


# Сохранение результатов сравнения моделей
def save_comparison(results, matches, differences):
    try:
        with open("results.txt", "a", encoding="utf-8") as file:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            file.write("\n================================\n")
            file.write("СРАВНЕНИЕ ДВУХ МОДЕЛЕЙ\n")
            file.write(f"Дата: {current_time}\n")
            file.write("================================\n")

            file.write(f"Модель 1: {MODEL_NAME}\n")
            file.write(f"Модель 2: {SECOND_MODEL_NAME}\n")

            for index, result in enumerate(results, start=1):
                file.write(f"\nОтзыв #{index}\n")
                file.write(f"Текст: {result['text']}\n")
                file.write(
                    f"Модель 1: {result['label1']} "
                    f"({result['score1']:.2%})\n"
                )
                file.write(
                    f"Модель 2: {result['label2']} "
                    f"({result['score2']:.2%})\n"
                )
                file.write(f"Результат: {result['comparison']}\n")

            total = len(results)

            file.write("\n================================\n")
            file.write("ИТОГИ СРАВНЕНИЯ\n")
            file.write("================================\n")
            file.write(f"Всего отзывов: {total}\n")
            file.write(f"Совпадений: {matches}\n")
            file.write(f"Несовпадений: {differences}\n")
            file.write(f"Процент совпадений: {matches / total:.2%}\n")

        print("\nРезультаты сравнения сохранены в 'results.txt'.")

    except OSError as error:
        print(f"Ошибка при сохранении результатов: {error}")



# Ручной анализ одного отзыва
def manual_analysis(analyzer):
    review = input("\nВведите отзыв для анализа: ").strip()

    if not review:
        print("Ошибка: Отзыв не может быть пустым.")
        return

    label, score = analyze_review(analyzer, review)

    print("\n================================")
    print("РЕЗУЛЬТАТ АНАЛИЗА")
    print("================================")
    print(f"Текст: {review}")
    print(f"Тональность: {label}")
    print(f"Уверенность: {score:.2%}")

    result = {
        "text": review,
        "label": label,
        "score": score
    }

    save_results([result], mode="Manual")


# Анализ отзывов из файла
def file_analysis(analyzer):
    reviews = load_reviews("reviews.txt")

    if not reviews:
        print("Отзывы не найдены.")
        return

    print("\n================================")
    print("АНАЛИЗ ОТЗЫВОВ ИЗ ФАЙЛА")
    print("================================")
    print(f"Всего отзывов: {len(reviews)}")

    results, statistics = analyze_reviews(analyzer, reviews)

    print("\n================================")
    print("СТАТИСТИКА")
    print("================================")
    print(f"Всего проанализировано: {sum(statistics.values())}")
    print(f"Положительные: {statistics['Положительный']}")
    print(f"Отрицательные: {statistics['Отрицательный']}")
    print(f"Нейтральные: {statistics['Нейтральный']}")

    save_results(results, statistics, mode="File")



# Сравнение результатов двух моделей
def compare_models(analyzer1, analyzer2, reviews):
    results = []

    matches = 0
    differences = 0

    for index, review in enumerate(reviews, start=1):
        label1, score1 = analyze_review(analyzer1, review)
        label2, score2 = analyze_review(analyzer2, review)

        sentiment1 = normalize_sentiment(label1)
        sentiment2 = normalize_sentiment(label2)

        if sentiment1 == sentiment2:
            comparison = "СОВПАДАЕТ"
            matches += 1
        else:
            comparison = "НЕ СОВПАДАЕТ"
            differences += 1

        result = {
            "text": review,
            "label1": label1,
            "score1": score1,
            "label2": label2,
            "score2": score2,
            "comparison": comparison
        }

        results.append(result)

        print(f"\nОтзыв #{index}")
        print(f"Текст: {review}")
        print(f"Модель 1: {label1} ({score1:.2%})")
        print(f"Модель 2: {label2} ({score2:.2%})")
        print(f"Результат: {comparison}")

    total = len(results)

    print("\n================================")
    print("СРАВНЕНИЕ МОДЕЛЕЙ")
    print("================================")
    print(f"Всего отзывов: {total}")
    print(f"Совпадений: {matches}")
    print(f"Несовпадений: {differences}")
    print(f"Процент совпадений: {matches / total:.2%}")

    return results, matches, differences

# Анализ и сравнение двух моделей
def comparison_analysis(analyzer):
    reviews = load_reviews("reviews.txt")

    if not reviews:
        print("Отзывы не найдены.")
        return

    print("\nЗагрузка второй модели Hugging Face...")

    try:
        analyzer2 = pipeline(
            "sentiment-analysis",
            model=SECOND_MODEL_NAME
        )

    except Exception as error:
        print(f"Ошибка загрузки второй модели: {error}")
        return

    print("\n================================")
    print("АНАЛИЗ ДВУМЯ МОДЕЛЯМИ")
    print("================================")

    results, matches, differences = compare_models(
        analyzer, analyzer2, reviews
    )

    save_comparison(results, matches, differences)


# Нормализация тональности
def normalize_sentiment(label):
    label = label.lower()

    if label in ["very positive", "positive"]:
        return "Положительный"
    elif label in ["very negative", "negative"]:
        return "Отрицательный"
    elif label == "neutral":
        return "Нейтральный"
    else:
        raise ValueError(f"Неизвестная тональность: {label}")


# Отображение меню
def show_menu():
    print("\n================================")
    print("АНАЛИЗАТОР ОТЗЫВОВ")
    print("================================")
    print("1. Ручной анализ одного отзыва")
    print("2. Анализ отзывов из файла")
    print("3. Сравнение двух моделей")
    print("0. Выход")
    print("================================")


# Main Program
MODEL_NAME = "tabularisai/multilingual-sentiment-analysis"
SECOND_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

analyzer = pipeline("sentiment-analysis", model=MODEL_NAME)

while True:
    show_menu()

    choice = input("Выберите опцию: ").strip()

    if choice == "1":
        manual_analysis(analyzer)

    elif choice == "2":
        file_analysis(analyzer)

    elif choice == "3":
        comparison_analysis(analyzer)

    elif choice == "0":
        print("Выход...")
        break

    else:
        print("Неверная опция. Пожалуйста, попробуйте снова.")
