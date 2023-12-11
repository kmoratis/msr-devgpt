import tempfile
import subprocess
from properties import pmd

def get_file_violations(current_content, prev_content, file_extension):
	"""
	This function checks the quality violations in the current and previous versions of a code file using the PMD tool.
	
	:param current_content: A string containing the current version of the code file
	:param prev_content: A string containing the previous version of the code file
	:param file_extension: A string that represents the file's extension
	:returns: A dictionary that contains the number of quality violations found for each version of the
	code. The keys of the dictionary are "Current" and "Previous", and the values are the total number
	of violations found for each version.
	If the PMD-check finished with some error code, return (-1)
	"""

	# Define dictionary to store number of violations found for each version
	violations = {}
	version_list = {"Current": current_content, "Previous": prev_content}

	for version, file_content in version_list.items():

		# Create temporary file to store the code file's content
		with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='cp437', errors="ignore", suffix=file_extension) as temp_file:
			temp_file.write(file_content)

		# Get temporary file's path
		temp_file_path = temp_file.name

		# Create the ruleset relative path according to the file's language
		ruleset_path = f"pmdrulesets\javascriptruleset.xml"

		# Define the PMD check command
		cpd_command = f"{pmd} check {temp_file_path} -f text --no-cache -R {ruleset_path}"
		
		# Run the command and capture the output
		output = subprocess.run(cpd_command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		# If quality violations found
		if output.returncode == 4:
			# Compute the total number of violations and save it to dictionary
			output_message = output.stdout
			total_violations = len(output_message.splitlines())
			violations[version] = total_violations

		# If no quality violations found
		elif output.returncode == 0: 
			violations[version] = 0
		
		# If PMD finished with an error code
		else:
			print('Error in before-after quality analysis')
			return -1

	return violations


def get_block_violations(dbobj):
	"""
	This function calculates the number of quality violations in the code blocks of a shared
	conversation and returns the updated conversation object.
	
	:param dbobj: A database object that contains the information about a commit
	:returns: The updated `sharing` object with the added `Violations` attribute for each supported
	code block in each conversation.
	The function returns (-1) if the PMD finished with error.
	"""

	# Get the information of the shared conversation
	sharing = dbobj['ChatgptSharing'][0]

	# Define a dictionary containing the 'name': 'category' of the supported violations for javascript
	javascript_violations = {'GlobalVariable': 'BestPractices',
								  'AvoidWithStatement': 'BestPractices',
								  'ConsistentReturn': 'BestPractices', 
								  'ScopeForInVariable': 'BestPractices',
								  'UseBaseWithParseInt': 'BestPractices',
								  'AssignmentInOperand': 'CodeStyle',
								  'ForLoopsMustUseBraces': 'CodeStyle',
								  'IfElseStmtsMustUseBraces': 'CodeStyle', 
								  'IfStmtsMustUseBraces': 'CodeStyle', 
								  'NoElseReturn': 'CodeStyle', 
								  'UnnecessaryBlock': 'CodeStyle', 
								  'UnnecessaryParentheses': 'CodeStyle',
								  'AvoidTrailingComma': 'ErrorProne',
								  'EqualComparison': 'ErrorProne',
								  'InnaccurateNumericLiteral': 'ErrorProne'
								  }

	# For every generated code block in every conversation of the shared link, calculate the violations
	for i, conversation in enumerate(sharing.get('Conversations', [])):
		# Define variable to specify whether the content of the conversation changed, in order to save it
		conv_changed = False
		for j, code in enumerate(conversation['ListOfCode'].copy()):

			# Initialize variables
			total_violations = 0
			violations_by_cat = {'BestPractices': 0, 'CodeStyle': 0, 'ErrorProne': 0}

			# If type of code is supported ( JavaScript )
			if code['Type'] == 'javascript':

				# Create temporary file to store the code file's content
				with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='cp437', errors="ignore", suffix='.js') as temp_file:
					temp_file.write(code['Content'])

				# Get temporary file's path
				temp_file_path = temp_file.name

				# Create the ruleset relative path according to the file's language
				ruleset_path = f"pmdrulesets\{code['Type']}ruleset.xml"

				# Define the PMD check command
				cpd_command = f"{pmd} check {temp_file_path} -f text --no-cache -R {ruleset_path}"
				
				# Run the command and capture the output
				output = subprocess.run(cpd_command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

				# If quality violations found
				if output.returncode == 4:
					# Extract the violations by category found and save it to dictionary
					output_message = output.stdout

					# For each supported violation
					for name, category in javascript_violations.items():
						# Check how many times it exist in the output message
						count = output_message.count(name)
						if count:
							total_violations += count
							violations_by_cat[category] += count

					# Formulate the final dictionary containing the information to be stored to the db
					code['Violations'] = {'Total': total_violations}
					code['Violations'].update({'ViolationsByCat': violations_by_cat})
					conversation['ListOfCode'][j] = code
					conv_changed = True 

				elif output.returncode == 0:
					code['Violations'] = {'Total': total_violations}
					code['Violations'].update({'ViolationsByCat': violations_by_cat})
					conversation['ListOfCode'][j] = code
					conv_changed = True
				
				# If PMD finished with an error code
				else:
					print('Error in generated-code quality analysis')
					return -1
		
		if conv_changed:
			sharing['Conversations'][i] = conversation

	return sharing
