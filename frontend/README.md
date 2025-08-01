# Doctor Procedures Frontend

A modern React frontend for the Doctor Procedures Bedrock App, featuring both AI chat interface and quick action forms.

## Features

- 🤖 **AI Chat Interface** - Natural language interaction with Amazon Bedrock Agent
- ⚡ **Quick Actions** - Forms for adding procedures, getting quotes, and viewing history
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎨 **Modern UI** - Built with Tailwind CSS and Lucide React icons
- 🔄 **Real-time Updates** - Live data from AWS API Gateway and DynamoDB

## Prerequisites

- Node.js 16+ and npm
- The backend API must be deployed and running

## Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Update API configuration (if needed):**
   Edit `src/api.js` to change the API endpoint:
   ```javascript
   const API_BASE_URL = 'https://your-api-gateway-url.amazonaws.com/dev';
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

4. **Open in browser:**
   Navigate to `http://localhost:3000`

## Build for Production

```bash
npm run build
```

The built files will be in the `build/` directory, ready for deployment to S3, CloudFront, or any static hosting service.

## Architecture

### Components

- **App.js** - Main application with routing and layout
- **ChatInterface.js** - AI chat component for Bedrock Agent
- **QuickActions.js** - Form-based interface for direct API calls

### API Integration

- **api.js** - Centralized API client with error handling
- Supports both Bedrock Agent (chat) and direct Lambda calls (forms)
- Automatic rate limiting consideration for Bedrock calls

### Styling

- **Tailwind CSS** - Utility-first CSS framework
- **Custom animations** - Fade-in effects and chat message animations
- **Responsive design** - Mobile-first approach

## Usage

### Chat Interface

- Natural language queries to the AI assistant
- Supports all three intents: Show History, Get Quote, Add Procedure
- Real-time responses with typing indicators
- Session management for conversation context

### Quick Actions

- **Add Procedure** - Structured form for adding new procedures
- **Get Quote** - Quick lookup for procedure costs
- **View History** - Filtered view of doctor procedure history

## API Endpoints

The frontend connects to these backend endpoints:

- `POST /intent-mapper` - Bedrock Agent chat interface
- `POST /add-doctor-procedure` - Direct procedure addition
- `GET /get-quote?procedureCode=X` - Cost quotes
- `GET /show-history?doctorName=X` - Procedure history

## Configuration

### Environment Variables

Create a `.env` file for local development:

```
REACT_APP_API_BASE_URL=https://jj6skt98b3.execute-api.us-east-1.amazonaws.com/dev
REACT_APP_BEDROCK_AGENT_ID=EBGEJR3FWL
```

### Rate Limiting

The chat interface automatically handles Bedrock rate limits by:
- Adding delays between requests
- Showing loading states
- Providing helpful error messages

## Deployment Options

### AWS S3 + CloudFront

1. Build the project: `npm run build`
2. Upload `build/` contents to S3 bucket
3. Configure CloudFront distribution
4. Set up custom domain (optional)

### Netlify/Vercel

1. Connect your Git repository
2. Set build command: `npm run build`
3. Set publish directory: `build`
4. Deploy automatically on push

## Troubleshooting

### CORS Issues

If you encounter CORS errors, ensure your API Gateway has proper CORS configuration:

```javascript
headers: {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
}
```

### Rate Limiting

If chat responses are slow or failing:
- Wait 30-60 seconds between requests
- Use Quick Actions for immediate responses
- Check CloudWatch logs for Bedrock Agent issues

### API Connection

Verify the API endpoint in `src/api.js` matches your deployed backend URL.

## License

This project is part of the Doctor Procedures Bedrock App.
