
def get_account_id(context):
    return context.invoked_function_arn.split(":")[4]

def get_region(context):
    return context.invoked_function_arn.split(":")[3]
