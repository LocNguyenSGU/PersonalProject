# Troubleshooting Guide

Common issues and their solutions for the AI personalization system.

## Backend API Issues

### API Returns 500 Errors

**Symptom**: `curl http://localhost:8000/api/test` returns HTTP 500

**Solutions**:

1. **Check backend logs:**
   ```bash
   docker logs portfolio_backend
   
   # Look for error messages, stack traces
   ```

2. **Verify database connection:**
   ```bash
   docker logs portfolio_db
   
   # Check for "connection refused" or "authentication failed"
   docker exec portfolio_db pg_isready -U portfolio
   ```

3. **Check environment variables:**
   ```bash
   docker exec portfolio_backend env | grep SUPABASE
   docker exec portfolio_backend env | grep GEMINI
   ```

4. **Test database directly:**
   ```bash
   docker exec portfolio_db psql -U portfolio -d portfolio_ai -c "SELECT 1"
   ```

5. **Restart backend:**
   ```bash
   docker restart portfolio_backend
   ```

### API Returns 422 (Validation Error)

**Symptom**: POST request with invalid JSON/format

**Solution**: Check request format matches Pydantic schema:
- event_name must be alphanumeric + underscore only
- event_params must be valid JSON object
- event_timestamp must be integer
- user_pseudo_id max 200 characters

### API Returns 429 (Rate Limited)

**Symptom**: Too many requests too fast

**Solutions**:
1. **Wait**: Rate limits reset per minute
2. **Check limits**: /api/events is 100/min, /api/admin/login is 5/min
3. **Adjust in code**: `backend/app/main.py` contains rate limit decorators

### Slow API Responses (>1 second)

**Solutions**:

1. **Check cache hit rate:**
   ```bash
   curl http://localhost:8000/metrics | grep cache_hits
   
   # Look for cache_hits_total metric
   # Target: >80% hit rate
   ```

2. **Check database performance:**
   ```bash
   # Connect to database
   docker exec -it portfolio_db psql -U portfolio -d portfolio_ai
   
   # Check slow queries
   SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
   
   # Add index if missing
   CREATE INDEX idx_analytics_raw_user_id ON analytics_raw(user_pseudo_id);
   ```

3. **Check LLM API response time:**
   ```bash
   # View metrics
   curl http://localhost:8000/metrics | grep llm_request_duration
   
   # If Gemini slow, check Deepseek fallback
   docker logs portfolio_backend | grep "DeepSeek fallback"
   ```

4. **Monitor resource usage:**
   ```bash
   # CPU and memory
   docker stats portfolio_backend
   
   # Check connections
   docker exec portfolio_db psql -U portfolio -c "SELECT count(*) FROM pg_stat_activity"
   ```

## Database Issues

### Database Connection Failed

**Symptom**: "could not connect to server: Connection refused"

**Solutions**:

1. **Verify PostgreSQL is running:**
   ```bash
   docker-compose ps
   
   # Should show portfolio_db as "Up"
   ```

2. **Check PostgreSQL logs:**
   ```bash
   docker logs portfolio_db
   
   # Look for "ready to accept connections"
   ```

3. **Test connection:**
   ```bash
   # From host
   docker exec portfolio_db pg_isready -U portfolio -h localhost -p 5432
   
   # Should output: "accepting connections"
   ```

4. **Restart database:**
   ```bash
   docker restart portfolio_db
   
   # May take 10-15 seconds to be ready
   ```

5. **Check network:**
   ```bash
   # Verify backend can reach database
   docker exec portfolio_backend ping db
   
   # Should respond (or show "Temporary failure in name resolution")
   ```

### Out of Memory

**Symptom**: Docker container killed/OOMKilled

**Solutions**:

1. **Check memory usage:**
   ```bash
   docker stats portfolio_db
   
   # Look for "% MemUsage"
   ```

2. **Increase container memory:**
   ```yaml
   # In docker-compose.yml
   services:
     db:
       mem_limit: 2g  # Increase from 1g
   ```

3. **Optimize database:**
   ```bash
   # Connect and check cache
   docker exec -it portfolio_db psql -U portfolio -d portfolio_ai
   
   # Check cache hit ratio
   SELECT sum(blks_hit)/(sum(blks_hit) + sum(blks_read)) as cache_ratio
   FROM pg_statio_user_tables;
   
   # Should be >90% for good performance
   ```

### Disk Space Full

**Symptom**: "ERROR: could not open file... No space left on device"

**Solutions**:

1. **Check disk usage:**
   ```bash
   # Container volumes
   docker volume ls
   docker volume inspect portfolio_db_postgres_data
   
   # Host filesystem
   df -h
   ```

2. **Clean old data:**
   ```bash
   # Archive analytics older than 30 days
   docker exec -it portfolio_db psql -U portfolio -d portfolio_ai << 'SQL'
   DELETE FROM analytics_raw 
   WHERE created_at < NOW() - INTERVAL '30 days';
   VACUUM ANALYZE;
   SQL
   ```

3. **Prune Docker volumes:**
   ```bash
   docker volume prune  # Removes unused volumes
   ```

## Redis Issues

### Redis Connection Failed

**Symptom**: Cache operations fail, "Connection refused"

**Solutions**:

1. **Verify Redis is running:**
   ```bash
   docker logs portfolio_redis
   
   # Should show "Ready to accept connections"
   ```

2. **Test connection:**
   ```bash
   docker exec portfolio_redis redis-cli ping
   
   # Should output: "PONG"
   ```

3. **Check memory:**
   ```bash
   docker exec portfolio_redis redis-cli INFO memory
   
   # Check used_memory vs maxmemory
   ```

4. **Clear cache if full:**
   ```bash
   docker exec portfolio_redis redis-cli FLUSHALL
   
   # Clears all cached data (safe, will re-cache on next request)
   ```

### Cache Not Working

**Symptom**: Every request has high latency (no cache hit)

**Solutions**:

1. **Check cache hit rate:**
   ```bash
   curl http://localhost:8000/metrics | grep -A2 cache_hits
   ```

2. **Verify cache is connected:**
   ```bash
   docker logs portfolio_backend | grep "cache"
   
   # Should show "Redis connected successfully"
   ```

3. **Check for cache errors:**
   ```bash
   docker logs portfolio_backend | grep "Cache"
   
   # Look for "Cache get error" or "Cache set error"
   ```

4. **Restart Redis:**
   ```bash
   docker restart portfolio_redis
   
   # Note: This clears all cached data
   ```

## LLM API Issues

### Gemini API Returns Error

**Symptom**: "Error calling Gemini API", "Invalid API key"

**Solutions**:

1. **Verify API key:**
   ```bash
   echo $GEMINI_API_KEY  # (only if set in environment)
   
   # Check in backend config
   docker exec portfolio_backend python -c "from app.config import settings; print(settings.GEMINI_API_KEY[:10])"
   ```

2. **Check API quota:**
   - Visit: https://console.cloud.google.com/apis/dashboard
   - Look for Generative Language API
   - Check usage and quotas

3. **Test API key directly:**
   ```bash
   curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"contents":[{"parts":[{"text":"test"}]}]}'
   ```

4. **Enable fallback to DeepSeek:**
   - Set DEEPSEEK_API_KEY in environment
   - Backend will automatically fallback if Gemini fails

### All LLM Providers Down

**Symptom**: "All LLM providers failed", segmentation not working

**Solutions**:

1. **Check API status:**
   - Gemini: https://status.cloud.google.com
   - DeepSeek: https://status.deepseek.com (if available)

2. **Use heuristic fallback:**
   ```python
   # In app/services/llm_service.py
   # Heuristic segmentation based on events (no LLM needed)
   ```

3. **Temporarily disable segmentation:**
   ```bash
   # Set LLM_DISABLED=true in .env
   # Frontend will show default portfolio (not personalized)
   ```

## Monitoring & Metrics Issues

### Prometheus Not Scraping Metrics

**Symptom**: No metrics in Prometheus dashboard, "Targets Down"

**Solutions**:

1. **Check Prometheus targets:**
   ```bash
   curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'
   ```

2. **Verify metrics endpoint:**
   ```bash
   curl http://localhost:8000/metrics | head -20
   
   # Should show Prometheus format metrics
   ```

3. **Check scrape config:**
   ```bash
   # In monitoring/prometheus.yml
   # Verify job_name and targets match
   
   # Restart Prometheus
   docker-compose -f docker-compose.monitoring.yml restart prometheus
   ```

4. **Check network connectivity:**
   ```bash
   docker exec prometheus ping backend
   
   # Or
   docker exec prometheus curl http://backend:8000/metrics
   ```

### Grafana Can't Connect to Prometheus

**Symptom**: "Prometheus server does not have a working datasource"

**Solutions**:

1. **Test connection:**
   ```bash
   docker exec grafana curl http://prometheus:9090
   
   # Should return Prometheus homepage HTML
   ```

2. **Check Grafana datasource config:**
   - Grafana UI → Configuration → Data Sources
   - Edit Prometheus datasource
   - Click "Test Connection" button
   - URL should be: http://prometheus:9090

3. **Verify network:**
   ```bash
   docker network ls
   docker network inspect portfolio_network
   ```

## Security Issues

### 401 Unauthorized on Admin Endpoints

**Symptom**: `curl http://localhost:8000/api/admin/dashboard` returns 401

**Solutions**:

1. **Get JWT token:**
   ```bash
   curl -X POST http://localhost:8000/api/admin/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin"}'
   
   # Response: {"access_token":"eyJ...","token_type":"bearer"}
   ```

2. **Use token in request:**
   ```bash
   TOKEN="eyJ..."
   curl http://localhost:8000/api/admin/dashboard \
     -H "Authorization: Bearer $TOKEN"
   ```

3. **Check token expiration:**
   - Tokens expire after 8 hours
   - Get new token when expired

4. **Verify admin credentials:**
   ```bash
   docker exec portfolio_backend python -c "from app.config import settings; print(settings.ADMIN_USERNAME)"
   ```

### CORS Error on Frontend

**Symptom**: "Access to XMLHttpRequest has been blocked by CORS policy"

**Solutions**:

1. **Add origin to ALLOWED_ORIGINS:**
   ```bash
   # In backend/.env
   ALLOWED_ORIGINS=http://localhost:3000,https://yourportfolio.com
   ```

2. **Verify CORS middleware:**
   ```python
   # In backend/app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=settings.ALLOWED_ORIGINS.split(","),
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Test CORS:**
   ```bash
   curl -i -X OPTIONS http://localhost:8000/api/test \
     -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET"
   
   # Should include "Access-Control-Allow-Origin" in response
   ```

## Docker Issues

### Container Won't Start

**Symptom**: `docker-compose up` fails

**Solutions**:

1. **Check logs:**
   ```bash
   docker-compose logs backend
   docker-compose logs db
   ```

2. **Validate docker-compose.yml:**
   ```bash
   docker-compose config
   
   # Will show syntax errors
   ```

3. **Rebuild image:**
   ```bash
   docker-compose build --no-cache
   docker-compose up
   ```

4. **Check disk space:**
   ```bash
   df -h
   docker system df
   ```

### Docker Compose Port Already in Use

**Symptom**: "Address already in use"

**Solutions**:

1. **Find process using port:**
   ```bash
   lsof -i :8000
   lsof -i :5432
   lsof -i :6379
   ```

2. **Stop other services:**
   ```bash
   sudo systemctl stop other_service
   # or
   kill -9 <PID>
   ```

3. **Change ports in docker-compose.yml:**
   ```yaml
   services:
     backend:
       ports:
         - "8001:8000"  # Changed from 8000
   ```

## Health Check

Run this script to diagnose system health:

```bash
#!/bin/bash
echo "=== Docker Services ==="
docker-compose ps

echo -e "\n=== Database Health ==="
docker exec portfolio_db pg_isready -U portfolio && echo "✓ PostgreSQL OK" || echo "✗ PostgreSQL Failed"

echo -e "\n=== Redis Health ==="
docker exec portfolio_redis redis-cli ping && echo "✓ Redis OK" || echo "✗ Redis Failed"

echo -e "\n=== Backend Health ==="
curl -s http://localhost:8000/health | jq . && echo "✓ Backend OK" || echo "✗ Backend Failed"

echo -e "\n=== Metrics ==="
curl -s http://localhost:8000/metrics | head -5 && echo "✓ Metrics OK" || echo "✗ Metrics Failed"

echo -e "\n=== Prometheus ==="
curl -s http://localhost:9090 > /dev/null && echo "✓ Prometheus OK" || echo "✗ Prometheus Failed"

echo -e "\n=== Grafana ==="
curl -s http://localhost:3000 > /dev/null && echo "✓ Grafana OK" || echo "✗ Grafana Failed"
```

## Getting Help

If you can't resolve the issue:

1. Check the logs (see commands above)
2. Review this troubleshooting guide
3. Check GitHub issues: https://github.com/yourrepo/issues
4. Contact support: support@example.com

Include the following when requesting help:
- Error message/logs
- Command you ran
- System info (OS, Docker version, etc.)
- Steps to reproduce

---

**Last Updated:** January 2026
