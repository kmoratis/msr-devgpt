import requests
import json
from properties import githubapikey

def download_commits_content(commits):
	"""
	This function takes a list of commits and downloads the content of each, using the GitHub API.
	
	:param commits: A list of dictionaries, where each dictionary represents a commit.
	:returns: A list of dictionaries containing the updates to be made to the 'commits' collection. 
	Each dictionary contains the commit's ID and content attribute. If API call was not successful 
	or GitHub's API remaining request number is low, return (-1)
	"""
	
	# Define a list to store dictionaries with the commit's ID and content attribute
	update_list = []

	for commit in commits:
	
		update_dict = {}

		# Get commit's ID and store it to dictionary
		update_dict['_id'] = commit['_id']

		# Get commit's reponame and sha 
		reponame = commit['RepoName']
		sha = commit['Sha']
		apiurl = "https://api.github.com/repos/" + reponame + "/commits/" + sha

		# Use GitHub token to achieve better maximum API call rate
		headers = {}
		headers['Authorization'] = 'token ' + githubapikey

		try:
			# API call to get GitHub's commit information
			response = requests.get(apiurl, headers = headers)

			# Store API response to update's dictionary
			update_dict['CommitContent'] = json.loads(response.text)

			# Add update dictionary to update list
			update_list.append(update_dict)

			# Check GitHub's API call rate limit
			if 'X-RateLimit-Remaining' in response.headers:
				if int(response.headers['X-RateLimit-Remaining']) <= 10:
					print("GitHub: X-RateLimit-Remaining is low, please try again later.")
					return -1
		except:
			print("Bad request response on commit:", commit['NumericID'])
			return -1
		
	return update_list
