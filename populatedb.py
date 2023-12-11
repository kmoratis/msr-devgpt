import os
import csv
import json
import codecs
from libs.dbmanager import DBManager
from properties import datasetpath, snapshot, dbpath
from libs.preprocessing import get_subpath, collection_preprocessing, links_preprocessing, remove_duplicates
from libs.download import download_commits_content

# Connect to database
dbmanager = DBManager(dbpath)
dbmanager.drop_db()

# Find snapshots
snapshots = [filename for filename in os.listdir(datasetpath) if filename.startswith("snapshot")]

print("\nLoading " + snapshot)
snapshotpath = os.path.join(datasetpath, snapshot)

# Create set to store the links that need to be dropped (bad status code, no code blocks detected, or non utf-8 characters)
linkstodrop = set()

# --- Discussion sharings collection ---
print("Loading discussions")
with codecs.open(get_subpath(snapshotpath, 'discussion'), 'r', 'utf-8') as infile:
	data = json.load(infile)
collection_preprocessing(data, "discussion", linkstodrop) 
dbmanager.add_data("discussions", data['Sources'])

# --- Pull-request sharings collection ---
print("Loading pull requests")
with codecs.open(get_subpath(snapshotpath, 'pr'), 'r', 'utf-8') as infile:
	data = json.load(infile)
collection_preprocessing(data, "pull-req", linkstodrop)
dbmanager.add_data("pull_requests", data['Sources'])

# --- Issue sharings collection ---
print("Loading issues")
with codecs.open(get_subpath(snapshotpath, 'issue'), 'r', 'utf-8') as infile:
	data = json.load(infile)
collection_preprocessing(data, "issue", linkstodrop)
dbmanager.add_data("issues", data['Sources'])

#--- Commit sharings collection ---
print("Loading commits")
with codecs.open(get_subpath(snapshotpath, 'commit'), 'r', 'utf-8') as infile:
	data = json.load(infile)
data['Sources'], duplicatelinks = remove_duplicates(data['Sources'], 'Sha')
collection_preprocessing(data, "commit", linkstodrop)
dbmanager.add_data("commits", data['Sources'])

# --- File sharings collection ---
print("Loading files")
with codecs.open(get_subpath(snapshotpath, 'file'), 'r', 'utf-8') as infile:
	data = json.load(infile)
collection_preprocessing(data, "file", linkstodrop)
dbmanager.add_data("files", data['Sources'])

# --- Hacker-news sharings collection ---
print("Loading hacker news")
with codecs.open(get_subpath(snapshotpath, 'hn'), 'r', 'utf-8') as infile:
	data = json.load(infile)
collection_preprocessing(data, "hacker-news", linkstodrop)
dbmanager.add_data("hacker-news", data['Sources'])

# --- Link sharing collection ---
print("Loading links")
with codecs.open(get_subpath(snapshotpath, 'Link'), 'r', 'utf-8') as infile:
	data = csv.DictReader(infile)
	validdata = links_preprocessing(data, linkstodrop, duplicatelinks)
	dbmanager.add_data("links", validdata)

# Enrich commits collection with commit content
print("Downloading commits content")
commitdocuments = dbmanager.get_all_documents("commits")
updates = download_commits_content(commitdocuments)

# Update the commits collection
if updates != -1: # GitHub's Rate-Limit reached
	for update in updates:
		document_id = update['_id']
		filter_condition = {'_id': document_id}
		update_data = {'$set': {'CommitContent': update['CommitContent']}}
		dbmanager.update("commits", filter_condition, update_data)
else:
	print('Download failed')

# Close the DB connection
dbmanager.close()
