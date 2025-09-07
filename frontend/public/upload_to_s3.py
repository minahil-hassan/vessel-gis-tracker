import os
import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS credentials and bucket details
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Directory containing images
image_directory = "public/vessel_images"

# Upload images to S3
def upload_images_to_s3():
    for root, _, files in os.walk(image_directory):
        for file in files:
            if file.endswith((".png", ".jpg", ".jpeg")):  # Filter image files
                file_path = os.path.join(root, file)
                s3_key = os.path.relpath(file_path, image_directory)  # Key in S3 bucket

                try:
                    s3_client.upload_file(
                        file_path,
                        s3_key,
                        ExtraArgs={"ACL": "public-read"}  # Make the file publicly readable
                    )
                    print(f"Uploaded {file_path} to s3://{s3_key}")
                except Exception as e:
                    print(f"Failed to upload {file_path}: {e}")

# Run the upload function
if __name__ == "__main__":
    upload_images_to_s3()