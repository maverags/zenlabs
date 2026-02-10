#!/bin/bash

# Quick Deployment Script for Spa/Salon Agentic System
# Run this after you've set up Supabase and Fly.io accounts

set -e

echo "🚀 Spa/Salon Agentic System - Quick Deploy"
echo "=========================================="
echo ""

# Check if fly CLI is installed
if ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI not found. Please install it first:"
    echo "   https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

echo "✅ Fly CLI found"
echo ""

# Check if logged in to Fly
if ! fly auth whoami &> /dev/null; then
    echo "🔐 Please login to Fly.io..."
    fly auth login
fi

echo "✅ Logged in to Fly.io"
echo ""

# Create app if it doesn't exist
APP_NAME="spa-agentic-system"

if fly apps list | grep -q "$APP_NAME"; then
    echo "✅ App '$APP_NAME' already exists"
else
    echo "📦 Creating new Fly.io app..."
    fly launch --name $APP_NAME --no-deploy
fi

echo ""
echo "🔑 Now set your environment variables:"
echo ""
echo "You'll need:"
echo "  1. Supabase database host (from Supabase dashboard)"
echo "  2. Supabase database password"
echo "  3. Anthropic API key"
echo ""

read -p "Supabase Host (db.xxxxx.supabase.co): " DB_HOST
read -sp "Supabase Password: " DB_PASSWORD
echo ""
read -sp "Anthropic API Key (sk-ant-...): " ANTHROPIC_KEY
echo ""
echo ""

echo "📝 Setting secrets..."
fly secrets set \
    DB_HOST="$DB_HOST" \
    DB_PORT=5432 \
    DB_NAME=postgres \
    DB_USER=postgres \
    DB_PASSWORD="$DB_PASSWORD" \
    ANTHROPIC_API_KEY="$ANTHROPIC_KEY"

echo ""
echo "🚀 Deploying application..."
fly deploy

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Your app is live at:"
fly status | grep "Hostname" | awk '{print "https://" $2}'
echo ""
echo "View dashboard:"
fly status | grep "Hostname" | awk '{print "https://" $2 "/dashboard"}'
echo ""
echo "Check logs:"
echo "  fly logs"
echo ""
echo "🎉 Happy demo'ing!"
