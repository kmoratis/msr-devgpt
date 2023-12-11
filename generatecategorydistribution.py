import json
from collections import defaultdict

""" Calculate the Conversation Category Distribution of the Dataset """

# Load annotations from file
with open('annotations.txt', 'r') as file:
	# Load the JSON data from the file into a dictionary
	annotations = json.load(file)

# Define a dictionary matching each annotation number with a scenario category	
annotationmatch = {
	"-1": "None",
	"0": "Example Usage", 
	"1": "Write me this code", 
	"2": "Improve this code", 
	"3": "Fix this issue", 
	"4": "Explain this code", 
	"5": "Other" }

# Define a dictionary to store the annotation category and the number of its occurencies
annotations_counts = defaultdict(int)

# Count the number of occurencies of each category
for annotationnum in annotations.values():   
	annotations_counts[annotationmatch[annotationnum]] += 1

# Sort categories by the number of occurrences
sorted_categories = sorted(annotations_counts.keys(), key=lambda x: annotations_counts[x], reverse=True)
sorted_occurrences = [annotations_counts[category] for category in sorted_categories]

# Print the results
print("\nConversation Category Distribution of the Dataset:\n")
for category, count in zip(sorted_categories, sorted_occurrences):
    print(f"{category}: {count}")
