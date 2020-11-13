import urllib.request, time as t
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
chrome_options = Options()
chrome_options.add_argument(r"user-data-dir=C:\Users\arondavidson\AppData\Local\Google\Chrome\User Data\Profile 1")
# chrome_options.add_argument('--headless')
# chrome_options.add_argument("--start-maximized")

class CMSBot:
	def __init__(self):
		self.bot = webdriver.Chrome(options=chrome_options,
			executable_path=r"C:\Users\arondavidson\AppData\Local\Programs\Python\Python37\chromedriver.exe")

	def edit_id(self, ID):
		b = self.bot
		url = 'http://newcms.warc.com/content/edit'
		b.get(url)
		b.implicitly_wait(5)
		legid = b.find_element_by_name('LegacyId')
		legid.clear()
		legid.send_keys(ID)
		legid.send_keys(Keys.RETURN)

	def get_content(self, path, new_ID):
		b = self.bot

		def scroll(element):
			actions = ActionChains(b)
			actions.move_to_element(element).perform()
		
		try:
			new_dir = Path(f"{path}/{new_ID}")
			new_dir.mkdir(parents=False, exist_ok=True)
			abs_fn = new_dir / f"{new_ID}.txt"
			htm_fn = new_dir / f"{new_ID}.htm"

			# grab text from summary
			summary = b.find_element_by_link_text('Summary (English)')
			scroll(summary)
			summary.click()
			summary_text = b.find_element_by_id('ParagraphSummary').text

			# grab html from source code
			body = b.find_element_by_link_text('Content body (English)')
			scroll(body)
			body.click()
			b.find_element_by_id('HtmlContent-Editor-source-code').click()
			body_html = b.find_element_by_id('source-code-textarea').text

			return body_html, summary_text, abs_fn, htm_fn

		except NoSuchElementException as e:
			print('Could not find elementn', e)


	def get_url(self, ID):
		bot = self.bot
		url = bot.find_element_by_xpath(u'//a[text()="Preview"]').get_attribute('href')
		return url

	def save_images(self, new_ID, url, path):
		b = self.bot
		b.get(url)
		t.sleep(1)
		# get the image source
		imgs = b.find_elements_by_class_name('ArticleImages')
		if len(imgs) > 0:
			for n, i in enumerate(imgs, 1):
				src = i.get_attribute('src')
				new_dir = Path(f"{path}/{new_ID}")
				new_dir.mkdir(parents=False, exist_ok=True)
				fn = f"{new_ID}f{str(n).zfill(2)}.{src.split('.')[-1]}"
				fp = new_dir / fn
				print(src.split('/')[-1], "--->", fn.split(r'\\')[-1])
				# download the image
				urllib.request.urlretrieve(src, filename=fp)
			t.sleep(1)
		else:
			print(url, "- no images or need to log in")