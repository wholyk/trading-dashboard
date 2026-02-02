"""
ShortsFactory Dashboard - Web UI for monitoring and reviewing jobs.
"""

import os
import streamlit as st
from datetime import datetime, timedelta

from shortsfactory.core.database import Database, JobState
from shortsfactory.core.config import get_config
from shortsfactory.core.logger import get_logger


# Page config
st.set_page_config(
    page_title="ShortsFactory Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize
@st.cache_resource
def init_dashboard():
    """Initialize dashboard resources"""
    config = get_config()
    db = Database(config.database_path)
    logger = get_logger("dashboard")
    return config, db, logger


config, db, logger = init_dashboard()


def main():
    """Main dashboard application"""
    
    # Title
    st.title("🎬 ShortsFactory Dashboard")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Overview", "Job Queue", "Review Queue", "Published", "Failed Jobs", "Logs", "Settings"]
    )
    
    # Route to appropriate page
    if page == "Overview":
        show_overview()
    elif page == "Job Queue":
        show_job_queue()
    elif page == "Review Queue":
        show_review_queue()
    elif page == "Published":
        show_published()
    elif page == "Failed Jobs":
        show_failed_jobs()
    elif page == "Logs":
        show_logs()
    elif page == "Settings":
        show_settings()


def show_overview():
    """Show overview page with statistics"""
    st.header("System Overview")
    
    # Get statistics
    stats = db.get_stats()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", stats['total_jobs'])
    
    with col2:
        processing = sum([
            stats['by_state'].get(s, 0) 
            for s in ['NEW', 'CUTTING', 'FORMATTING', 'CAPTIONING', 'METADATA', 'RENDERING']
        ])
        st.metric("Processing", processing)
    
    with col3:
        st.metric("Ready for Review", stats['by_state'].get('READY_FOR_REVIEW', 0))
    
    with col4:
        st.metric("Published", stats['by_state'].get('PUBLISHED', 0))
    
    # State breakdown
    st.subheader("Jobs by State")
    
    cols = st.columns(3)
    for idx, (state, count) in enumerate(stats['by_state'].items()):
        with cols[idx % 3]:
            if count > 0:
                st.info(f"**{state}**: {count}")
    
    # Recent activity
    st.subheader("Recent Activity")
    logs = db.get_activity_logs(limit=20)
    
    if logs:
        for log in logs:
            timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            job_info = f"Job {log.job_id}" if log.job_id else "System"
            st.text(f"{timestamp} | {job_info} | {log.action}")
    else:
        st.info("No recent activity")


def show_job_queue():
    """Show current job queue"""
    st.header("Job Queue")
    
    # Filter options
    state_filter = st.selectbox(
        "Filter by State",
        ["All"] + [s.value for s in JobState]
    )
    
    # Get jobs
    if state_filter == "All":
        jobs = db.get_all_jobs(limit=100)
    else:
        jobs = db.get_jobs_by_state(JobState(state_filter), limit=100)
    
    if not jobs:
        st.info("No jobs found")
        return
    
    # Display jobs
    for job in jobs:
        with st.expander(f"Job {job.id} - {job.state} - {job.created_at.strftime('%Y-%m-%d %H:%M')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**State:** {job.state}")
                st.write(f"**Source Type:** {job.source_type}")
                st.write(f"**Created:** {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Updated:** {job.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Progress:** {job.progress:.1f}%")
            
            with col2:
                if job.title:
                    st.write(f"**Title:** {job.title}")
                if job.duration_seconds:
                    st.write(f"**Duration:** {job.duration_seconds:.1f}s")
                if job.error_message:
                    st.error(f"**Error:** {job.error_message}")
                if job.source_idea:
                    st.write(f"**Idea:** {job.source_idea[:100]}")


def show_review_queue():
    """Show review queue with approval controls"""
    st.header("Review Queue")
    
    # Get jobs ready for review
    jobs = db.get_jobs_by_state(JobState.READY_FOR_REVIEW)
    
    if not jobs:
        st.success("No jobs awaiting review")
        return
    
    st.info(f"{len(jobs)} job(s) ready for review")
    
    # Review each job
    for job in jobs:
        st.markdown("---")
        st.subheader(f"Job {job.id}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Video preview
            if job.final_path and os.path.exists(job.final_path):
                st.video(job.final_path)
            else:
                st.warning("Video file not found")
            
            # Metadata
            st.write(f"**Title:** {job.title or 'N/A'}")
            st.write(f"**Description:**")
            st.text(job.description or 'N/A')
            st.write(f"**Hashtags:** {job.hashtags or 'N/A'}")
            st.write(f"**Duration:** {job.duration_seconds:.1f}s" if job.duration_seconds else "N/A")
        
        with col2:
            st.write("**Review Actions**")
            
            # Review notes
            review_notes = st.text_area(
                "Notes (optional)",
                key=f"notes_{job.id}",
                height=100
            )
            
            # Action buttons
            col_approve, col_reject = st.columns(2)
            
            with col_approve:
                if st.button("✅ Approve", key=f"approve_{job.id}", type="primary"):
                    db.update_job_state(
                        job.id,
                        JobState.APPROVED,
                        reviewed_at=datetime.utcnow(),
                        reviewed_by="Dashboard User",
                        review_notes=review_notes
                    )
                    st.success(f"Job {job.id} approved!")
                    st.rerun()
            
            with col_reject:
                if st.button("❌ Reject", key=f"reject_{job.id}"):
                    db.update_job_state(
                        job.id,
                        JobState.REJECTED,
                        reviewed_at=datetime.utcnow(),
                        reviewed_by="Dashboard User",
                        review_notes=review_notes
                    )
                    st.error(f"Job {job.id} rejected")
                    st.rerun()
            
            # Reprocess button
            if st.button("🔄 Send to Reprocess", key=f"reprocess_{job.id}"):
                db.update_job_state(
                    job.id,
                    JobState.NEW,
                    review_notes=review_notes
                )
                st.info(f"Job {job.id} sent back for reprocessing")
                st.rerun()


def show_published():
    """Show published videos"""
    st.header("Published Videos")
    
    jobs = db.get_jobs_by_state(JobState.PUBLISHED)
    
    if not jobs:
        st.info("No published videos yet")
        return
    
    st.success(f"{len(jobs)} video(s) published")
    
    for job in jobs:
        with st.expander(f"Job {job.id} - Published {job.uploaded_at.strftime('%Y-%m-%d %H:%M') if job.uploaded_at else 'N/A'}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Title:** {job.title}")
                st.write(f"**Published:** {job.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if job.uploaded_at else 'N/A'}")
                st.write(f"**Video ID:** {job.video_id or 'N/A'}")
                if job.video_url:
                    st.write(f"**URL:** [{job.video_url}]({job.video_url})")
            
            with col2:
                st.write(f"**Duration:** {job.duration_seconds:.1f}s" if job.duration_seconds else 'N/A')
                st.write(f"**Hashtags:** {job.hashtags or 'N/A'}")


def show_failed_jobs():
    """Show failed jobs with error details"""
    st.header("Failed Jobs")
    
    jobs = db.get_jobs_by_state(JobState.FAILED)
    
    if not jobs:
        st.success("No failed jobs")
        return
    
    st.error(f"{len(jobs)} failed job(s)")
    
    for job in jobs:
        with st.expander(f"Job {job.id} - Failed"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Created:** {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Source Type:** {job.source_type}")
                st.write(f"**Retry Count:** {job.retry_count}")
                st.error(f"**Error:** {job.error_message or 'Unknown error'}")
            
            with col2:
                if st.button(f"🔄 Retry Job {job.id}", key=f"retry_{job.id}"):
                    db.update_job_state(
                        job.id,
                        JobState.NEW,
                        error_message=None,
                        retry_count=0
                    )
                    st.success("Job queued for retry")
                    st.rerun()


def show_logs():
    """Show activity logs"""
    st.header("Activity Logs")
    
    # Limit selector
    limit = st.slider("Number of logs to show", 10, 200, 50)
    
    # Get logs
    logs = db.get_activity_logs(limit=limit)
    
    if not logs:
        st.info("No logs found")
        return
    
    # Display logs
    for log in logs:
        timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        job_info = f"Job {log.job_id}" if log.job_id else "System"
        status = "✅" if log.success else "❌"
        
        with st.expander(f"{status} {timestamp} | {job_info} | {log.action}"):
            if log.details:
                st.text(log.details)


def show_settings():
    """Show and edit settings"""
    st.header("Settings")
    
    st.info("Configuration is loaded from config/settings.yaml")
    
    # Display current config
    st.subheader("Current Configuration")
    
    with st.expander("Video Processing"):
        st.write(f"Target Resolution: {config.video.target_width}x{config.video.target_height}")
        st.write(f"FPS: {config.video.fps}")
        st.write(f"Duration Range: {config.video.min_duration}-{config.video.max_duration} seconds")
    
    with st.expander("Upload Settings"):
        st.write(f"Enabled: {'✅ Yes' if config.upload.enabled else '❌ No'}")
        st.write(f"Max per Day: {config.upload.max_per_day}")
        st.write(f"Min Delay: {config.upload.min_delay_minutes} minutes")
        st.write(f"Max Delay: {config.upload.max_delay_minutes} minutes")
        st.write(f"Privacy Status: {config.upload.privacy_status}")
    
    with st.expander("Worker Settings"):
        st.write(f"Max Retries: {config.worker.max_retries}")
        st.write(f"Retry Delay: {config.worker.retry_delay} seconds")
        st.write(f"Timeout: {config.worker.timeout} seconds")
    
    st.markdown("---")
    st.info("To modify settings, edit the config/settings.yaml file and restart the dashboard.")


if __name__ == "__main__":
    main()
