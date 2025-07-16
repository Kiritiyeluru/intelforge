# IntelForge Configuration Files

This directory contains production configuration files for IntelForge's Phase 4 implementation.

## Configuration Files

### 1. `proxy_pools.txt`
**Purpose**: Proxy rotation for stealth crawling
**Usage**: Add proxy URLs (one per line) when using `--proxy-rotate` flag
**Format**: `protocol://[username:password@]ip:port`

**Example**:
```
http://proxy1.example.com:8080
socks5://user:pass@proxy2.example.com:1080
```

**Note**: Ensure proxy providers comply with target websites' Terms of Service.

### 2. `robots_whitelist.txt`
**Purpose**: Pre-approved domains for crawling
**Usage**: Domains listed here have been verified for robots.txt compliance
**Format**: One domain per line (without protocol)

**Example**:
```
arxiv.org
github.com
stackoverflow.com
```

**Important**: Always verify current robots.txt before adding new domains.

### 3. `ban_tracking.json`
**Purpose**: Track and manage IP/domain bans and circuit breakers
**Usage**: Automatically updated by the system to track failed requests
**Structure**: JSON format with ban history, settings, and recovery tracking

**Key Settings**:
- `ban_threshold_429`: Number of 429 (rate limit) responses before ban
- `cooldown_period_seconds`: Time to wait before retrying banned domain
- `circuit_breaker_failure_threshold`: Failures before circuit opens

### 4. `freshness_config.yaml`
**Purpose**: Time-to-recheck (TTR) settings for content freshness tracking
**Usage**: Defines how often different content types should be refreshed
**Format**: YAML with content type and domain-specific rules

**Key Sections**:
- `content_types`: TTL settings for news, research, documentation, etc.
- `domains`: Domain-specific freshness rules
- `tracking`: Freshness tracking behavior settings

## CLI Integration

These configuration files integrate with the following CLI flags:

- `--proxy-rotate`: Uses `proxy_pools.txt`
- `--respect-robots`: References `robots_whitelist.txt`
- `--max-retries`: Works with `ban_tracking.json` circuit breakers
- All crawling commands use `freshness_config.yaml` for TTR

## Production Setup

1. **Proxy Configuration**: Add your proxy providers to `proxy_pools.txt`
2. **Domain Verification**: Verify robots.txt compliance before adding to whitelist
3. **Monitoring**: Monitor `ban_tracking.json` for frequent bans
4. **Freshness Tuning**: Adjust TTL values in `freshness_config.yaml` based on your needs

## Security Notes

- Never commit actual proxy credentials to version control
- Use environment variables for sensitive proxy authentication
- Regularly audit whitelisted domains for compliance
- Monitor ban tracking logs for potential issues

## File Permissions

Ensure appropriate file permissions for production:
```bash
chmod 600 config/proxy_pools.txt  # Restrict proxy credentials
chmod 644 config/robots_whitelist.txt
chmod 644 config/ban_tracking.json
chmod 644 config/freshness_config.yaml
```
