# GitHub Upload Guide

Step-by-step guide to upload the delivery_bot_ws project to GitHub.

## Prerequisites

- Git installed on your system
- GitHub account (https://github.com/abhishekbera86)
- Repository already created on GitHub: https://github.com/abhishekbera86/delivery_bot_pkg

## Step-by-Step Instructions

### Step 1: Check Git is Installed

```bash
git --version
```

If not installed:
```bash
sudo apt update
sudo apt install git
```

### Step 2: Navigate to Project Directory

```bash
cd ~/delivery_bot_ws
```

### Step 3: Initialize Git Repository

```bash
git init
```

### Step 4: Configure Git (if not already configured)

```bash
# Set your name (if not already set)
git config --global user.name "abhishekbera86"

# Set your email (if not already set)
git config --global user.email "your-email@example.com"
```

### Step 5: Add All Files

```bash
# Add all files to staging
git add .

# Check what will be committed
git status
```

### Step 6: Create Initial Commit

```bash
git commit -m "Initial commit: Delivery Bot project for TurtleBot 4"
```

### Step 7: Add GitHub Remote

```bash
git remote add origin https://github.com/abhishekbera86/delivery_bot_pkg.git
```

### Step 8: Verify Remote

```bash
git remote -v
```

Should show:
```
origin  https://github.com/abhishekbera86/delivery_bot_pkg.git (fetch)
origin  https://github.com/abhishekbera86/delivery_bot_pkg.git (push)
```

### Step 9: Push to GitHub

```bash
# Set default branch name to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Note:** You may be prompted for GitHub credentials:
- **Username:** abhishekbera86
- **Password:** Use a Personal Access Token (not your GitHub password)
  - Generate token: https://github.com/settings/tokens
  - Select "repo" scope
  - Copy and paste token when prompted

### Step 10: Verify Upload

Check your repository on GitHub:
https://github.com/abhishekbera86/delivery_bot_pkg

You should see all your files!

## Troubleshooting

### Authentication Failed

If you get authentication errors, use a Personal Access Token:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select "repo" scope
4. Copy the token
5. Use token as password when prompted

### Push Rejected

If push is rejected because repository has content:
```bash
# Pull first, then push
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Wrong Remote URL

If you need to change the remote URL:
```bash
git remote set-url origin https://github.com/abhishekbera86/delivery_bot_pkg.git
```

## Future Updates

To push future changes:

```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push
git push
```

## Summary Commands

```bash
cd ~/delivery_bot_ws
git init
git add .
git commit -m "Initial commit: Delivery Bot project for TurtleBot 4"
git remote add origin https://github.com/abhishekbera86/delivery_bot_pkg.git
git branch -M main
git push -u origin main
```

