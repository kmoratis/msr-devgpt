import os
import numpy as np
import matplotlib.pyplot as plt
import json
from properties import dbpath, resultspath
from libs.dbmanager import DBManager

""" Generate diagram for RQ-1 """

# Connect to database
dbmanager = DBManager(dbpath)
db = dbmanager.db

# Create a folder to store the results if it doesn't exist
results_folder = resultspath
os.makedirs(results_folder, exist_ok=True)

prompts_number_until_copy_paste = []

# Load annotations from file
with open('annotations.txt', 'r') as file:
	# Load the JSON data from the file into a dictionary
	annotations = json.load(file)

# Get all commits
for commit in db["commits"].find({"AnalysisFeatures": {"$exists": True}}):
	# Keep only the commits of class `write me this code` (1)
	if annotations[commit['URL']] == "1":
		pnums = []
		for commit_file in commit['AnalysisFeatures']['FileAnalysis']:
			if commit_file['LinesCopied'] > 0:
				pnums.append(commit_file['PromptsBeforeClone'])
		if pnums:
			prompts_number_until_copy_paste.append(max(pnums))

	# Define the max number of the x-axis
	max_value = 20
	
# Create the histogram
fig = plt.figure(figsize=(4.85, 2.62))

bins = list(range(0, max_value+2))  # Including max number in the last bin
clipped_values = np.minimum(prompts_number_until_copy_paste, max_value)

# Create the histogram using the clipped values
hist_values, bin_edges, _ = plt.hist(clipped_values, bins=bins, edgecolor='black')

# Set x-axis ticks and labels
bin_labels = [str(int(bin_edge)) if bin_edge < max_value else '  '+str(max_value)+'+' for bin_edge in bin_edges[:-1]]
bin_ticks = np.arange(len(bin_labels)) + 0.5

plt.xticks(bin_ticks, [''] + bin_labels[1:])  # Set the first label to an empty string
plt.xlim(0.5, max(bin_ticks) + 1)

# Add labels
plt.xlabel('Number of Prompts', fontsize=13)
plt.ylabel('Frequency', fontsize=13)

# Save the plot to results
plt.tight_layout()
plt.subplots_adjust(bottom=0.2, top=1)
plt.savefig(os.path.join(results_folder, 'RQ1NumPromptsBeforeCopying.eps'), format='eps')
plt.savefig(os.path.join(results_folder, 'RQ1NumPromptsBeforeCopying.pdf'), format='pdf')
# plt.show()
