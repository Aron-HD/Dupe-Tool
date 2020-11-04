# Dupe tool

Recent project that helps massively with duplicate content which I'm responsible for.

When we receive a case study that we already have an article for, we reuse the old source code which has already been edited and converted into html to save money. This involves some minor amendments such as changing image links, and swapping out a few `<h3>Headings</h3>`. 

The script has three main functions:

1. Gets url links generated from cms and print them
2. Copies html source code and plain text summary from old cms article
    - creates new directory in specified path named after new article ID
    - runs string replacements on copied content according to old / new award
    - saves edited summary as '.txt' and source code as '.html' in new directory
3. Saves and renames images from old cms article to new directory

**Instructions**

- **Links:** paste a column of IDs into NEW ids input box
- **Text & Images:** both need Path, OLD ids and NEW ids

Currently all three run indepentently for more control, but may link them together.

### ToDo 

- create function to write urls to a csv file or text file
- change SUBS dict as a JSON file and read in
- cut CMSbot class split GUI + other functions and import it as a separate file
- replace GUI window inputs for IDs with multilines and use streamline map / filter

### Completed improvements

- tidied if blocks under window events into functions
- reduced duplication of code around zipping lists under different events
