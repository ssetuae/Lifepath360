# Learning Compass Deployment Guide

This document provides instructions for deploying the Learning Compass application to Render.

## Prerequisites

1. A Render account (https://render.com)
2. A GitHub repository with the Learning Compass code
3. OpenAI API key for AI-driven question generation
4. Stripe API keys for payment processing

## Deployment Steps

### 1. Fork or Clone the Repository

First, fork or clone the Learning Compass repository to your GitHub account.

### 2. Connect to Render

1. Log in to your Render account
2. Go to the Dashboard and click "New +"
3. Select "Blueprint"
4. Connect your GitHub account if you haven't already
5. Select the Learning Compass repository
6. Click "Connect"

### 3. Configure Environment Variables

Render will automatically detect the `render.yaml` file and create the services defined in it. You'll need to set the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `STRIPE_SECRET_KEY`: Your Stripe secret key
- `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
- `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret

### 4. Deploy the Application

1. Click "Apply" to create the services
2. Render will automatically build and deploy the application
3. Once deployment is complete, you can access the application at the provided URLs

### 5. Database Setup

The database will be automatically created by Render. To initialize it:

1. Go to the "learning-compass-api" service in Render
2. Click on the "Shell" tab
3. Run the following commands:
   
4. Follow the prompts to create an admin user

### 6. Verify Deployment

1. Access the frontend application at the URL provided by Render
2. Log in with the admin credentials you created
3. Verify that all features are working correctly

## Troubleshooting

If you encounter any issues during deployment:

1. Check the logs in the Render dashboard
2. Ensure all environment variables are set correctly
3. Verify that the database migrations have been applied
4. Check that the frontend is correctly configured to connect to the backend API

For more information, refer to the Render documentation: https://render.com/docs
