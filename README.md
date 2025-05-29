# Location-finder
Shows the location of visitor on website in paragraph 
The GeoT City Replacer WordPress plugin replaces the shortcode [geot_city] anywhere on a webpage with the user's city, determined based on their IP address. Here's a breakdown of what the plugin does:

IP-based City Detection:
The plugin uses the ip-api.com service to fetch the user's city by sending a request with their IP address (obtained from $_SERVER['REMOTE_ADDR']).
If the IP is 127.0.0.1 or ::1 (localhost), it returns a fallback value of "Your City" for testing purposes.
If the API request succeeds and returns a valid city, it uses that city; otherwise, it falls back to "Your City."
Shortcode Replacement:
The plugin searches for the [geot_city] shortcode in the page's content.
It replaces all instances of [geot_city] with the user's city (escaped for security using esc_html).
Output Buffering:
The plugin uses PHP's output buffering to capture the entire page output.
It processes the page content to replace [geot_city] with the user's city before the page is sent to the browser.
Output buffering is initiated using the template_redirect action hook, ensuring the replacement happens early in the page rendering process.
Security:
The plugin includes a security check (if (!defined('ABSPATH')) exit;) to prevent direct access to the plugin file.
It uses esc_html to sanitize the city name, preventing potential XSS vulnerabilities.
In summary, this plugin dynamically personalizes content by replacing the [geot_city] shortcode with the user's city based on their IP address, using an external API for geolocation. If the API fails or the user is on localhost, it defaults to "Your City."