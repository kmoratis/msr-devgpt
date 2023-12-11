import re
from pygments import lexers
from collections import Counter

def get_content_from_patch(patch, version):
	"""
	This functions extracts the required version of the code file's content from the commit patch.
	
	:param patch: A string that represents the patch of a GitHub's commit for a specific file. 
	It follows the unified diff format, which shows the differences between two versions of a file
	:param version: A string used to specify which version of the file's content to
	retrieve from the patch. It can have two possible values: 'current' or 'previous'
	:returns: the content of the file based on the given patch and version.
	"""

	patch_lines = patch.splitlines()
	content_lines = []

	if version == 'current':
		# Specify which patch lines belongs to current version of the file
		for line in patch_lines:
			if line[0] == '+':
				content_lines.append(line[1:])
			elif line[0] != '@' and line[0] != '-':
				content_lines.append(line)

	elif version == 'previous':
		# Specify which patch lines belongs to previous version of the file
		for line in patch_lines:
			if line[0] == '-':
				content_lines.append(line[1:])
			elif line[0] != '@' and line[0] != '+':
				content_lines.append(line)

	content = '\n'.join(content_lines)
	return content
	

def get_file_extension(filename):
	"""
	This function attempts to determine the file extension of a given filename by
	using the `get_lexer_for_filename` function from the `lexers` module.
	
	:param filename: A string that represents the name of a file, including its extension
	:returns: The file extension of the given filename if it can be determined by the `lexers` module. 
	If the file extension cannot be determined or an exception occurs, it returns `None`.
	"""

	try:
		lexer = lexers.get_lexer_for_filename(filename)
		return lexer.filenames[0]
	except Exception as e:
		return None


def detect_language(dbobj):
	"""
	This function detects the most common programming language of the codes that were generated 
	in the shared links of a given `dbobj` object. Also, it checks if the name of the repo is `tisztamo/Junior`,
	and if so it modifies the content of `ChatgptSharing` objects and returns them, if any code blocks were changed.
	
	:param dbobj: The `dbobj` parameter is a dictionary object that contains information about a
	commit object and its associated Chatgpt dialogues.
	:returns: The function `detect_language` returns two values: `programming_language` and
	`dbobj['ChatgptSharing'][0]` (if any generated code block needed to be modified).
	"""

	# Initialize variables
	codeblocks_changed = False
	programming_language = 'Unknown'

	# Commits in this repo, were created using some particular prompting so we are extracting 
	# only the useful information (javascript), for our analysis, from the chatgpt generated blocks
	if dbobj['RepoName'] == 'tisztamo/Junior':

		# Define regular expression to match the JavaScript part contained in the 'sh' code block
		regex = re.compile(r'import[\s\S]*?(?=\nEOF)')

		for i, conversation in enumerate(dbobj['ChatgptSharing'][0]['Conversations'].copy()):

			modified_code_list = []
			
			for code in conversation['ListOfCode']:

				if code['Type'] in ['sh', 'bash']:
					# Find all JavaScript parts
					matches = regex.finditer(code['Content'])

					# Loop through each match and create a code block for the JavaScript part
					for match in matches:
						javascript_part = match.group(0)
						code['Type'] = 'javascript'
						code['Content'] = javascript_part
						modified_code_list.append(code)
						codeblocks_changed = True
				else:
					modified_code_list.append(code)

			# If JS parts found, update the list of code in the shared link
			if modified_code_list:
				conversation['ListOfCode'] = modified_code_list
				dbobj['ChatgptSharing'][0]['Conversations'][i] = conversation

	# Get the coding language of all code blocks generated in the specific Chatpgt dialogue
	gen_code_langs = [
		code['Type']
		for conversation in dbobj['ChatgptSharing'][0].get('Conversations', [])
		for code in conversation['ListOfCode']	
		if code.get('Type') is not None
	]

	if gen_code_langs:
		# Use Counter to count occurrences of each element in the list
		language_counts = Counter(gen_code_langs)

		# Use the most_common() method to get a list of tuples (element, count),
		most_common_languages = language_counts.most_common()

		# Find the language(s) with the most counts
		max_count = most_common_languages[0][1]
		max_count_languages = [lang for lang, count in most_common_languages if count == max_count]

		# Check if 'javascript' is among the languages with the most counts
		for language in max_count_languages:
			if language == 'javascript':
				programming_language = language
				break
		else:
			# If 'javascript' is not found among the most common, pick the first language (random)
			programming_language = max_count_languages[0]

	return programming_language, dbobj['ChatgptSharing'][0] if codeblocks_changed else None
