# IAM Permissions Setup Guide for BharatSignal

## 🚨 Current Issue

Your IAM user `Developer-User` (ARN: `arn:aws:iam::217441067719:user/Developer-User`) lacks the necessary permissions to create AWS resources.

### Errors Encountered:
- **S3**: AccessDenied - Cannot create buckets
- **DynamoDB**: AccessDeniedException - Cannot create tables
- **Bedrock**: AccessDeniedException - Cannot invoke models

## ✅ Solution: Grant Required IAM Permissions

You have **two options** to fix this:

### Option 1: Use AWS Console (Recommended - Easiest)

1. **Log in to AWS Console** as an administrator
   - Go to: https://console.aws.amazon.com/

2. **Navigate to IAM**
   - Search for "IAM" in the top search bar
   - Click on "IAM" service

3. **Find Your User**
   - Click "Users" in the left sidebar
   - Find and click on "Developer-User"

4. **Attach Policies**
   - Click the "Permissions" tab
   - Click "Add permissions" → "Attach policies directly"
   - Search and select these policies:
     - ✅ `AmazonS3FullAccess`
     - ✅ `AmazonDynamoDBFullAccess`
     - ✅ `AmazonBedrockFullAccess`
   - Click "Next" → "Add permissions"

5. **Verify Permissions**
   - You should see all three policies listed under "Permissions policies"

### Option 2: Use AWS CLI (For Advanced Users)

If you have AWS CLI configured with admin credentials:

```bash
# Attach S3 permissions
aws iam attach-user-policy \
  --user-name Developer-User \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Attach DynamoDB permissions
aws iam attach-user-policy \
  --user-name Developer-User \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

# Attach Bedrock permissions
aws iam attach-user-policy \
  --user-name Developer-User \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

### Option 3: Create Custom Policy (Most Secure - Least Privilege)

If you want to grant only the minimum required permissions:

1. **Go to IAM Console** → "Policies" → "Create policy"

2. **Use this JSON policy**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BucketManagement",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:PutBucketVersioning",
        "s3:PutLifecycleConfiguration",
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::bharatsignal-*",
        "arn:aws:s3:::bharatsignal-*/*"
      ]
    },
    {
      "Sid": "DynamoDBTableManagement",
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable",
        "dynamodb:UpdateTimeToLive",
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:217441067719:table/BharatSignal_*"
    },
    {
      "Sid": "BedrockModelAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    }
  ]
}
```

3. **Name the policy**: `BharatSignal-Developer-Policy`

4. **Attach to User**:
   - Go to "Users" → "Developer-User"
   - Click "Add permissions" → "Attach policies directly"
   - Search for "BharatSignal-Developer-Policy"
   - Select and attach it

## 🔐 Enable Bedrock Model Access

Even with IAM permissions, you need to enable Bedrock models in your region:

1. **Go to Bedrock Console**
   - https://console.aws.amazon.com/bedrock/

2. **Enable Model Access**
   - Click "Model access" in the left sidebar
   - Click "Manage model access" (orange button)
   - Find "Claude 3 Sonnet" by Anthropic
   - Check the box next to it
   - Click "Request model access" at the bottom
   - Wait 1-2 minutes for approval (usually instant)

3. **Verify Access**
   - The status should change to "Access granted" (green)

## 🧪 Test After Granting Permissions

Once you've granted the permissions, run these commands to test:

```bash
# Test 1: Verify credentials are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✓ Credentials loaded')"

# Test 2: Run AWS setup
python aws_setup.py

# Test 3: Test Bedrock connection
python -c "from bedrock_client import test_bedrock_connection; print(test_bedrock_connection())"

# Test 4: Run the application
python run.py
```

## 📋 Verification Checklist

After granting permissions, verify each service:

- [ ] **IAM Permissions Attached**
  - AmazonS3FullAccess (or custom S3 policy)
  - AmazonDynamoDBFullAccess (or custom DynamoDB policy)
  - AmazonBedrockFullAccess (or custom Bedrock policy)

- [ ] **Bedrock Model Access Enabled**
  - Claude 3 Sonnet status: "Access granted"

- [ ] **AWS Setup Successful**
  - S3 buckets created: `bharatsignal-csv-uploads`, `bharatsignal-static`
  - DynamoDB tables created: `BharatSignal_UserSessions`, `BharatSignal_AnalysisCache`, `BharatSignal_AnalysisHistory`
  - Bedrock connection test passed

- [ ] **Application Running**
  - Flask app starts without errors
  - Can upload CSV files
  - Can get AI recommendations

## 🆘 Still Having Issues?

### Issue: "Access Denied" after granting permissions
**Solution**: Wait 1-2 minutes for IAM changes to propagate, then try again.

### Issue: "Bedrock not available in region"
**Solution**: Bedrock is available in `us-east-1`. Verify your `.env` file has:
```
AWS_REGION=us-east-1
```

### Issue: "Model not found"
**Solution**: Make sure you enabled "Claude 3 Sonnet" specifically, not just "Claude 3".

### Issue: "Bucket name already exists"
**Solution**: S3 bucket names are globally unique. Edit `.env` and add a unique suffix:
```
S3_BUCKET_NAME=bharatsignal-csv-uploads-YOUR_UNIQUE_ID
S3_STATIC_BUCKET=bharatsignal-static-YOUR_UNIQUE_ID
```

## 📞 Next Steps

1. ✅ Grant IAM permissions (Option 1, 2, or 3 above)
2. ✅ Enable Bedrock model access
3. ✅ Run `python aws_setup.py`
4. ✅ Test with `python run.py`
5. ✅ Upload a CSV file and get recommendations!

## 🔒 Security Best Practices

- ✅ Never commit `.env` file to Git (already in `.gitignore`)
- ✅ Use IAM user credentials, not root account (you're already doing this!)
- ✅ Rotate access keys every 90 days
- ✅ Enable MFA on your AWS account
- ✅ Use least privilege principle (Option 3 above)

---

**Your AWS Account ID**: 217441067719  
**Your IAM User**: Developer-User  
**Your Region**: us-east-1  
**Your Access Key**: AKIATFID7MLDW5U4DQLV (already configured in `.env`)

Once you complete the steps above, run `python aws_setup.py` again and it should work! 🚀
