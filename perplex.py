from selenium import webdriver
from selenium_stealth import stealth
import undetected_chromedriver as uc
import time
from urllib.parse import urlparse
import openai
import sys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent


openai.api_key = "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"

def bypass_cloudflare(driver):
    stage = WebDriverWait(driver, 20).until(presence_of_element_located((By.CSS_SELECTOR, '#challenge-stage')))
    print(stage)
    time.sleep(2.8)
    try:
        frame = WebDriverWait(driver, 20).until(presence_of_element_located((By.XPATH,'//*[contains(@id, "cf-chl-widget")]')))
    except:
        driver.refresh()
    driver.switch_to.frame(frame)
    print(frame)
    time.sleep(1.7)
    challenge_stage = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#challenge-stage > div > label > span.mark')))
    print("Found")
    element = driver.find_element(By.CSS_SELECTOR, '#challenge-stage > div > label > input')
    time.sleep(2.6)
    element.click()
    driver.switch_to.default_content()

def format_response(response):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            request_timeout= 30,
            temperature = 0.6,
            messages=[
                {"role": "system", "content": "Using these websites, create a comprehensive summary of this producer (focus on trying to figure out who they are signed to, managed by or published by. If that information is not available in the sources I provide, figure it out yourself). Make sure the data is relevant to the songwriter/producer and remove any irrelevant information if the sources don't refer to the correct person. If you are not sure about something or the information seems irrelevant, DO NOT RETURN IT: "},
                {"role": "user", "content": "[{'title': 'genius.com', 'url': 'https://genius.com/artists/254bodi'}, {'title': 'www.254sound.ca', 'url': 'https://www.254sound.ca/'}, {'title': 'twitter.com', 'url': 'https://twitter.com/beatsbybodi'}, {'title': 'www.reddit.com', 'url': 'https://www.reddit.com/r/PoloG/comments/tlrz09/254bodi_the_story_behind_polo_g_bloody_canvas/'}, {'title': 'beatmakingvideos.com', 'url': 'https://beatmakingvideos.com/video/uncategorized/bodi-story-behind-polo-g-bloody-canvas/'}]"},
                {"role": "assistant", "content": '254Bodi is a music producer who has gained recognition for his work with rapper Polo G. Through his production, he has contributed to some of Polo Gs most popular tracks such as "Pop Out" and "Bloody Canvas." He has a profile on the website Genius where his discography is listed, including songs he has produced for Polo G, Lil Durk, and Juice WRLD. On his official website, 254Sound.ca, he offers production services and sells beats. His Twitter account, @beatsbybodi, has over 13,000 followers and is regularly updated with updates on his music and collaborations. Additionally, there is a Reddit thread about him where he is discussed in relation to his work with Polo G and the making of "Bloody Canvas." Finally, there is a video on beatmakingvideos.com that features Bodi telling the story behind the creation of "Bloody Canvas." It is unclear from these sources who Bodi is signed to, managed by, or published by.'},
                {"role": "user", "content": str(response)},
            ]
        )
        sentiment = response.choices[0]['message']['content'].strip()
        return sentiment
    except:
        print("Content failed to load. Trying again in 5 seconds.")
        time.sleep(1.5)
        format_response(comment)


#Customize Options
options = Options()
#proxy = "http://c751d3f66f12dd6919616aef636958298dc7e4eb:@proxy.zenrows.com:8001"
#options.add_argument(f'--proxy-server={proxy}')
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
options.add_argument("--start-maximized")

# Set up Selenium WebDriver
driver = uc.Chrome(options=options)

# Navigate to perplexity.ai
artist = sys.argv[1]
driver.get(f'https://www.perplexity.ai/search?q=songwriter/producer+{artist}')
time.sleep(1.7)
# Find and input the question in the textarea field
#search_field = WebDriverWait(driver, 10).until(presence_of_element_located((By.TAG_NAME, "textarea")))
#search_field.send_keys(f'Tell me everything there is to know about artist/songwriter/producer {artist}. Go into the amount of detail that a CEO of a record label would want to know')
# Submit the question by pressing Enter and wait for the results page to load
#search_field.send_keys(Keys.RETURN)
WebDriverWait(driver, 10).until(presence_of_element_located((By.CSS_SELECTOR, "#__next > main > div > div > div.grow > div > div > div.min-h-\[100vh\].flex.flex-col.pt-\[56px\].pb-\[124px\].md\:pb-0 > div > div > div:nth-child(2) > div > div > div > div.border-borderMain.dark\:border-borderMainDark.divide-borderMain.dark\:divide-borderMainDark.ring-borderMain.dark\:ring-borderMainDark.transition.duration-300.bg-transparent > div > div.border-borderMain.dark\:border-borderMainDark.divide-borderMain.dark\:divide-borderMainDark.ring-borderMain.dark\:ring-borderMainDark.transition.duration-300.bg-background.dark\:bg-backgroundDark > div.default.font-sans.text-base.text-textMain.dark\:text-textMainDark.selection\:bg-super.selection\:text-white.dark\:selection\:bg-opacity-50.selection\:bg-opacity-70 > div > div:nth-child(1) > div > span")))

time.sleep(3)

# Print out the results
results = driver.find_elements(By.CSS_SELECTOR, "#__next > main > div > div > div.grow > div > div > div.min-h-\[100vh\].flex.flex-col.pt-\[56px\].pb-\[124px\].md\:pb-0 > div > div > div:nth-child(2) > div > div > div > div.border-borderMain.dark\:border-borderMainDark.divide-borderMain.dark\:divide-borderMainDark.ring-borderMain.dark\:ring-borderMainDark.transition.duration-300.bg-transparent > div > div.border-borderMain.dark\:border-borderMainDark.divide-borderMain.dark\:divide-borderMainDark.ring-borderMain.dark\:ring-borderMainDark.transition.duration-300.bg-background.dark\:bg-backgroundDark > div.default.font-sans.text-base.text-textMain.dark\:text-textMainDark.selection\:bg-super.selection\:text-white.dark\:selection\:bg-opacity-50.selection\:bg-opacity-70 > div > div:nth-child(1) > div > span")
refs = results[0].find_elements(By.TAG_NAME, "a")
references = []
for ref in refs:
    y = {"title": urlparse(ref.get_attribute("href")).netloc, "url": ref.get_attribute("href")}
    if y not in references:
        references.append(y)

#print(results[0].text.strip())
print(references)
msg = f'{references} /n {results[0].text.strip()}'
print(format_response(msg))
#for result in results:
    #print(result.text.strip())


# Close the browser
driver.quit()
