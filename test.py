from linkedin_api import Linkedin

# Authenticate using any Linkedin user account credentials
api = Linkedin('Izayahhudnut@gmail.com', 'WPs#O"^fLfs!cB0m0S_2a')

# GET a profile
profile = api.get_profile('jashwanthyenugu')


print(profile)