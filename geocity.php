<?php
/**
 * Plugin Name: GeoT City Replacer
 * Description: Replaces [geot_city] anywhere on the page with the user's city based on IP.
 * Version: 1.1
 * Author: Sajid Khan
 */

if (!defined('ABSPATH')) exit; // Exit if accessed directly

// Get user city using ip-api
function geot_get_user_city() {
    $ip = $_SERVER['REMOTE_ADDR'];

    // Fallback for localhost testing
    if ($ip === '127.0.0.1' || $ip === '::1') {
        return 'Your City';
    }

    $response = @file_get_contents("http://ip-api.com/json/{$ip}?fields=city");

    if ($response) {
        $data = json_decode($response);
        if (!empty($data->city)) {
            return esc_html($data->city);
        }
    }

    return 'Your City'; // Fallback
}

// Replace token in full page output
function geot_replace_output_buffer($buffer) {
    if (strpos($buffer, '[geot_city]') !== false) {
        $city = geot_get_user_city();
        $buffer = str_replace('[geot_city]', $city, $buffer);
    }
    return $buffer;
}

// Start output buffering
function geot_start_buffer() {
    ob_start('geot_replace_output_buffer');
}

add_action('template_redirect', 'geot_start_buffer');
