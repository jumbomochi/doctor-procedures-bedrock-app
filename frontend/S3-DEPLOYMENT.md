# S3 Deployment Guide for Doctor Procedures React App

## 🎯 Overview
This guide will help you deploy your React app to Amazon S3 for static website hosting. Your app will be accessible via a public URL and ready for testing.

## 📋 Prerequisites

### 1. AWS CLI Setup
```bash
# Install AWS CLI (if not already installed)
brew install awscli  # macOS
# or download from: https://aws.amazon.com/cli/

# Configure AWS credentials
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key  
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

### 2. Build Your App
```bash
# Make sure you're in the frontend directory
cd frontend

# Build for production
npm run build
```

## 🚀 Deployment Options

### Option 1: Automated Script (Recommended)
```bash
# Edit the bucket name in deploy-to-s3.sh if needed
# Then run:
./deploy-to-s3.sh
```

### Option 2: Manual Deployment
```bash
# 1. Create S3 bucket
aws s3 mb s3://your-bucket-name --region us-east-1

# 2. Enable static website hosting
aws s3 website s3://your-bucket-name --index-document index.html --error-document index.html

# 3. Upload files
aws s3 sync build/ s3://your-bucket-name --delete

# 4. Set public read permissions
aws s3api put-bucket-policy --bucket your-bucket-name --policy '{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}'
```

### Option 3: AWS Amplify (Advanced)
For a more robust solution with CI/CD:
```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize Amplify project
amplify init

# Add hosting
amplify add hosting

# Deploy
amplify publish
```

## 🌐 Accessing Your App

After deployment, your app will be available at:
- **S3 Website URL**: `http://your-bucket-name.s3-website-us-east-1.amazonaws.com`
- **Direct S3 URL**: `https://your-bucket-name.s3.amazonaws.com/index.html`

## 🔧 Configuration Notes

### Environment Variables
Your React app is built with these settings:
- API Base URL: `https://jj6skt98b3.execute-api.us-east-1.amazonaws.com/dev`
- Bedrock Agent ID: `EBGEJR3FWL`

### CORS Considerations
If you encounter CORS issues, ensure your API Gateway has the correct CORS headers:
```json
{
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
  "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}
```

## 🛠 Troubleshooting

### Common Issues:

1. **403 Forbidden Error**
   - Check bucket policy allows public read access
   - Verify bucket name in policy matches actual bucket

2. **404 on Refresh**
   - S3 static hosting uses `index.html` as error document for SPA routing
   - This is already configured in the deployment script

3. **API Calls Failing**
   - Check if your AWS Lambda functions are in the same region
   - Verify API Gateway endpoints are publicly accessible
   - Check browser developer tools for CORS errors

4. **Build Errors**
   - Ensure all dependencies are installed: `npm install`
   - Check for any linting errors in the code

## 🔄 Updates

To update your deployed app:
```bash
# 1. Make your changes
# 2. Rebuild
npm run build

# 3. Redeploy
./deploy-to-s3.sh
```

## 💡 Production Considerations

For production use, consider:
- **CloudFront**: Add CDN for better performance and HTTPS
- **Custom Domain**: Use Route 53 for custom domain names
- **Monitoring**: Set up CloudWatch for logging and metrics
- **Security**: Review bucket policies and access controls

## 📱 Testing Your Deployment

Once deployed, test these features:
1. ✅ Chat interface loads and connects to Bedrock Agent
2. ✅ Quick Actions forms work (Add Procedure, Get Quote, Show History)
3. ✅ Error handling displays correctly
4. ✅ Responsive design works on mobile devices
5. ✅ All API calls to your Lambda functions succeed

Your Doctor Procedures app should now be live and ready for testing!
