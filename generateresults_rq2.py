import os
import numpy as np
import matplotlib.pyplot as plt
import json
from collections import defaultdict
from properties import dbpath, resultspath
from libs.dbmanager import DBManager
import re

""" Generate diagrams for RQ-2 """

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

""" Figure 1: Histogram of total violations found in JS code blocks """
violations = []

# Get all commits that contain JS generated code
for commit in db["commits"].find({'ChatgptSharing.Conversations.ListOfCode.Type': 'javascript'}):
	# Keep only the commits of class `write me this code` (1)
	if annotations[commit['URL']] == "1":
		sharing  = commit['ChatgptSharing'][0] # all commits contain only one shared link
		for conversation in sharing.get("Conversations", []):
			for listofcode in conversation["ListOfCode"]:
				if listofcode["Type"] == "javascript" and "Violations" in listofcode:
					violations.append(listofcode["Violations"]["Total"])

# Create the histogram of violations found in all JS blocks
fig = plt.figure(1, figsize=(4.85, 2.62))

# Adjust the white space around the figure
plt.subplots_adjust(bottom=0.15)

bins = list(range(min(violations), max(violations) + 2))
plt.hist(violations, bins=bins, edgecolor='black')
plt.xticks(np.array(bins[:-1]) + 0.5, bins[:-1])
# Set the x-axis limits
plt.xlim(min(violations) - 0.5, max(violations) + 1.5)
# Add labels and title
plt.xlabel('Number of Violations', fontsize=13)
plt.ylabel('Frequency', fontsize=13)

# Save the plot to results
plt.tight_layout()
plt.subplots_adjust(bottom=0.2, top=1)
plt.savefig(os.path.join(results_folder, 'RQ2TotalViolations.eps'), format='eps')
plt.savefig(os.path.join(results_folder, 'RQ2TotalViolations.pdf'), format='pdf')

""" Figure 2: Pie chart of violation categories """
violations_categories = defaultdict(int)

# Get all commits that contain JS generated code
for commit in db["commits"].find({'ChatgptSharing.Conversations.ListOfCode.Type': 'javascript'}):
	# Keep only the commits of class `write me this code` (1)
	if annotations[commit['URL']] == "1":
		sharing  = commit['ChatgptSharing'][0] # all commits contain only one shared link
		for conversation in sharing.get("Conversations", []):
			for listofcode in conversation["ListOfCode"]:
				if listofcode["Type"] == "javascript" and "Violations" in listofcode:
					# Add number of each violation category to the appropriate value in the dict
					for cat, viol_num in listofcode["Violations"]['ViolationsByCat'].items():
						violations_categories[cat] += viol_num

# Create the pie chart
sorted_violations_categories = dict(sorted(violations_categories.items(), key=lambda item: item[1], reverse=True))
fig, ax = plt.subplots(figsize=(4.85, 2.42))

wedges, texts, autotexts = ax.pie(sorted_violations_categories.values(), labels=[''] * len(sorted_violations_categories),
                                   autopct='%1.1f%%', startangle=90)

plt.axis('equal')

# Create legend using proxy artists
legend_labels = [' '.join(re.sub('([A-Z]+)', r' \1', category).split()) for category in sorted_violations_categories.keys()]
prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors[i], markersize=10,
                            label=label) for i, label in enumerate(legend_labels)]

# Move the plot to the right to avoid overlap with the legend
plt.subplots_adjust(left=0)

# Display legend
ax.legend(handles=legend_handles, bbox_to_anchor=(1.35, 1), loc='upper right')

plt.tight_layout()
plt.subplots_adjust(bottom=0.2, top=1)
plt.savefig(os.path.join(results_folder, 'RQ2ViolationCategories.eps'), format='eps')
plt.savefig(os.path.join(results_folder, 'RQ2ViolationCategories.pdf'), format='pdf')
# plt.show()
