#!/bin/bash

# Hugging Face Spaces Deployment Script for Market Intelligence API

echo "🚀 Deploying Market Intelligence API to Hugging Face Spaces"
echo ""

# Check if user has git configured
if ! git config user.name > /dev/null 2>&1; then
    echo "⚠️  Git user not configured. Please set it up:"
    echo "git config --global user.name 'Your Name'"
    echo "git config --global user.email 'your.email@example.com'"
    exit 1
fi

# Get Hugging Face username
read -p "Enter your Hugging Face username: " HF_USERNAME

# Create Space name
SPACE_NAME="market-intel-api"
SPACE_URL="https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"

echo ""
echo "📝 Before running this script, make sure you've:"
echo "1. Created an account at https://huggingface.co/join"
echo "2. Created a new Space at https://huggingface.co/new-space with:"
echo "   - Name: $SPACE_NAME"
echo "   - SDK: Docker"
echo "   - License: Apache 2.0"
echo ""
read -p "Have you created the Space? (y/n): " CREATED

if [ "$CREATED" != "y" ]; then
    echo ""
    echo "Please create the Space first, then run this script again."
    echo "Go to: https://huggingface.co/new-space"
    exit 0
fi

echo ""
echo "🔑 Setting up environment variables..."
echo "You'll need to add these secrets in the Space settings:"
echo "1. Go to: $SPACE_URL/settings"
echo "2. Navigate to 'Repository secrets'"
echo "3. Add the following secrets:"
echo "   - GEMINI_API_KEY (your Gemini API key)"
echo "   - FINANCIAL_DATASETS_API_KEY (optional)"
echo ""
read -p "Press Enter to continue after adding secrets..."

# Create temporary directory for deployment
TEMP_DIR="/tmp/hf-space-deploy-$$"
mkdir -p "$TEMP_DIR"

echo ""
echo "📦 Preparing files for deployment..."

# Clone the Space repository
git clone "https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME" "$TEMP_DIR"

if [ $? -ne 0 ]; then
    echo "❌ Failed to clone Space repository. Please check:"
    echo "   - Your Hugging Face username is correct"
    echo "   - The Space name is: $SPACE_NAME"
    echo "   - You have access to the Space"
    exit 1
fi

cd "$TEMP_DIR"

# Copy project files
echo "📋 Copying project files..."
cp -r /home/arun/Desktop/Hack/Market_intelligence_MCP/* .

# Rename the HF readme
if [ -f ".huggingface_readme.md" ]; then
    mv .huggingface_readme.md README.md
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
*.db
.env
.venv/
venv/
*.log
.DS_Store
EOF
fi

# Commit and push
echo ""
echo "📤 Pushing to Hugging Face Spaces..."
git add .
git commit -m "Deploy Market Intelligence API"
git push

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "🎉 Your API is being deployed to:"
    echo "   $SPACE_URL"
    echo ""
    echo "⏳ Building will take 2-5 minutes. Check the 'Logs' tab for progress."
    echo ""
    echo "🧪 Once deployed, test with:"
    echo "   curl https://$HF_USERNAME-$SPACE_NAME.hf.space/health"
    echo ""
else
    echo ""
    echo "❌ Push failed. You may need to authenticate:"
    echo "   - Go to https://huggingface.co/settings/tokens"
    echo "   - Create a new token with 'write' permission"
    echo "   - Use it when prompted for password"
fi

# Cleanup
cd /home/arun/Desktop/Hack/Market_intelligence_MCP
rm -rf "$TEMP_DIR"
