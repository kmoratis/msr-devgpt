import os
from properties import dbpath
from libs.dbmanager import DBManager
from libs.codeanalysis import extract_commit_features
from libs.utils import detect_language
from libs.codequality import get_block_violations

# Connect to database
dbmanager = DBManager(dbpath)

# Create a directory for temporary files
temp_dir = "./temp_files"
os.makedirs(temp_dir, exist_ok=True) 

print("\nAnalyzing data")

print("Extracting commit features")
# Get all chatgpt links that relate to commits
for l, link in enumerate(dbmanager.db['links'].find({'MentionedSource': 'commit'}, {'_id': False})):

	# Get the commit object
	commit = dbmanager.db['commits'].find_one({'URL': link['MentionedURL']})

	# Call function to detect the programming language
	language, updatedsharing = detect_language(commit)

	# If language was identified, save it to db
	if language:
		dbmanager.update('commits', {'_id': commit['_id']}, {'$set': {'Language': language}})

	# If information about generated code blocks was modified (entries from repo: tisztamo/Junior), update the db
	if updatedsharing:
		commit['ChatgptSharing'][0] = updatedsharing
		# Define the query to update ChatgptSharing to db
		query = {'$set': {f'ChatgptSharing.{0}': updatedsharing}}
		dbmanager.update('commits', {'_id': commit['_id']}, query)

	# Call function to extract the analysis features of the commit
	features = extract_commit_features(commit, temp_dir)
	# Add commit's features to the database
	dbmanager.update('commits', {'_id': commit['_id']}, {'$set': {'AnalysisFeatures': features}})

	# Add attribute to the local variable of the commit
	commit['AnalysisFeatures'] = features

	# Call function to calculate the quality violations for every generated code block in the shared conversation link
	commitsharing = get_block_violations(commit)

	# If quality analysis finished sucessfully, update the db
	if commitsharing != -1:
		query = {'$set': {f'ChatgptSharing.{0}': commitsharing}}
		dbmanager.update('commits', {'_id': commit['_id']}, query)

# Remove the directory with temporary files
os.rmdir(temp_dir)

# Close the DB connection
dbmanager.close()
