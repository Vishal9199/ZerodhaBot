#importing libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv

uid= []
pwd= []
pin= []

with open('loginData.csv', newline='') as uData:
        reader = csv.reader(uData)
        try:
            next(reader)
            for row in reader:
                uid.append(row[0])
                pwd.append(row[1])
                pin.append(row[2].strip())

        except Exception as e:
            print('error in reading csv file -- %s' %e)
print('logging IN')

for i in range(len(uid)):
    try:
        driver = webdriver.Chrome()
        driver.implicitly_wait(7)
        driver.get('https://kite.zerodha.com/')
        driver.find_element(By.ID, "userid").send_keys(uid[i])
        driver.find_element(By.ID, "password").send_keys(pwd[i])
        driver.find_element(By.TAG_NAME, 'button').click()
        driver.maximize_window()
        driver.find_element(By.ID, 'pin').send_keys(pin[i])
        driver.find_element(By.TAG_NAME, 'button').click()
        while True:
            driver.find_element(By.CSS_SELECTOR, '#app > div.header > div > div.header-right > div.app-nav > a:nth-child(4) > span')

    except:
        print('closed driver for -- %s'%(uid[i]))
        driver.quit()
input('\n all fine?\t')
