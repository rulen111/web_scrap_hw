import requests
import json
from bs4 import BeautifulSoup
from fake_headers import Headers
headers_generator = Headers(os="win", browser="firefox")

# Парсим страницу выдачи результатов поиска вакансий
response = requests.get(
    "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2/", headers=headers_generator.generate()
)
main_html_data = response.text
main_soup = BeautifulSoup(main_html_data, "lxml")
vacancy_list = main_soup.find("main", class_="vacancy-serp-content")
vacancies = vacancy_list.find_all("div", class_="serp-item")
print(f"Найдено вакансий: {len(vacancies)}")

# Проходим циклом по каждой вакансии
vacancies_data = []
for vacancy_tag in vacancies:
    # Достаем ссылку на вакансию
    vacancy_link_tag = vacancy_tag.find("a", attrs={"class": "serp-item__title"})
    vacancy_link = vacancy_link_tag["href"]

    # Достаем город вакансии
    vacancy_city_tag = vacancy_tag.find("div", attrs={"data-qa": "vacancy-serp__vacancy-address"})
    vacancy_city_text = vacancy_city_tag.text.strip().replace('\xa0', ' ')

    # Переходим на страницу вакансии
    response = requests.get(vacancy_link, headers=headers_generator.generate())
    vacancy_html_data = response.text
    vacancy_soup = BeautifulSoup(vacancy_html_data, "lxml")

    # Достаем описание вакансии и проверяем вхождение ключевых слов
    vacancy_description_tag = vacancy_soup.find("div", attrs={"data-qa": "vacancy-description"})
    vacancy_description_text = vacancy_description_tag.text.strip().lower()
    if "django" not in vacancy_description_text and "flask" not in vacancy_description_text:
        continue

    # Достаем название вакансии
    vacancy_title_tag = vacancy_soup.find("h1", attrs={"data-qa": "vacancy-title"})
    vacancy_title_text = vacancy_title_tag.text.strip().replace('\xa0', ' ')

    # Достаем вилку ЗП вакансии
    vacancy_salary_tag = vacancy_soup.find("span", attrs={"data-qa": "vacancy-salary-compensation-type-net"})
    if vacancy_salary_tag:
        vacancy_salary_text = vacancy_salary_tag.text.strip().replace('\xa0', ' ')
    else:
        vacancy_salary_text = "Не указана"

    # Достаем название компании работодателя
    vacancy_company_tag = vacancy_soup.find("span", attrs={"data-qa": "bloko-header-2",
                                                           "class": "bloko-header-section-2 bloko-header-section-2_lite"})
    vacancy_company_text = vacancy_company_tag.text.strip().replace('\xa0', ' ')

    # Добавляем информацию о вакансии в общий список
    vacancies_data.append(
        {
            "title": vacancy_title_text,
            "link": vacancy_link,
            "salary": vacancy_salary_text,
            "employer": vacancy_company_text,
            "city": vacancy_city_text
        }
    )
print(f"Записанов вакансий: {len(vacancies_data)}")

# Записываем информацию о вакансиях в файл json
with open("vacancies.json", "w", encoding="utf-8") as f:
    json.dump(vacancies_data, f, ensure_ascii=False)
