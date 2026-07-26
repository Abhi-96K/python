import requests
from bs4 import BeautifulSoup

def get_contact_details(insta_id):
    url = f"https://www.instagram.com/{insta_id}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract email address from profile page
    email = soup.find('meta', {'property': 'email'})
    if email:
        email = email['content']
    else:
        email = "Not available"
    
    # Extract other contact details
    username = soup.find('meta', {'name': 'twitter:title'})
    if username:
        username = username['content'].split(' - ')[0]
    else:
        username = "Not available"
    
    full_name = soup.find('meta', {'property': 'og:title'})
    if full_name:
        full_name = full_name['content']
    else:
        full_name = "Not available"
    
    bio = soup.find('meta', {'property': 'og:description'})
    if bio:
        bio = bio['content']
    else:
        bio = "Not available"
    
    profile_picture_url = soup.find('meta', {'property': 'og:image'})
    if profile_picture_url:
        profile_picture_url = profile_picture_url['content']
    else:
        profile_picture_url = "Not available"
    
    contact_details = {
        "username": username,
        "full_name": full_name,
        "bio": bio,
        "profile_picture_url": profile_picture_url,
        "email": email
    }
    
    return contact_details

# Example usage
insta_id = "ialokyaddav"
contact_details = get_contact_details(insta_id)
print(contact_details)