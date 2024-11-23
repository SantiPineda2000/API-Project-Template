from datetime import timedelta

##=============================================================================================
## AUTH UTILITY FUNCTIONS
##=============================================================================================

def get_data() -> dict[int, timedelta]:
    return {
        "subject": 123,
        "expires_delta": timedelta(minutes=15)
    }