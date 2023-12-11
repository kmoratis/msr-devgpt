import os
import regex as re

def get_subpath(snapshotpath, datatype):
	"""
	Returns the subpath within a given snapshot path that contains a specific datatype.
	
	:param snapshotpath: The path to the snapshot directory where the data is stored.
	:param datatype: A string that represents the specific datatype within the snapshot path.
	:returns: the required subpath
	"""
	
	datasubpath = next(subpath for subpath in os.listdir(snapshotpath) if datatype in subpath) 
	return os.path.join(snapshotpath, datasubpath)
    

def contains_invalid_chars(text):
	"""
	Checks if a given text contains any invalid Unicode character.
	
	:param text: The string to check for invalid characters.
	:returns: Boolean. (True) if the input text contains any invalid characters, and (False) otherwise.
	"""
	
	all_unicode_patterns = re.compile(r'[\u0080-\uffef]', re.UNICODE)  # @UndefinedVariable

	valid_patterns = [
		r'[\u0080-\u00FF]', # "Latin-1 Supplement" category
		r'[\u2500-\u257F\u200b\u23a6\u23a4\u23a3\u23a1]', # Box drawing characters
		r'[\u2600-\u26FF\u2B50\ufe0f]', # Miscellaneous Symbols
		r'[\u25A0-\u25FF]', # Geometric shape characters
		r'[\u2190-\u21FF]', # Arrow characters and similar
		r'[\u2200-\u22FF]', # Math symbols and operators
		r'[\u0391-\u03A9\u03B1-\u03C9]', # Greek letters used in math
		r'[\p{P}\p{S}\p{So}]', # "Punctuation Dash" and Symbol characters
		r'[\p{Block=Emoticons}]', # Emoticons Block characters
	]

	valid_patterns = '|'.join(valid_patterns)
	valid_patterns = re.compile(valid_patterns)

	all_unicode_characters = all_unicode_patterns.findall(text)

	for character in all_unicode_characters:
		# If at least one non-valid unicode found, return True
		if not valid_patterns.search(character):
			return True

	return False


def collection_preprocessing(data, datatype, linkstodrop):
	"""
	Checks whether the data contains invalid sources and removes them. Invalid sources are those that contain any of the following:
    - Specific non-UTF-8 characters
    - No valid response codes
    - Conversations that lack at least one code block.
	
	:param data: A dictionary containing the collection of sources.
	:param datatype: A string that specifies the type of data being processed. 
	:param linkstodrop: A set that stores the URLs of the invalid links to be removed from the `links` collection.
	"""
	
	# Create set to store the indexes of invalid sources, in order to delete them
	invalid_sources = set()

	# Check if every source is valid or not
	for i, source in enumerate(data['Sources']):

		# For different data types (commits, discussion, etc), different text fields are checked
		if datatype == "discussion" or datatype == "issue" or datatype == "pull-req":
			# Check if entry's title or body contains contains non utf-8 characters
			if contains_invalid_chars(source['Title']) or contains_invalid_chars(source['Body']):
					invalid_sources.add(i) # Add source's index to invalid sources set
					sharing_urls = [sharing['URL'] for sharing in source['ChatgptSharing']]
					linkstodrop.update(sharing_urls) # Add its shared links to linkstodrop set
					continue # check next source
		
		elif datatype == "commit":
			# Check if entry's message contains non utf-8 characters
			if contains_invalid_chars(source['Message']):
					invalid_sources.add(i)
					sharing_urls = [sharing['URL'] for sharing in source['ChatgptSharing']]
					linkstodrop.update(sharing_urls)
					continue

		elif datatype == "file":
			# Check if entry's commit message contains non utf-8 characters
			if contains_invalid_chars(source['CommitMessage']):
					invalid_sources.add(i)
					sharing_urls = [sharing['URL'] for sharing in source['ChatgptSharing']]
					linkstodrop.update(sharing_urls)
					continue

		elif datatype == "hacker-news":
			if source['Title']: # if Title attribute not null
					# Check if entry's Title contains non utf-8 characters
					if contains_invalid_chars(source['Title']):
						invalid_sources.add(i)
						sharing_urls = [sharing['URL'] for sharing in source['ChatgptSharing']]
						linkstodrop.update(sharing_urls)
						continue

		source_contains_code = False # Variable to check if source contains code blocks

		contains_active_link = False # Variable to store whether reference contains at least one active link

		# Ckeck each Chatgpt shared link
		for sharing in source['ChatgptSharing']:
			# Check status code of the Chatgpt shared link, and keep only success (200)
			if sharing['Status'] != 200:
					linkstodrop.add(sharing['URL'])
					continue # continue to the next dialogue check
			else:
					contains_active_link = True

			# For each conversation in the specific shared link, check if code block exists
			link_contains_code = False
			for conv in sharing['Conversations']:
					if len(conv['ListOfCode']): # check if List of Code is not empty
						link_contains_code = True # if code block found, no need to check the rest of the conversations, so exit loop
						source_contains_code = True
						break

			# If no code blocks are detected in the link, add link to drop set
			if not link_contains_code:
				linkstodrop.add(sharing['URL'])

			# Check if conversation's prompt or answer contains non utf-8 characters
			found = False # variable to exit nested loop
			for conv in sharing['Conversations']:
					if contains_invalid_chars(conv['Prompt']) or contains_invalid_chars(conv['Answer']):
						invalid_sources.add(i)
						sharing_urls = [sharing['URL'] for sharing in source['ChatgptSharing']]
						linkstodrop.update(sharing_urls)
						found = True
						break # exit nested loop
			if found: # if non utf-8 found, no need to check the rest of the dialogues, so exit loop
					break

		# If there are no active links shared at the moment the snapshot was taken, remove source from data
		if not contains_active_link:
			invalid_sources.add(i)

		# If there are no code blocks in any of the shared links, remove source from data
		if not source_contains_code:
			invalid_sources.add(i)

	# Remove invalid sources from data
	for i in sorted(invalid_sources, reverse=True):
		data['Sources'].pop(i)

	# Create a NumericID attribute for valid data
	for i in range(len(data['Sources'])):
		data['Sources'][i] = {'NumericID': i + 1, **data['Sources'][i]}


def remove_duplicates(collection, attribute):
	"""
	This function takes a collection of entries and removes duplicates based on a
	specified attribute, returning the unique entries and a list of duplicate links.
	
	:param collection: A list of dictionaries. Each dictionary represents an entry in the collection
	:param attribute: A string specifying the attribute to be used to determine if there are duplicates
	:returns: Two values: `result` and `duplicate_links`.
	`result` is a list of unique entries from the collection, while `duplicate_links` is a list of URLs
	that correspond to the duplicate entries.
	"""
	
	# Initialize variables
	unique_entries = {}
	result = []
	duplicate_links = []

	# Check all entries of the collection and keep only the first occurence of each entry
	for entry in collection:
		value = entry[attribute]

		if value not in unique_entries:
			unique_entries[value] = True
			result.append(entry)
		else:
			duplicate_links.append(entry['ChatgptSharing'][0]['URL'])

	return result, duplicate_links


def links_preprocessing(data, linkstodrop, duplicatelinks):
	"""
	The function filters a list of links based on whether they were dropped during
	collection preprocessing and returns the filtered list.
	
	:param data: A list of dictionaries, where each dictionary represents a reference link.
	:param linkstodrop: A list of URLs of the links that were dropped during collection preprocessing.
	These links that should not be included in the final list of links
	:param duplicatelinks: A list of URLs that are contained more than one time in the initial list
	:returns: a list of dictionaries that contains only the unique links that were not dropped during
	preprocessing.
	"""

	# Create list to contain the references that should be inserted to the database
	data_to_insert = []

	# Check if entry's Mentioned URL was not dropped during collection_preprocessing
	for row in data:
		if row['URL'] not in duplicatelinks:
			if row['URL'] not in linkstodrop:
				data_to_insert.append(row)
		else:
			duplicatelinks.remove(row['URL'])

	# Create a NumericID attribute for valid links
	for i in range(len(data_to_insert)):
		data_to_insert[i] = {'NumericID': i + 1, **data_to_insert[i]}

	return data_to_insert
