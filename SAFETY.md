# Safety and Compliance

## System Design Principles

ShortsFactory is designed from the ground up with safety, transparency, and user control as core principles.

## What This System IS

✅ **Business-Grade Local Automation**
- Runs entirely on your PC
- Processes videos through a quality-controlled pipeline
- Provides tools for content creation
- Respects platform terms of service
- Operates transparently with full logging

✅ **User-Controlled**
- Requires explicit permission to run
- Manual approval gate before any upload
- Clear configuration and controls
- Can be stopped at any time
- Clean uninstall (just delete the directory)

✅ **Observable and Auditable**
- Every action logged with timestamp
- Full dashboard visibility
- Complete activity trail
- No hidden operations
- Open source code

## What This System IS NOT

❌ **NOT Malware**
- Does not hide or obfuscate operations
- Does not persist without user consent
- Does not run in stealth mode
- Does not bypass security measures
- Does not modify system files

❌ **NOT a Terms of Service Violator**
- Respects rate limits
- Includes human review gates
- Uses official APIs (when configured)
- Randomizes timing naturally
- Designed for compliant use

❌ **NOT a Spam Tool**
- Requires manual content approval
- Built-in upload throttling
- Quality control checkpoints
- Intended for legitimate content creation
- Not designed for abuse

## Safety Features

### 1. Explicit Permission
- User must manually start all components
- Nothing runs automatically on system boot
- Clear start/stop controls
- No background persistence without consent

### 2. Review Gate
- **Human approval required for ALL uploads**
- Nothing publishes without explicit user action
- Video preview in dashboard
- Metadata review before approval
- Three-action system: Approve/Reject/Reprocess

### 3. Rate Limiting
- Configurable daily upload limits
- Minimum delay between uploads (default: 60 minutes)
- Maximum delay with randomization (default: 180 minutes)
- Prevents platform overload
- Mimics natural human behavior

### 4. Audit Trail
- Complete logging of all actions
- Timestamps on every operation
- Activity logs viewable in dashboard
- File-based logs for external audit
- No action goes unrecorded

### 5. Crash Safety
- Jobs resume from last known state
- No data loss on unexpected shutdown
- Database transactions ensure consistency
- Graceful shutdown on CTRL+C
- No orphaned processes

### 6. Upload Safety
- **Disabled by default**
- Requires explicit configuration
- Stub implementation initially (doesn't actually upload)
- Real uploads need API credentials setup
- Test mode available

### 7. Configuration Transparency
- All settings in plain YAML file
- No hidden configurations
- Clear documentation of all options
- No obfuscation
- Easy to review and modify

## Compliance with Platform Guidelines

### YouTube Terms of Service
This system is designed to **comply** with YouTube's terms:

✅ **Content Quality**
- Human review before upload
- Quality control checkpoints
- Original or properly licensed content

✅ **Upload Practices**
- Respects API rate limits
- No automated spam
- Natural posting patterns
- Proper metadata and categorization

✅ **API Usage**
- Uses official YouTube Data API
- Follows OAuth 2.0 authentication
- Respects quota limits
- No unauthorized access

### What Users Must Ensure

🔒 **Your Responsibilities:**
1. Only upload content you own or have rights to
2. Follow YouTube's Community Guidelines
3. Comply with copyright laws
4. Don't use for spam or abuse
5. Monitor your content regularly
6. Respond to any platform feedback

## Data Privacy

### What Data is Stored Locally
- Video files (originals and processed)
- Metadata (titles, descriptions, hashtags)
- Job history and status
- Activity logs
- Configuration settings
- OAuth tokens (if configured)

### What Data is NOT Sent Externally
- No telemetry or analytics sent to developers
- No data shared with third parties
- No tracking of your usage
- No cloud backups without your setup

### What Data IS Sent to YouTube (when uploading)
- Video files (to YouTube's servers)
- Metadata (title, description, tags)
- API authentication tokens
- Standard API calls

All uploads use YouTube's official API with your credentials.

## Security Considerations

### Credentials
- YouTube API credentials stored in `config/credentials.json`
- OAuth tokens in `config/token.json`
- **Add both to .gitignore** (done automatically)
- Never commit credentials to version control
- Keep credentials file secured with file permissions

### Database
- SQLite database is local only
- No external connections
- File-based storage
- Can be encrypted at OS level if needed

### Network
- Only connects to YouTube API when uploading
- No other external connections
- Dashboard runs on localhost only
- No exposed ports to internet

## Monitoring and Control

### Real-Time Monitoring
- Dashboard shows all active jobs
- Live status updates
- Error tracking and reporting
- Activity log streaming

### Manual Controls
- Pause/stop any component at any time
- Reject videos at review stage
- Modify configuration while running
- Clear failed jobs and retry

### Shutdown Procedures
1. **Normal Shutdown**: CTRL+C (graceful)
2. **Emergency Stop**: Kill processes by PID
3. **State Preserved**: Resume on next start
4. **No Data Loss**: Transactions committed

## Responsible Use Guidelines

### Do's ✅
- Use for your own legitimate content creation
- Review and approve all videos manually
- Monitor system logs regularly
- Respect platform guidelines
- Keep software updated
- Configure reasonable rate limits
- Test thoroughly before production use

### Don'ts ❌
- Don't use for spam or abuse
- Don't upload copyrighted content without permission
- Don't bypass the review gate
- Don't exceed platform rate limits
- Don't hide your use of automation
- Don't violate terms of service
- Don't use for malicious purposes

## Liability

### User Responsibility
- You are responsible for content you upload
- You must comply with platform terms of service
- You must respect copyright and intellectual property
- You are responsible for monitoring your account

### Software Provided As-Is
- No warranty of any kind
- Use at your own risk
- Authors not liable for misuse
- Check LICENSE file for details

## Reporting Issues

### If You Find a Security Issue
1. Do not create a public issue
2. Email maintainers directly (if available)
3. Provide detailed information
4. Allow time for fix before disclosure

### If You Find a Bug
1. Check existing issues first
2. Create detailed bug report
3. Include logs and steps to reproduce
4. Help improve the system

## Transparency Commitment

This project commits to:
- ✅ Open source code
- ✅ Clear documentation
- ✅ No hidden features
- ✅ Honest about capabilities
- ✅ Responsive to security concerns
- ✅ Updates for safety improvements

## Future Safety Enhancements

Planned improvements:
- Content filtering hooks
- Duplicate detection
- Advanced rate limiting
- Multi-level approval workflows
- Integration with compliance tools
- Audit log export formats

## Questions?

If you have safety, compliance, or ethical concerns:
1. Review this document thoroughly
2. Check ARCHITECTURE.md for technical details
3. Examine the source code (it's open!)
4. Ask questions via GitHub issues
5. Suggest improvements

---

**Bottom Line**: This system is designed to help you create and manage content responsibly. It provides automation while maintaining human oversight and control. Use it ethically, follow platform guidelines, and respect others' rights.

**Remember**: With great automation comes great responsibility. Always review what you're uploading and ensure it complies with all applicable rules and laws.
