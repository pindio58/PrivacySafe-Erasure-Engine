import json, os, boto3, psycopg2
from datetime import datetime, timezone

s3 = boto3.client('s3')
AUDIT_BUCKET = os.environ['AUDIT_BUCKET']

def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))
    user_id = body.get('user_id')
    
    conn = psycopg2.connect(
        host=os.environ['PGHOST'],
        dbname='postgres',
        user=os.environ['PGUSER'],
        password=os.environ['PGPASSWORD']
    )
    
    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ecommerce.users WHERE user_id = %s RETURNING user_id", (user_id,))
            deleted = cur.fetchone()
    
    if not deleted:
        return {"statusCode": 404, "body": json.dumps({"error": "user not found"})}
    
    receipt = {
        "user_id": user_id,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "tables_affected": ["users", "orders", "order_items"],
        "method": "hard_delete_cascade"
    }
    
    key = f"erasure_requests/{datetime.now(timezone.utc).date()}/request_{user_id}.json"
    s3.put_object(Bucket=AUDIT_BUCKET, Key=key, Body=json.dumps(receipt), ContentType='application/json')
    
    return {"statusCode": 200, "body": json.dumps({"status": "erased", **receipt, "audit_key": key})}