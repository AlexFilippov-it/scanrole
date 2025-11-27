from linkedin_scraper import Job, actions
from selenium import webdriver

driver = webdriver.Chrome()
actions.login(driver)  # Спросит email/password в терминале
job = Job("https://www.linkedin.com/jobs/view/3456898261", driver=driver, close_on_complete=False)
print(job)
