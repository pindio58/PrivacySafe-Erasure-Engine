import os
import json
import logging
import boto3
import psycopg2
from botocore.exceptions import ClientError

# 1. Configure structured JSON logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": self.formatTime(record, self.datefmt),
        }
        # Inject AWS request context if available
        if hasattr(record, "aws_request_id"):
            log_record["request_id"] = record.aws_request_id
        
        # Capture tracebacks cleanly if an exception occurred
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

# Initialize logger
logger = logging.getLogger("anonymizer_lambda")
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

# Ensure handler uses our JSON formatter
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

s3_client = boto3.client('s3')

S3_BUCKET = os.environ.get('AUDIT_BUCKET', 'audit-pipeline-bucket')
S3_KEY = os.environ.get('HASH_SALT_REGISTRY', 'security/salt.txt') + "/salt.txt"

def lambda_handler(event, context):
    # 2. Inject AWS request ID dynamically into the logger filter context
    log_extra = {"aws_request_id": context.aws_request_id}
    logger = logging.LoggerAdapter(logging.getLogger("anonymizer_lambda"), log_extra)

    logger.info("Lambda execution started.", extra={"remaining_time_ms": context.get_remaining_time_in_millis()})

    try:
        logger.debug(f"Incoming Event: {json.dumps(event)}")
    except Exception:
        logger.debug(f"Incoming Event (raw conversion failed): {event}")

    # STEP 1 - Parsing request
    try:
        if "user_id" in event:
            user_id = event["user_id"]
        else:
            body = json.loads(event.get("body", "{}"))
            user_id = body.get("user_id")

        if not user_id:
            logger.error("Request validation failed: missing user_id parameter")
            return build_response(400, {"error": "Missing user_id parameter"})
            
        logger.info(f"Successfully parsed user_id: {user_id}")

    except Exception:
        logger.exception("Failed to parse incoming request payload")
        return build_response(400, {"error": "Invalid request format"})

    # STEP 2 & 3 - Reading salt from S3
    try:
        logger.info(f"Retrieving salt resource from S3://{S3_BUCKET}/{S3_KEY}")
        s3_response = s3_client.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        salt_value = s3_response["Body"].read().decode("utf-8").strip()
        logger.info("Successfully fetched salt configuration")

    except ClientError:
        logger.exception(f"AWS S3 ClientError while fetching key {S3_KEY}")
        return build_response(500, {"error": "Internal server configuration storage error"})

    # STEP 4 to 8 - Database interaction
    conn = None
    try:
        logger.info(
            f"Initiating PostgreSQL connection to host={os.environ.get('PGHOST')} "
            f"database={os.environ.get('DBNAME')} user={os.environ.get('PGUSER')}"
        )

        conn = psycopg2.connect(
            host=os.environ["PGHOST"],
            dbname=os.environ["DBNAME"],
            user=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"],
            connect_timeout=5
        )
        conn.autocommit = True
        logger.info("Database connection handshake successful")

        with conn.cursor() as cur:
            logger.info("Executing database procedure: ecommerce.anonymize_user")
            cur.execute(
                """
                CALL ecommerce.anonymize_user(%s::uuid, %s::varchar);
                """,
                (user_id, salt_value)
            )
        
        
        # conn.commit()
        logger.info("Database transaction committed successfully")

    except Exception:
        # logger.exception automatically captures the full stack trace/error type
        logger.exception("Database transaction failed during execution")
        
        if conn:
            logger.warning("Rolling back uncommitted database changes")
            conn.rollback()

        return build_response(500, {"error": "Database processing failure"})

    finally:
        if conn:
            logger.info("Terminating open database connection")
            conn.close()

    logger.info("Lambda execution completed successfully")
    return build_response(
        200,
        {
            "message": "User safely anonymised and analytics mapping broken successfully.",
            "user_id": user_id
        }
    )

def build_response(status_code: int, body_dict: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body_dict)
    }
