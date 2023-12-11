# msr-devgpt
Analyzing ChatGPT code quality on DevGPT dataset

This repository contains all code and instructions required to reproduce the outcomes of our analysis.

## Instructions
Our analysis is applied to the DevGPT dataset, which is available either on [GitHub](https://github.com/NAIST-SE/DevGPT) or [Zenodo](https://zenodo.org/records/8304091). The first step is to clone this repository and also download the DevGPT dataset. Then, inside the project's folder, create a `.env` file, following the format specified in the `.env.sample` file. Set the `DBPATH`, `DATASETPATH`, and `WORKINGSNAPSHOT` variables appropriately.

### Populating a MongoDB database
This step populates a MongoDB database (MongoDB can be downloaded [here](https://www.mongodb.com/try/download/community)) and performs the preprocessing of the data. Also, it enriches the dataset with additional information about the commits collection, obtained through the GitHub API.

To execute this step, run the `populatedb.py` script.

Note: To download the information through the GitHub API, you'll need to generate a Personal Access Token on GitHub. Ensure that this token has the following permissions: read:user, repo, and user:email. Save this token to your `.env` file for authentication to increase GitHub's API rate limit.

### Analyzing the data
This step performs the basic analysis of the dataset.

To execute this step, run the `analyzedata.py` script.

#### Requirements: 
Before executing this script, ensure you have the following prerequisites in place:
- Java Installation:
  Make sure Java is installed on your system. If not, you can download it [here](https://www.java.com/en/).
- Simian Tool:
  Download and set up the Simian tool for code similarity analysis. Obtain Simian [here](https://simian.quandarypeak.com/).
- PMD Tool:
  Download and set up the PMD Tool from [here](https://pmd.github.io/).
- Configure your environment:
  Add the path to Java, Simian, and PMD to your `.env` file, following the format specified in the `.env.sample` file.

### Generating the distribution of the conversation categories in the dataset
This step calculates and prints the distribution of conversation categories based on annotations in the dataset.

To execute this step, run the `generatecategorydistribution.py` script.

### Generating the results
This step generates the appropriate results and figures to answer the main research questions of our analysis.
Before executing the scripts below, set the `RESULTSPATH` variable in the `.env` file to the folder where the result figures should be saved.

To execute this step, run the following scripts:
- `generateresults_rq1.py`
- `generateresults_rq2.py`
- `generateresults_rq3.py`
