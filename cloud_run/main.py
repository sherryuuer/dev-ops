import csv
import os

from cloudevents.http import from_http
from flask import Flask, request
from google.cloud import bigquery, storage


client = bigquery.Client()
storage_client = storage.Client()

app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():

    # Create a CloudEvent object from the incoming request
    event = from_http(request.headers, request.data)
    # Gets the GCS bucket name from the CloudEvent
    bucket = event.get("subject")
    print(f"Detected change in Cloud Storage bucket: {bucket}")

    bucket_name = 'oh-test'
    file_name = bucket.removeprefix('objects/')
    print(f"Processing file: {file_name} in bucket: {bucket_name}")
    process_file(bucket_name, file_name)

    return (f"Detected change in Cloud Storage bucket: {bucket}, and complate the process", 200)


def process_file(bucket_name, file_name):

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    content = blob.download_as_string().decode('utf-8')

    rows = list(csv.DictReader(content.splitlines()))
    print(f"Rows to insert: {rows}")

    errors = client.insert_rows_json("oh_practice.run_table", rows)

    if errors:
        print("Errors:", errors)
        print("失敗したよ.")
    else:
        print("New rows have been added.")
        print("成功したよ.")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
