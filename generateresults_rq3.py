import os
import numpy as np
import matplotlib.pyplot as plt
import json
from properties import dbpath, resultspath
from libs.dbmanager import DBManager

""" Generate diagram for RQ-3 """

# Connect to database
dbmanager = DBManager(dbpath)
db = dbmanager.db
# Create a folder to store the results if it doesn't exist
results_folder = resultspath
os.makedirs(results_folder, exist_ok=True)

# Load annotations from file
with open('annotations.txt', 'r') as file:
	# Load the JSON data from the file into a dictionary
	annotations = json.load(file)

before_after_diff = []
# Get commits
for commit in db["commits"].find({"AnalysisFeatures": {"$exists": True}}):
	# Keep only the entries of class `improve this code` (2)
	if annotations[commit['URL']] == "2":
		for commited_file in commit['AnalysisFeatures']['FileAnalysis']:
			if isinstance(commited_file['QualityAnalysis'], dict):
				# Keep only the entries where previous version exists
				if commited_file['QualityAnalysis']['PreviousContent']:
					diff = commited_file['QualityAnalysis']['Current'] - commited_file['QualityAnalysis']['Previous']
					before_after_diff.append(diff)

# Create a list of differences with zeros removed
before_after_diff_nz = [a for a in before_after_diff if a]

# Create the bar chart of differences
fig, ax = plt.subplots(figsize=(4.85, 3))

# Adjust the white space around the figure
plt.subplots_adjust(bottom=0.15)

before_after_diff_nz = np.array(before_after_diff_nz)

# Plotting the data with two different colors
added_violations = np.where(before_after_diff_nz > 0, before_after_diff_nz, 0)
removed_violations = np.where(before_after_diff_nz < 0, before_after_diff_nz, 0)

bars_added = ax.barh(range(len(before_after_diff_nz)), added_violations, color='green', label='Violations\nIncreased')
bars_removed = ax.barh(range(len(before_after_diff_nz)), removed_violations, color='red', label='Violations\nDecreased')

# Set labels
ax.set_xlabel('Change in Violations', fontsize=13)
ax.set_ylabel('Case Index', fontsize=13)

# Calculate new x-axis limits based on the data
data_max = np.max(np.abs(before_after_diff_nz))
rounded_max = 5 * round((data_max + 5) / 5)

# Set ticks and labels based on the rounded values
ticks = np.arange(-rounded_max, rounded_max + 1, 5)
ax.set_xticks(ticks)
ax.set_xticklabels([str(t) for t in ticks])

# Extend the x-axis range a little bit from the right
current_xlim = ax.get_xlim()
new_xlim = (current_xlim[0] - 2, current_xlim[1] + 2)
ax.set_xlim(new_xlim)

plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(results_folder, 'RQ3ViolationDifference.eps'), format='eps')
plt.savefig(os.path.join(results_folder, 'RQ3ViolationDifference.pdf'), format='pdf')
# plt.show()
