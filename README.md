# GitHub Archive Analysis
This is a data engineering pipeline built to ingest data from the [GitHub Archive](https://www.gharchive.org/) website and analyze all fork events on GitHub.

## Prerequisites
To run this project, you will need
* Google Cloud Platform Account
* Terraform CLI

## Technologies Used
* Docker
* Google Cloud Storage
* Google BigQuery
* Google Data Studio
* Apache Airflow
* Apache Spark (Dataproc)
* dbt (Data Build Tool)

## Setup

Clone the repository in your local machine.

```bash
git clone https://github.com/kprakhar27/streamify.git
```

### Google Cloud CLI Setup

For this course, we'll use a free gcloud version (upto EUR 300 credits). 

1. Create an account with your Google email ID 
2. Setup your first [project](https://console.cloud.google.com/) if you haven't already
    * eg. "GHArchive Analysis", and note down the "Project ID" (we'll use this later when deploying infra with TF)
3. Setup [service account & authentication](https://cloud.google.com/docs/authentication/getting-started) for this project
    * Grant `Viewer` role to begin with.
    * Download service-account-keys (.json) for auth.
4. Download [SDK](https://cloud.google.com/sdk/docs/quickstart) for local setup
5. Set environment variable to point to your downloaded GCP keys:
   ```shell
   # Set project id
   gcloud config set project PROJECT-ID
   
   export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"
   
   # Refresh token/session, and verify authentication
   gcloud auth application-default login
   ```
### Terraform Setup


## Usage

* Terraform - [Setup]()
* SSH - [Setup]()

## Contributing
Contributions are welcome! If you find any issues or have any suggestions for improvement, please create an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/kprakhar27/GitHub-Archive-Analysis/blob/main/LICENSE) file for details.