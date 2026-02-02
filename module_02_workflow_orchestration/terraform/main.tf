terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "taxi_data" {
  name          = "${var.project_id}-taxi-data"
  location      = var.region
  force_destroy = true
  storage_class = "STANDARD"
  uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "taxi_dataset" {
  dataset_id = "taxi_data"
  location   = var.region
}
