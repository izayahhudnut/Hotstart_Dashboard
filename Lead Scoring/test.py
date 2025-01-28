from linkedin_api import Linkedin

# Authenticate using any Linkedin user account credentials
api = Linkedin('admin@dor15.com', 'L0R9>m7C%Yj8s.JRfymr')

profile = api.get_profile('izayah-hudnut-873027198')

print(profile)