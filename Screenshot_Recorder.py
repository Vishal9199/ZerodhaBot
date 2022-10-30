#importing libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import time
import csv
import os

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

date = datetime.datetime.now().strftime("%b%d")
try:
    os.mkdir(os.path.join(os.getcwd(), date))
except:
    import shutil
    shutil.rmtree(os.path.join(os.getcwd(), date))
    os.mkdir(os.path.join(os.getcwd(), date))

os.chdir(os.path.join(os.getcwd(), date))

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

        name= driver.find_element(By.CSS_SELECTOR, '#app > div.container.wrapper > div.container-right > div > div > h1 > span').text
        driver.find_element(By.CSS_SELECTOR, '#app > div.header > div > div.header-right > div.app-nav > a:nth-child(4) > span').click()
        time.sleep(1)
        driver.save_screenshot('%s%s.png' %(date,uid[i]))
        print('screenshot saved for \t %s' %name)

        driver.quit()

    except Exception as e:
        print('couldnt login for -- %s --\t%s'%(uid[i],e))
        driver.quit()

print('\nscreenshots saved in child directory\t')
