import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def next_weekday(today, weekday):
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return today + datetime.timedelta(days_ahead)


def _wait_for_request(driver):
    WebDriverWait(driver, 30).until_not(EC.presence_of_element_located((By.CLASS_NAME, 'bigWaiting')))


def find_table(driver):
    driver.get('http://zvonarna.e-rezervace.cz/Branch/pages/Schedule.faces')
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.LINK_TEXT, '2-Squash'))
    )
    element.click()
    _wait_for_request(driver)

    date = next_weekday(datetime.datetime.today(), 1)  # 0 = Monday, 1=Tuesday, 2=Wednesday...
    driver.execute_script('''
        var input = document.getElementById('scheduleNavigForm:schedule_calendarInputDate');
        input.value = "{}";
        input.click();
    '''.format(date.strftime('%d.%m.%Y')))

    calendar_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'rich-calendar-select'))
    )
    driver.execute_script('''
        arguments[0].click();
    ''', calendar_element)
    _wait_for_request(driver)

    select_element = driver.find_element_by_id('scheduleNavigForm:view_filter_menu')
    for option in select_element.find_elements_by_tag_name('option'):
        if option.text == 'Jeden den':
            option.click()
            break
    _wait_for_request(driver)


def parse_table(driver):
    # event_elements = driver.find_elements_by_class_name('event')
    script_element = driver.find_element_by_xpath('//*[@id="resContainer"]/following-sibling::script')
    data = driver.execute_script('eval(arguments[0].innerHTML); return scheduleData', script_element)
    return data


class Interval(object):

    def __init__(self, court, start, end):
        self.court = court
        self.start = start + 7 * 2
        self.duration = end - start + 1

    @classmethod
    def from_table(cls, start, end):
        intervals = []
        for court in range(start[1], end[1] + 1):
            intervals.append(Interval(court, start[0], end[0]))
        return intervals

    def __repr__(self):
        return '{self.court}: ({self.start}, {self.duration})'.format(self=self)


def main():
    driver = webdriver.Firefox()
    try:
        find_table(driver)
        data = parse_table(driver)
        intervals = []
        for x in data['events']:
            intervals.extend(Interval.from_table(x['start'], x['end']))

        print(intervals)
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
