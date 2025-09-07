import os
import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS credentials and bucket details
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

# Directory containing images
image_directory = "public/vessel_images"

# List files in S3 bucket
def list_s3_files():
    try:
        response = s3_client.list_objects_v2(Bucket=AWS_BUCKET_NAME)
        if "Contents" in response:
            s3_files = [obj["Key"] for obj in response["Contents"]]
            print("Files in S3 bucket:")
            for file in s3_files:
                print(file)
            return s3_files
        else:
            print("No files found in the S3 bucket.")
            return []
    except Exception as e:
        print(f"Failed to list files in S3 bucket: {e}")
        return []

# Compare local files with S3 files
def compare_files():
    local_files = [
        os.path.relpath(os.path.join(root, file), image_directory)
        for root, _, files in os.walk(image_directory)
        for file in files
        if file.endswith((".png", ".jpg", ".jpeg"))
    ]
    s3_files = list_s3_files()

    missing_files = [file for file in local_files if file not in s3_files]
    if missing_files:
        print("The following files were not uploaded to S3:")
        for file in missing_files:
            print(file)
    else:
        print("All files were uploaded successfully!")

# Run the comparison
if __name__ == "__main__":
    compare_files()