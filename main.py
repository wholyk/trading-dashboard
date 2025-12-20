"""
Google Cloud Function entry point for automated trading bot.
This file is used when deploying to Google Cloud Functions.
"""

from trading_bot import main_trading_function


def trading_function(request):
    """
    Cloud Function entry point.
    
    Args:
        request (flask.Request): The request object.
    
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`.
    """
    return main_trading_function(request)
