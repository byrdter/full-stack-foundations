"""
Health check endpoints for monitoring application and database status.

This module demonstrates:
- Complete logging lifecycle (started, completed, failed)
- Duration tracking for performance monitoring
- Structured logging with context
- Health check best practices

Pattern: All health check endpoints follow the logging lifecycle pattern
"""

import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.shared.schemas import EchoRequest, EchoResponse

logger = get_logger(__name__)

# Health check endpoints are typically at root (no prefix)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Basic health check endpoint.

    Demonstrates complete logging lifecycle:
    - health.check_started (with timestamp)
    - health.check_completed (with duration)

    Returns:
        dict: Health status of the API service.

    Example response:
        {"status": "healthy", "service": "api"}
    """
    # Track duration
    start_time = time.time()

    # Log START
    logger.info("health.check_started", endpoint="/health")

    # Perform health check (trivial for basic endpoint)
    response = {"status": "healthy", "service": "api"}

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log SUCCESS
    logger.info(
        "health.check_completed",
        endpoint="/health",
        status="healthy",
        duration_ms=round(duration_ms, 2),
    )

    return response


@router.get("/health/db")
async def database_health_check(
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Database connectivity health check.

    Demonstrates complete logging lifecycle:
    - health.db_check_started
    - health.db_check_completed (with duration)
    - health.db_check_failed (with error details)

    Args:
        db: Database session dependency.

    Returns:
        dict: Health status of the database connection.

    Raises:
        HTTPException: 503 if database is not accessible.

    Example response:
        {"status": "healthy", "service": "database", "provider": "postgresql"}
    """
    # Track duration
    start_time = time.time()

    # Log START
    logger.info("health.db_check_started", endpoint="/health/db")

    try:
        # Execute a simple query to verify database connectivity
        await db.execute(text("SELECT 1"))

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log SUCCESS
        logger.info(
            "health.db_check_completed",
            endpoint="/health/db",
            status="healthy",
            provider="postgresql",
            duration_ms=round(duration_ms, 2),
        )

        return {
            "status": "healthy",
            "service": "database",
            "provider": "postgresql",
        }

    except Exception as exc:
        # Calculate duration (even for failures)
        duration_ms = (time.time() - start_time) * 1000

        # Log FAILURE
        logger.error(
            "health.db_check_failed",
            endpoint="/health/db",
            error=str(exc),
            error_type=type(exc).__name__,
            duration_ms=round(duration_ms, 2),
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not accessible",
        ) from exc


@router.get("/health/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Readiness check for all application dependencies.

    Verifies that the application is ready to serve requests by checking
    all critical dependencies (database, configuration, etc.).

    Demonstrates complete logging lifecycle:
    - health.readiness_check_started
    - health.readiness_check_completed (with duration)
    - health.readiness_check_failed (with error details)

    Args:
        db: Database session dependency.

    Returns:
        dict: Readiness status with environment and dependency information.

    Raises:
        HTTPException: 503 if any dependency is not ready.

    Example response:
        {
            "status": "ready",
            "environment": "development",
            "database": "connected"
        }
    """
    # Track duration
    start_time = time.time()

    settings = get_settings()

    # Log START
    logger.info(
        "health.readiness_check_started",
        endpoint="/health/ready",
        environment=settings.environment,
    )

    try:
        # Verify database connectivity
        await db.execute(text("SELECT 1"))

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log SUCCESS
        logger.info(
            "health.readiness_check_completed",
            endpoint="/health/ready",
            status="ready",
            environment=settings.environment,
            database="connected",
            duration_ms=round(duration_ms, 2),
        )

        return {
            "status": "ready",
            "environment": settings.environment,
            "database": "connected",
        }

    except Exception as exc:
        # Calculate duration (even for failures)
        duration_ms = (time.time() - start_time) * 1000

        # Log FAILURE
        logger.error(
            "health.readiness_check_failed",
            endpoint="/health/ready",
            environment=settings.environment,
            error=str(exc),
            error_type=type(exc).__name__,
            duration_ms=round(duration_ms, 2),
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application is not ready",
        ) from exc


@router.post("/health/echo", response_model=EchoResponse)
async def echo(payload: EchoRequest) -> EchoResponse:
    """
    Echo back the provided message for connectivity testing.

    Demonstrates complete logging lifecycle:
    - health.echo_started (with message length)
    - health.echo_completed (with duration)

    Args:
        payload: Echo request with message to echo back

    Returns:
        EchoResponse: Same message echoed back

    Example request:
        {"message": "Hello, World!"}

    Example response:
        {"message": "Hello, World!"}
    """
    # Track duration
    start_time = time.time()

    # Log START
    logger.info(
        "health.echo_started",
        endpoint="/health/echo",
        message_length=len(payload.message),
    )

    # Echo the message
    response = EchoResponse(message=payload.message)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log SUCCESS
    logger.info(
        "health.echo_completed",
        endpoint="/health/echo",
        message_length=len(payload.message),
        duration_ms=round(duration_ms, 2),
    )

    return response
