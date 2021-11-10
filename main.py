import services.startDriver
from services.startDriver import *
import csv
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException


def initiate_driver(driver, url):
    driver.get(url)


def fillForm(driver, members):
    formTag = "form#custom_form "
    tags = {
        "firstName": formTag + 'input.field_type-first_name[name="2143195302"]',
        "lastName": formTag + 'input.field_type-last_name[name="2143195302"]',
        "guardian": formTag + 'input[name="2143195303"]',
        "phone": formTag + 'input[name="2143195304"]',
        "email": formTag + 'input[name="2143195305"]',
        "fellowship": formTag + "div.field_2143195306 ",
        "agreements": formTag + 'input[type="checkbox"]',
    }
    buttonCSS = "button#submit"
    returnToFormButtonCSS = "a.return_to_form"

    WebDriverWait(driver, 2147483647).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, buttonCSS))
    )

    try:
        for member in members:
            driver.get(
                "https://nycbc.breezechms.com/form/6d9d2510867913525845518213115168941257227345259327618061713965257424945628127140573113171039894790"
            )

            fields = {}
            for tag in tags:
                if not tag == "agreements" and not tag == "fellowship":
                    fields[tag] = driver.find_element_by_css_selector(tags[tag])
                elif tag == "agreements":
                    fields[tag] = driver.find_elements_by_css_selector(tags[tag])

            fellowshipTemp = (
                tags["fellowship"]
                + 'label.radio>input[value="'
                + str(member["fellowship"])
                + '"]'
            )
            fields["fellowship"] = driver.find_element_by_css_selector(fellowshipTemp)
            button = driver.find_element_by_css_selector(buttonCSS)

            for fieldName in fields:
                if not fieldName == "fellowship" and not fieldName == "agreements":
                    fields[fieldName].send_keys(member[fieldName])
            fields["fellowship"].click()
            for agreement in fields["agreements"]:
                agreement.click()

            button.click()
            
            WebDriverWait(driver, 2147483647).until(EC.presence_of_element_located((By.CSS_SELECTOR, returnToFormButtonCSS)))
    except Exception as e:
        print(str(e))


INPUT_PATH = "./input/info.csv"


def fellowshipConversion(memberDict):
    fellowshipList = {
        "": 1504,  # N/A
        "Enoch": 1446,
        "Jireh": 1447,
        "Kairos": 1448,
        "Nissi": 1449,
        "Kadesh": 1450,
        "Canaan": 1451,
        "Joshua": 1452,
        "Caleb": 1453,
        "Evergreen": 1454,
        "John": 1455,
        "New Comer": 1456,
        "N/A": 1504,
    }

    if not memberDict["fellowship"] in fellowshipList:
        raise Exception(
            memberDict["firstName"]
            + ""
            + memberDict["lastName"]
            + "'s fellowship: \""
            + memberDict["fellowship"]
            + '" is not valid.'
        )

    if memberDict["fellowship"]:
        memberDict["fellowshipName"] = memberDict["fellowship"]
    else:
        memberDict["fellowshipName"] = "N/A"

    memberDict["fellowship"] = fellowshipList[memberDict["fellowship"]]

    return memberDict


def readFile():
    members = []
    with open(INPUT_PATH, "r", newline="") as csvfile:
        fileIsNotEmpty = csvfile.read(1)
        if not fileIsNotEmpty:
            raise Exception("Member list is empty!")

        csvfile.seek(0)

        members_csv = csv.DictReader(
            csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        for member in members_csv:
            if member:
                if not member["firstName"]:
                    raise Exception("First name is missing for one of the entries.")
                if not member["lastName"]:
                    raise Exception(
                        "Last name is missing for " + member["firstName"] + "."
                    )
                if not member["phone"]:
                    raise Exception(
                        "Phone no. is missing for "
                        + member["firstName"]
                        + " "
                        + member["lastName"]
                        + "."
                    )
                if not member["email"]:
                    raise Exception(
                        "E-mail is missing for "
                        + member["firstName"]
                        + " "
                        + member["lastName"]
                        + "."
                    )

                member = fellowshipConversion(member)

                member["phone"] = int(member["phone"])

                members.append(member)
            else:
                pass

    return members


def checkFile():
    file = Path(INPUT_PATH)
    file.touch(exist_ok=True)

    return readFile()


def run():

    members = checkFile()

    driver = services.startDriver.start()
    initiate_driver(
        driver,
        "https://nycbc.breezechms.com/form/6d9d2510867913525845518213115168941257227345259327618061713965257424945628127140573113171039894790",
    )
    try:
        fillForm(driver, members)

    except:
        pass
    finally:
        #input("Press Enter to close...")
        driver.close()


if __name__ == "__main__":
    run()
