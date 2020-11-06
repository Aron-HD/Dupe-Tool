import PySimpleGUI as sg, json
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


	def get_info(self, SUBS, award, path, new_ID, old_ID):
		b = self.bot

		def scroll(element):
			actions = ActionChains(b)
			actions.move_to_element(element).perform()
		
		new_dir = Path(f"{path}/{new_ID}")
		new_dir.mkdir(parents=False, exist_ok=True)
		abs_fn = new_dir / f"{new_ID}.txt"
		htm_fn = new_dir / f"{new_ID}.htm"
		# grab text from summary
		summary = b.find_element_by_link_text('Summary (English)')
		scroll(summary)
		summary.click()
		summary_text = b.find_element_by_id('ParagraphSummary').text
		# # write summary text to new txt file named after new ID
		write_file(abs_fn, summary_text)
		# grab html from source code
		body = b.find_element_by_link_text('Content body (English)')
		scroll(body)
		body.click()
		b.find_element_by_id('HtmlContent-Editor-source-code').click()
		body_html = b.find_element_by_id('source-code-textarea').text

		amended_html = amend_content(
							SUBS=SUBS,
							award=award,
							new_ID=new_ID,
							old_ID=old_ID,
							content=body_html
						)
		t.sleep(0.5)
		# # write html text to new htm file named after new ID
		write_file(htm_fn, amended_html)

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

def amend_content(SUBS, award, new_ID, old_ID, content):
	# replace subheadings according to the award the dupes have been entered to
	for i in SUBS.keys():
		if i != award:
			for k, v in SUBS[i].items():
				r = SUBS[award][k]
				content = content.replace(v, r)
	# replacements within image tags
	for i, x in zip([f'/{old_ID}f', 'ASIA-MEDIA', 'MEDIA-MEDIA', 'WARC-WARC', '<h3>Footnotes</h3>'], 
					[f'/{new_ID}f', 'ASIA', 'MEDIA', 'WARC', '<h3>Sources</h3>']):
		content = content.replace(i,x)
	# content = content.replace(f'/{old_ID}f', f'/{new_ID}f').replace('MEDIA-MEDIA', 'MEDIA')
	return content

def write_file(filename, contents):
		with open(filename, "w", encoding='utf-8') as f:
			f.write(contents)
			print(filename.name)

def dupe_assets(SUBS, cms, event, values):
	OIDs_input = values['OIDS']
	NIDs_input = values['NIDS']
	dst_path = values['DST']

	if not OIDs_input:
		print('No old dupe IDs entered')
	if not NIDs_input:
		print('No new dupe IDs entered')
	elif not dst_path:
		print('No destination path entered')
	else:
		IDs = zip(
			[int(x) if len(x) == 6 else print(x, 'ID not valid 6 digits') for x in OIDs_input.strip().split('\n')],
			[int(x) if len(x) == 6 else print(x, 'ID not valid 6 digits') for x in NIDs_input.strip().split('\n')]
		)
		print(f"# creating in:\n# '{dst_path}'")
		for old, new in IDs:
			cms.edit_id(old)
			if event == 'Images':
				url = cms.get_url(old)
				t.sleep(0.5)
				cms.save_images(
					new_ID=new, 
					url=url, 
					path=dst_path
				)
			elif event == 'Text':
				for x in SUBS.keys():
					if values[x] == True:
						award = x
				cms.get_info(
					SUBS=SUBS,
					new_ID=new,
					old_ID=old,
					award=award,
					path=dst_path
				)
		print('# finished run\n')

def article_links(cms, NIDs_input):
	if not NIDs_input:
		print('No new dupe IDs entered')
	else:
		IDs = [int(x) if len(x) == 6 else print(x, 'ID not valid 6 digits') for x in NIDs_input.strip().split('\n')]
		for i in IDs:
			cms.edit_id(i)
			print(cms.get_url(i))			

def ID_selection(SUBS, cms):
	layout = [
		# [sg.Output(size=(140,18))],
		[sg.Frame(layout=[*[[sg.Radio(x, 'Award', key=x, default=True)] for x in SUBS.keys()]], # .upper().split(' ')[0]
			title='Award',
			title_color='white')],
		[sg.Text('Paste destination path:')],
		[sg.InputText(do_not_clear=True, key='DST')], # values[5]
		[sg.Text('Paste OLD dupe IDs:')],
		[sg.InputText(do_not_clear=True, key='OIDS')],
		[sg.Text('Paste NEW dupe IDs:')],
		[sg.InputText(do_not_clear=True, key='NIDS')],
		[sg.Button('Text'), sg.Button('Images'), sg.Button('Links'), sg.Cancel()]
	]
	window = sg.Window('Article Links',
								layout,
								keep_on_top=True,
								grab_anywhere=True)
	while True:
		event, values = window.read()
		if event in ('Cancel', None):
			break
		if event == 'Text' or event == 'Images':
			dupe_assets(SUBS, cms, event, values)
		if event == 'Links':
			article_links(cms, NIDs_input=values['NIDS'])

	window.close()

def main():
	"""
	For proofing dupe articles easier.

	Text needs Path, OLD dupe ids and NEW Dupe ids
	"""
	cms = CMSBot()

	with open('substitutes.json') as f:
		SUBS = json.load(f)

	try:
		ID_selection(SUBS, cms)
	except NoSuchElementException as e:
		print('Could not find elementn', e)
	except Exception:
		raise
	finally:
		cms.bot.quit()

if __name__ == '__main__':
	main()