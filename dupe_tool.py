import PySimpleGUI as sg, json
from CMSBot import CMSBot

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

				cms.save_images(path=dst_path,
								new_ID=new,
								url=url)

			elif event == 'Text':
				
				for x in SUBS.keys():
					if values[x] == True:
						award = x

				body_html, summary_text, abs_fn, htm_fn = cms.get_content(path=dst_path,
																		new_ID=new)
				amended_html = amend_content(content=body_html,
												award=award,
												new_ID=new,
												old_ID=old,
												SUBS=SUBS)
				# write summary text to new txt file named after new ID
				# write html text to new htm file named after new ID
				[write_file(k, v) for k, v in [(abs_fn, summary_text),(htm_fn, amended_html)]]

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
			dupe_assets(cms=cms,
						SUBS=SUBS, 
						event=event, 
						values=values)
		if event == 'Links':
			article_links(NIDs_input=values['NIDS'],
								cms=cms)

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
	except Exception:
		raise
	finally:
		cms.bot.quit()

if __name__ == '__main__':
	main()