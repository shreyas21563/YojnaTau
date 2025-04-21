import streamlit as st
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2
import base64
__version__ = "0.1"


async def write_authorization_url(client, redirect_uri):
    authorization_url = await client.get_authorization_url(
        redirect_uri,
        scope=["profile", "email"],
        extras_params={"access_type": "offline"},
    )
    return authorization_url


async def write_access_token(client, redirect_uri, code):
    token = await client.get_access_token(code, redirect_uri)
    return token


async def get_user_info(client, token):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email


async def revoke_token(client, token):
    return await client.revoke_token(token)

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return encoded
def login_button(authorization_url, app_name, app_desc):
    image_path = "img/google_icon.png"  # Update this path to your image
    image_base64 = get_image_base64(image_path)

    button_html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap');

    .center-container {{
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }}

    .center-container a {{
        text-decoration: none !important;
        color: #3c4043 !important; /* softer color */
    }}

    .google-btn {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: white;
        border: 1px solid #dadce0;
        border-radius: 4px;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: #3c4043 !important;
        padding: 10px 15px;
        transition: all 0.2s;
        outline: none;
        box-shadow: none;
    }}

    .google-btn:focus {{
        outline: none !important;
        box-shadow: none !important;
    }}

    .google-btn:hover {{
        box-shadow: 0 1px 2px rgba(0,0,0,0.1),
                    0 1px 3px rgba(0,0,0,0.2);
        color: #3c4043 !important;
    }}

    .google-icon {{
        height: 18px;
        margin-right: 10px;
    }}
    </style>

    <div class="center-container">
        <p>
            <a class="google-btn" href="{authorization_url}" target="_self">
                <img class="google-icon" src="data:image/png;base64,{image_base64}" alt="Google logo">
                Sign in with Google
            </a>
        </p>
    </div>
    """

    # Render the button
    st.markdown(button_html, unsafe_allow_html=True)










def logout_button(button_text):
    if st.button(button_text):
        asyncio.run(
            revoke_token(
                client=st.session_state.client,
                token=st.session_state.token["access_token"],
            )
        )
        st.session_state.user_email = None
        st.session_state.user_id = None
        st.session_state.token = None
        st.rerun()


def login(
    client_id,
    client_secret,
    redirect_uri,
    app_name="Continue with Google",
    app_desc="",
    logout_button_text="Logout",
):
    st.session_state.client = GoogleOAuth2(client_id, client_secret)
    authorization_url = asyncio.run(
        write_authorization_url(
            client=st.session_state.client, redirect_uri=redirect_uri
        )
    )
    app_desc
    if "token" not in st.session_state:
        st.session_state.token = None

    if st.session_state.token is None:
        try:
            code = st.query_params["code"]
        except:
            login_button(authorization_url, app_name, app_desc)
        else:
            try:
                token = asyncio.run(
                    write_access_token(
                        client=st.session_state.client,
                        redirect_uri=redirect_uri,
                        code=code,
                    )
                )
            except:
                login_button(authorization_url, app_name, app_desc)
            else:
                if token.is_expired():
                    login_button(authorization_url, app_name, app_desc)
                else:
                    st.session_state.token = token
                    st.session_state.user_id, st.session_state.user_email = asyncio.run(
                        get_user_info(
                            client=st.session_state.client, token=token["access_token"]
                        )
                    )
                    # logout_button(button_text=logout_button_text)
                    return (st.session_state.user_id, st.session_state.user_email)
    else:
        # logout_button(button_text=logout_button_text)
        return (st.session_state.user_id, st.session_state.user_email)