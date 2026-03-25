import os
from bs4 import BeautifulSoup
import pytest

# Define paths to the HTML templates
# Assuming tests/test_templates.py and templates/ are siblings under the project root
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'static')

LOGIN_HTML_PATH = os.path.join(TEMPLATES_DIR, 'login.html')
REGISTER_HTML_PATH = os.path.join(TEMPLATES_DIR, 'register.html')
DASHBOARD_HTML_PATH = os.path.join(TEMPLATES_DIR, 'dashboard.html')
COMMON_CSS_PATH = os.path.join(STATIC_DIR, 'style.css')

def read_file_content(filepath):
    """Helper function to read a file's content."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found at: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture(scope='module')
def common_head_elements():
    """Fixture to define common elements expected in the head section."""
    return {
        'charset': 'UTF-8',
        'viewport_content': 'width=device-width, initial-scale=1.0',
        'css_href': '/static/style.css'
    }

def validate_html_base(soup, expected_title, common_elements):
    """Helper to validate common HTML structure."""
    assert soup.html, "html tag missing"
    assert soup.html.get('lang') == 'en', "html lang attribute not set to 'en'"

    head = soup.head
    assert head, "head tag missing"
    assert head.find('meta', charset=common_elements['charset']), f"UTF-8 meta charset missing in head for {expected_title}"
    assert head.find('meta', attrs={'name': 'viewport', 'content': common_elements['viewport_content']}), \
        f"Viewport meta tag with correct content missing in head for {expected_title}"

    title = head.title
    assert title, f"title tag missing in head for {expected_title}"
    assert title.string == expected_title, f"Page title is incorrect for {expected_title}"

    css_link = head.find('link', rel='stylesheet', href=common_elements['css_href'])
    assert css_link, f"CSS stylesheet link to '{common_elements['css_href']}' is missing or incorrect in head for {expected_title}"

    body = soup.body
    assert body, "body tag missing"
    return body # Return body for further specific tests

# --- Test Login Page ---
def test_login_html_exists():
    """Ensure login.html file exists."""
    assert os.path.exists(LOGIN_HTML_PATH), f"The HTML file '{LOGIN_HTML_PATH}' does not exist."

def test_login_html_structure(common_head_elements):
    """Test login.html basic structure and form elements."""
    html_content = read_file_content(LOGIN_HTML_PATH)
    soup = BeautifulSoup(html_content, 'html.parser')

    body = validate_html_base(soup, "Login - SaaS App", common_head_elements)

    # Test heading
    h1 = body.find('h1')
    assert h1, "H1 heading missing in login.html"
    assert h1.string == "Login to Your Account", "Login page H1 heading text is incorrect"

    # Test form
    form = body.find('form', action='/login', method='post')
    assert form, "Login form with action='/login' and method='post' is missing"

    email_input = form.find('input', type='email', id='email', name='email')
    assert email_input, "Email input field missing in login form"
    assert 'required' in email_input.attrs, "Email input should be required"

    password_input = form.find('input', type='password', id='password', name='password')
    assert password_input, "Password input field missing in login form"
    assert 'required' in password_input.attrs, "Password input should be required"

    submit_button = form.find('button', type='submit')
    assert submit_button, "Submit button missing in login form"
    assert submit_button.string == "Login", "Login button text is incorrect"

    # Test link to register page
    register_link = body.find('p').find('a', href='/register')
    assert register_link, "Link to register page missing in login.html"
    assert "Register here" in register_link.string, "Register link text is incorrect"


# --- Test Register Page ---
def test_register_html_exists():
    """Ensure register.html file exists."""
    assert os.path.exists(REGISTER_HTML_PATH), f"The HTML file '{REGISTER_HTML_PATH}' does not exist."

def test_register_html_structure(common_head_elements):
    """Test register.html basic structure and form elements."""
    html_content = read_file_content(REGISTER_HTML_PATH)
    soup = BeautifulSoup(html_content, 'html.parser')

    body = validate_html_base(soup, "Register - SaaS App", common_head_elements)

    # Test heading
    h1 = body.find('h1')
    assert h1, "H1 heading missing in register.html"
    assert h1.string == "Create Your Account", "Register page H1 heading text is incorrect"

    # Test form
    form = body.find('form', action='/register', method='post')
    assert form, "Register form with action='/register' and method='post' is missing"

    username_input = form.find('input', type='text', id='username', name='username')
    assert username_input, "Username input field missing in register form"
    assert 'required' in username_input.attrs, "Username input should be required"

    email_input = form.find('input', type='email', id='email', name='email')
    assert email_input, "Email input field missing in register form"
    assert 'required' in email_input.attrs, "Email input should be required"

    password_input = form.find('input', type='password', id='password', name='password')
    assert password_input, "Password input field missing in register form"
    assert 'required' in password_input.attrs, "Password input should be required"

    confirm_password_input = form.find('input', type='password', id='confirm_password', name='confirm_password')
    assert confirm_password_input, "Confirm password input field missing in register form"
    assert 'required' in confirm_password_input.attrs, "Confirm password input should be required"

    submit_button = form.find('button', type='submit')
    assert submit_button, "Submit button missing in register form"
    assert submit_button.string == "Register", "Register button text is incorrect"

    # Test link to login page
    login_link = body.find('p').find('a', href='/login')
    assert login_link, "Link to login page missing in register.html"
    assert "Login here" in login_link.string, "Login link text is incorrect"


# --- Test Dashboard Page ---
def test_dashboard_html_exists():
    """Ensure dashboard.html file exists."""
    assert os.path.exists(DASHBOARD_HTML_PATH), f"The HTML file '{DASHBOARD_HTML_PATH}' does not exist."

def test_dashboard_html_structure(common_head_elements):
    """Test dashboard.html basic structure and key elements."""
    html_content = read_file_content(DASHBOARD_HTML_PATH)
    soup = BeautifulSoup(html_content, 'html.parser')

    body = validate_html_base(soup, "Dashboard - SaaS App", common_head_elements)

    # Test header elements
    header = body.find('header')
    assert header, "Header tag missing in dashboard.html"
    assert header.find('h1').string == "SaaS App Dashboard", "Dashboard H1 heading incorrect"
    
    nav = header.find('nav')
    assert nav, "Navigation bar missing in dashboard header"
    assert nav.find('span', id='user-name'), "User name placeholder missing in dashboard nav"
    assert nav.find('a', href='/profile'), "Profile link missing in dashboard nav"
    assert nav.find('a', href='/settings'), "Settings link missing in dashboard nav"
    assert nav.find('a', href='/logout'), "Logout link missing in dashboard nav"

    # Test main content sections
    main = body.find('main', class_='container')
    assert main, "Main content area with class 'container' missing in dashboard.html"

    # Subscription details
    subscription_section = main.find('section', id='subscription-details')
    assert subscription_section, "Subscription details section missing"
    assert subscription_section.find('h2').string == "Subscription Details", "Subscription details heading incorrect"
    assert subscription_section.find('span', id='plan-name'), "Plan name span missing"
    assert subscription_section.find('span', id='plan-status'), "Plan status span missing"
    assert subscription_section.find('span', id='next-billing'), "Next billing span missing"
    assert subscription_section.find('a', href='/billing', class_='button'), "Manage Billing link/button missing"


    # Usage statistics
    usage_section = main.find('section', id='usage-statistics')
    assert usage_section, "Usage statistics section missing"
    assert usage_section.find('h2').string == "Usage Statistics", "Usage statistics heading incorrect"
    assert usage_section.find('span', id='api-calls'), "API calls span missing"
    assert usage_section.find('span', id='api-limit'), "API limit span missing"
    assert usage_section.find('span', id='storage-used'), "Storage used span missing"
    assert usage_section.find('span', id='storage-limit'), "Storage limit span missing"
    assert usage_section.find('a', href='/usage-history', class_='button'), "View Usage History link/button missing"

    # Account management
    account_section = main.find('section', id='account-management')
    assert account_section, "Account management section missing"
    assert account_section.find('h2').string == "Account Management", "Account management heading incorrect"
    assert account_section.find('a', href='/profile/edit'), "Edit Profile link missing"
    assert account_section.find('a', href='/password/change'), "Change Password link missing"
    assert account_section.find('a', href='/integrations'), "Integrations link missing"
    assert account_section.find('a', href='/support'), "Contact Support link missing"

    # Test footer
    footer = body.find('footer')
    assert footer, "Footer tag missing in dashboard.html"
    # Test for the presence of the copyright text (with flexible year)
    footer_text = footer.get_text()
    assert "SaaS App" in footer_text and "All rights reserved" in footer_text, "Footer copyright text incorrect or missing"

# --- Test Common Static Files ---
def test_common_static_files_exist():
    """Ensure the common style.css file exists."""
    assert os.path.exists(COMMON_CSS_PATH), f"The CSS file '{COMMON_CSS_PATH}' does not exist."