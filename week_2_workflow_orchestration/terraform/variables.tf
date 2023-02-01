locals {
  prefect_bucket = "prefect_taxi"
}

variable "project" {
  description = "Your GCP Project ID"
  default="zoomcamp-olvol3"
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "europe-west6"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "PREFECT_BQ_DATASET_GREEN" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "prefect_taxi_data_green"
}

variable "PREFECT_BQ_DATASET_YELLOW" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "prefect_taxi_data_yellow"
}
