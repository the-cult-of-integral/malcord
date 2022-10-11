class InvalidChannelTypeException(Exception):
    """    
    In `malcord.ctxcommands`, there are three channel type constants:
        `TEXT_CHANNEL = 1`
        `VOICE_CHANNEL = 2`
        `RANDOM_CHANNEL = 3`
    
    These constants should be used during conditional statements to determine
    what type of channel to use.
    
    This exception should be raised when the channel type provided is invalid.
    """
    pass


class InvalidTokenException(Exception):
    """    
    In `malcord.token`, there is a validate_token method that checks if a token
    is valid.
    
    If not valid, this exception should be raised.
    """
    pass


class InvalidLoginActionException(Exception):
    """
    In `malcord.token`, there is a login method that allows you to log into
    an account that a token represents. This method takes an action parameter
    that determines what action to take after logging in.
    
    This exception should be raised when the action provided is invalid.
    """
    pass