import os
import sys
import secrets
import boto3
from pathlib import Path
from dotenv import load_dotenv
from mypy_boto3_s3 import S3Client
from botocore.exceptions import ClientError, NoCredentialsError

# 1. Safely inject the project root directory into sys.path FIRST
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent  # Navigates up to 'root'

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 2. Import your project logger now that sys.path includes the root
from project_utils.logger import get_logger

# Initialize the custom logger
logger = get_logger(__name__)

# 3. Load variables and generate the secure salt
load_dotenv()
logger.info("Environment variables loaded successfully.")

try:
    AUDIT_BUCKET = os.environ['AUDIT_BUCKET']
except KeyError:
    logger.critical("Missing 'AUDIT_BUCKET' key in your .env file!")
    raise

hash_to_be_used = secrets.token_urlsafe(32)

# Setup dynamic paths pointing to project_root/data/
filename = 'salt'

# Initialize S3 client
s3: S3Client = boto3.client('s3')


def push_salt_to_s3(filename: str):
    """Uploads the generated cryptographically secure salt token to AWS S3."""
    key = f"hash_salt_registry/{filename}" if filename.endswith('.txt') else f"hash_salt_registry/{filename}.txt"
    
    logger.info(f"Initiating S3 upload. Target path: s3://{AUDIT_BUCKET}/{key}")
    
    try:
        s3.put_object(
            Bucket=AUDIT_BUCKET,
            Key=key,
            Body=hash_to_be_used,
            ContentType='text/plain'
        )
        logger.info(f"Successfully written salt registry metadata to S3.")
        
    except NoCredentialsError:
        logger.error("Authentication Failed: Local AWS credentials could not be resolved.")
        raise
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            logger.error(f"Configuration Error: The bucket '{AUDIT_BUCKET}' does not exist.")
        elif error_code == 'AccessDenied':
            logger.error(f"IAM Permission Denied: Your user lacks 's3:PutObject' capability for bucket '{AUDIT_BUCKET}'.")
        else:
            logger.error(f"S3 Client Error [{error_code}]: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error occurred during S3 pipeline stream: {e}")
        raise


def main():
    logger.info("Executing PrivacySafe Erasure Engine - Salt Generation Routine.")
    push_salt_to_s3(filename)
    logger.info("Routine execution finished cleanly.")


if __name__ == '__main__':
    main()
