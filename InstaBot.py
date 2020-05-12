from time import sleep
import selenium
import selenium.common.exceptions

from openpyxl import Workbook
from selenium import webdriver

import config

username = config.username
password = config.password
sub_period = config.sub_period

# Выбор браузера
browser = webdriver.Chrome()

# Открытие Excel-файла
wb = Workbook()
ws = wb.active
ws.title = username
ws['A1'] = "Подписчики"
ws['B1'] = "Подписки"
ws['C1'] = "Невзаимные подписки"

# Данные для бота
subscribers_links_global = []
followings_links_global = []


def registration():
    browser.get("https://www.instagram.com/")
    sleep(0.5)
    try:
        browser.find_element_by_xpath("//input[@name = 'username']").send_keys(
            username)
    except selenium.common.exceptions.NoSuchElementException:
        print("Не успел загрузиться сайт")
        sleep(2)
        browser.find_element_by_xpath("//input[@name = 'username']").send_keys(
            username)
    browser.find_element_by_xpath("//input[@name = 'password']").send_keys(
        password)
    browser.find_element_by_xpath("//button[@type = 'submit']").click()
    sleep(3)


def login_check():
    # Проверка необходимости ввести код подтверждения
    try:
        browser.find_element_by_xpath("//button[contains(text(), 'Отправить код безопасности')]").click()
        sleep(3)
        browser.find_element_by_xpath("//input[@type = 'tel']").send_keys(
            input("Введите код: "))
        sleep(1)
        browser.find_element_by_xpath("//button[contains(text(), 'Отправить')]").click()
        browser.maximize_window()
        sleep(2)
    except selenium.common.exceptions.NoSuchElementException:
        pass

    # Проверка кнопки "включить уведомления"
    try:
        browser.find_element_by_xpath("//button[contains(text(), 'Не сейчас')]").click()
        sleep(1)
    except selenium.common.exceptions.NoSuchElementException:
        pass


def scroll(block):
    last_position, bottom = 0, 1
    while last_position != bottom:
        last_position = bottom
        sleep(1)
        bottom = browser.execute_script("""
            arguments[0].scrollTo(0 , arguments[0].scrollHeight);
            return arguments[0].scrollHeight;
            """, block)


def get_subscribers():
    browser.get(f"https://www.instagram.com/{username}")
    sleep(3)
    browser.find_element_by_xpath("//a[contains(@href,'/followers')]").click()
    sleep(2)
    subscribers_block = browser.find_element_by_xpath("/html/body/div[4]/div/div[2]")
    scroll(subscribers_block)
    subscribers_links = [subscriber.get_attribute("href") for subscriber in
                         subscribers_block.find_elements_by_xpath("//a[@title]") if subscriber != ""]
    subscribers_links_global.extend(subscribers_links)
    for i in range(len(subscribers_links)):
        ws[f"B{i + 2}"] = subscribers_links[i]
    print("Подписчики внесены в базу данных")


def get_followings():
    browser.get(f"https://www.instagram.com/{username}")
    sleep(2)
    browser.find_element_by_xpath("//a[contains(@href,'/following')]").click()
    sleep(2)
    followings_block = browser.find_element_by_xpath("/html/body/div[4]/div/div[2]")
    scroll(followings_block)
    followings_links = [following.get_attribute("href") for following in
                        followings_block.find_elements_by_xpath("//a[@title]") if following != ""]
    # followings_profiles = [following.text for following in
    #                       followings_block.find_elements_by_xpath("//a[@title]") if following != ""]
    followings_links_global.extend(followings_links)
    for i in range(len(followings_links)):
        ws[f"A{i + 2}"] = followings_links[i]
    print("Подписки внесены в базу данных")


def get_delta():
    delta = []
    for following in followings_links_global:
        if following in subscribers_links_global:
            delta.append(following)
    for i in range(len(delta)):
        ws[f"C{i + 2}"] = delta[i]
    print("Невзаимные подписки внесены в базу данных")


def check_sub(block):
    for _ in block.find_elements_by_xpath("//a[@title]"):
        try:
            browser.find_element_by_xpath("//button[contains(text(), 'Подписаться')]").click()
            sleep(sub_period)
        except selenium.common.exceptions.NoSuchElementException:
            pass


def mutual_subscribe():
    browser.get(f"https://www.instagram.com/{username}")
    sleep(2)
    try:
        browser.find_element_by_xpath("//a[contains(@href,'/followers)]").click()
        sleep(2)
    except selenium.common.exceptions.NoSuchElementException:
        browser.get(f"https://www.instagram.com/{username}")
        sleep(2)
        browser.find_element_by_xpath("//a[contains(@href,'/followers')]").click()
        sleep(2)
    followers_block = browser.find_element_by_xpath("/html/body/div[4]/div/div[2]")
    scroll(followers_block)
    check_sub(followers_block)


def like_posts():
    # browser.get("https://www.instagram.com/")
    sleep(14)
    posts = browser.find_elements_by_xpath("//section/main/section/div[1]/div[2]/div")
    for post in posts:
        for i in post.find_elements_by_xpath("//section/main/section/div/div[2]/div/article[3]/div[2]/section[1]/span[1]/button/svg/path"):
            i.click()


registration()
login_check()
# get_subscribers()
# get_followings()
# get_delta()
# mutual_subscribe()
like_posts()
wb.save("subscribers.xlsx")
browser.quit()
