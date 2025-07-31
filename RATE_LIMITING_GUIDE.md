# Bedrock Rate Limiting Troubleshooting Guide

## 🚨 **"Request Rate Too High" Error Solutions**

### **Immediate Actions:**
1. **Stop testing for 5-10 minutes** to let rate limits reset
2. **Check CloudWatch logs** for any retry loops or excessive calls
3. **Ensure you're not testing multiple agents simultaneously**

## 🔧 **Rate Limiting Solutions Applied:**

### **1. Intent Mapper Improvements:**
- ✅ **Exponential backoff retry** - Automatically retries with increasing delays
- ✅ **Adaptive retry configuration** - boto3 client optimizes retries
- ✅ **Rate limit detection** - Catches ThrottlingException and TooManyRequestsException
- ✅ **Graceful degradation** - Returns 429 status with helpful error message

### **2. Testing Best Practices:**

#### **Reduce Test Frequency:**
```bash
# ❌ Don't test rapidly like this:
curl -X POST .../intent-mapper -d '{"text":"test1","sessionId":"1"}'
curl -X POST .../intent-mapper -d '{"text":"test2","sessionId":"2"}'
curl -X POST .../intent-mapper -d '{"text":"test3","sessionId":"3"}'

# ✅ Instead, space out tests:
curl -X POST .../intent-mapper -d '{"text":"test1","sessionId":"1"}'
# Wait 30-60 seconds
curl -X POST .../intent-mapper -d '{"text":"test2","sessionId":"2"}'
```

#### **Use Consistent Session IDs:**
```bash
# ✅ Reuse session IDs to reduce overhead
curl -X POST .../intent-mapper -d '{"text":"Add procedure","sessionId":"dev-session"}'
curl -X POST .../intent-mapper -d '{"text":"Get quote","sessionId":"dev-session"}'
curl -X POST .../intent-mapper -d '{"text":"Show history","sessionId":"dev-session"}'
```

### **3. Direct Lambda Testing (Bypass Bedrock Agent):**

Test Lambda functions directly to avoid Bedrock rate limits:

```bash
# Test AddDoctorProcedure directly
curl -X POST https://jj6skt98b3.execute-api.us-east-1.amazonaws.com/dev/add-doctor-procedure \
  -H "Content-Type: application/json" \
  -d '{"doctorName":"Dr. Smith","procedureCode":"TEST001","procedureName":"Test Procedure","cost":100}'

# Test GetQuote directly  
curl "https://jj6skt98b3.execute-api.us-east-1.amazonaws.com/dev/get-quote?procedureCode=TEST001"

# Test ShowHistory directly
curl "https://jj6skt98b3.execute-api.us-east-1.amazonaws.com/dev/show-history?doctorName=Dr.%20Smith"
```

## 📊 **Understanding Bedrock Limits:**

### **Default Rate Limits:**
- **invoke_agent**: 25 requests per minute per account per region
- **Foundation model calls**: Varies by model (Claude 3 Haiku: ~1000 TPM)
- **Session limits**: 10 concurrent sessions per agent

### **Rate Limit Hierarchy:**
1. **AWS Account Level** - Overall Bedrock API calls
2. **Agent Level** - Calls to specific agent
3. **Session Level** - Concurrent sessions per agent
4. **Model Level** - Foundation model invocations

## 🛠 **Advanced Solutions:**

### **1. Request Quotas Increase:**
If you need higher limits for production:
1. Go to **AWS Service Quotas** console
2. Search for **Amazon Bedrock**
3. Request quota increases for:
   - "Invoke Agent requests per minute"
   - "Agent sessions per agent"

### **2. Implement Client-Side Rate Limiting:**
```javascript
// Example for frontend applications
class BedrockRateLimiter {
    constructor() {
        this.lastRequest = 0;
        this.minInterval = 2000; // 2 seconds between requests
    }
    
    async makeRequest(payload) {
        const now = Date.now();
        const timeToWait = this.minInterval - (now - this.lastRequest);
        
        if (timeToWait > 0) {
            await new Promise(resolve => setTimeout(resolve, timeToWait));
        }
        
        this.lastRequest = Date.now();
        return fetch('/intent-mapper', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }
}
```

### **3. Use Different Regions (If Available):**
Some regions may have different rate limits:
- us-east-1 (default)
- us-west-2
- eu-west-1

## 🔍 **Monitoring and Debugging:**

### **CloudWatch Metrics to Monitor:**
- `AWS/Bedrock/InvocationLatency`
- `AWS/Bedrock/InvocationErrors` 
- `AWS/Lambda/Throttles`

### **Log Analysis:**
Check CloudWatch logs for patterns:
```
# Look for these in Lambda logs:
"Rate limit hit, retrying in X seconds"
"ThrottlingException"
"TooManyRequestsException"
```

## ✅ **Current Status:**
- ✅ **Intent mapper has retry logic** - Automatically handles rate limits
- ✅ **All Lambda functions work independently** - Can test without Bedrock
- ✅ **Exponential backoff implemented** - Reduces consecutive failures
- ✅ **Error handling improved** - Clear error messages for rate limits

## 🎯 **Recommended Testing Approach:**

1. **Test Lambda functions directly first** (no rate limits)
2. **Test Bedrock Agent with 30-60 second intervals**
3. **Use same session ID for related tests**
4. **If rate limited, wait 5-10 minutes before retrying**
5. **Monitor CloudWatch logs for patterns**

The rate limiting improvements are now deployed and should help manage the "request rate too high" errors automatically!
