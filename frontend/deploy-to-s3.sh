#!/bin/bash

# S3 Deployment Script for Doctor Procedures React App
# This script deploys the React build to an S3 bucket for static website hosting

set -e

# Configuration
BUCKET_NAME="doctor-procedures-app"  # Change this to your desired bucket name
REGION="us-east-1"  # Change to your preferred AWS region
BUILD_DIR="build"

echo "🚀 Deploying Doctor Procedures React App to S3..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   brew install awscli"
    echo "   or visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if build directory exists
if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build directory not found. Please run 'npm run build' first."
    exit 1
fi

echo "📦 Build directory found: $BUILD_DIR"

# Create S3 bucket (will fail gracefully if bucket already exists)
echo "🪣 Creating S3 bucket: $BUCKET_NAME"
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "   (Bucket may already exist)"

# Enable static website hosting
echo "🌐 Configuring static website hosting..."
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html

# Set bucket policy for public read access
echo "🔓 Setting bucket policy for public access..."
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json
rm bucket-policy.json

# Sync build files to S3
echo "📤 Uploading files to S3..."
aws s3 sync $BUILD_DIR/ s3://$BUCKET_NAME --delete --cache-control "max-age=31536000" --exclude "*.html"
aws s3 sync $BUILD_DIR/ s3://$BUCKET_NAME --delete --cache-control "max-age=0" --include "*.html"

# Get the website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your app is now live at:"
echo "   $WEBSITE_URL"
echo ""
echo "📝 Next steps:"
echo "1. Test your app in the browser"
echo "2. Set up CloudFront for HTTPS and better performance (optional)"
echo "3. Configure a custom domain (optional)"
echo ""
echo "💡 Tip: If you need HTTPS, consider using CloudFront distribution"
echo "    or AWS Amplify for a more complete hosting solution."
